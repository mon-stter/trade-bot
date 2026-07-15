#!/usr/bin/env python3
"""Trading-rule enforcement helper. All hard rules live here."""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "memory"
STATE_PATH = Path(os.environ.get("GUARD_STATE_PATH", MEMORY / "state.json"))
TRADES_PATH = Path(os.environ.get("GUARD_TRADES_PATH", MEMORY / "trades.jsonl"))

# Rule constants (see spec section 5)
MAX_POSITIONS = 6
MAX_WEEKLY_TRADES = 3
MAX_POSITION_PCT = 0.20
INITIAL_STOP_PCT = 0.07
MAX_DRAWDOWN = -0.10
MAX_DAILY_LOSS = -0.05
PDT_LIMIT = 3


class GateError(Exception):
    """Raised when a rule blocks an action."""


class AlpacaClient:
    def __init__(self):
        self.key = os.environ["ALPACA_API_KEY"]
        self.secret = os.environ["ALPACA_SECRET_KEY"]
        self.api = os.environ.get("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets/v2")
        self.data = os.environ.get("ALPACA_DATA_ENDPOINT", "https://data.alpaca.markets/v2")

    def _req(self, method, url, body=None):
        headers = {
            "APCA-API-KEY-ID": self.key,
            "APCA-API-SECRET-KEY": self.secret,
            "Content-Type": "application/json",
        }
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())

    def account(self):
        return self._req("GET", f"{self.api}/account")

    def positions(self):
        return self._req("GET", f"{self.api}/positions")

    def orders(self, status="open"):
        return self._req("GET", f"{self.api}/orders?status={status}")

    def submit_order(self, body):
        return self._req("POST", f"{self.api}/orders", body)

    def calendar(self, start, end):
        return self._req("GET", f"{self.api}/calendar?start={start}&end={end}")


DEFAULT_STATE = {
    "halted": False, "halt_reason": "", "high_water_mark": 0.0,
    "week_start_equity": 0.0, "last_equity": 0.0,
}


def load_state(path=STATE_PATH):
    path = Path(path)
    if not path.exists():
        return dict(DEFAULT_STATE)
    return {**DEFAULT_STATE, **json.loads(path.read_text())}


def save_state(state, path=STATE_PATH):
    Path(path).write_text(json.dumps(state, indent=2) + "\n")


def set_halt(state, reason):
    state = dict(state)
    state["halted"] = True
    state["halt_reason"] = reason
    return state


def clear_halt(state):
    state = dict(state)
    state["halted"] = False
    state["halt_reason"] = ""
    return state


def read_jsonl(path=TRADES_PATH):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def week_start(ref):
    return ref - timedelta(days=ref.weekday())  # Monday


def weekly_trade_count(records, ref):
    start = week_start(ref)
    n = 0
    for r in records:
        if r.get("side") != "buy":
            continue
        d = date.fromisoformat(r["date"])
        if start <= d <= ref:
            n += 1
    return n


def is_plain_stock(symbol):
    return symbol.isalpha() and 1 <= len(symbol) <= 5


def validate_buy(order, account, positions, weekly_count, halted):
    reasons = []
    symbol = order["symbol"]
    qty = float(order["qty"])
    price = float(order["price"])
    cost = qty * price
    equity = float(account["equity"])
    cash = float(account["cash"])
    daytrades = int(account.get("daytrade_count", 0))
    held = {p["symbol"] for p in positions}

    if halted:
        reasons.append("kill-switch active")
    if not is_plain_stock(symbol):
        reasons.append(f"{symbol} is not a plain stock")
    if symbol not in held and len(positions) + 1 > MAX_POSITIONS:
        reasons.append(f"would exceed {MAX_POSITIONS} open positions")
    if weekly_count + 1 > MAX_WEEKLY_TRADES:
        reasons.append(f"would exceed {MAX_WEEKLY_TRADES} trades this week")
    if cost > MAX_POSITION_PCT * equity:
        reasons.append(f"cost {cost:.2f} exceeds 20% of equity ({MAX_POSITION_PCT*equity:.2f})")
    if cost > cash:
        reasons.append(f"cost {cost:.2f} exceeds available cash {cash:.2f}")
    if daytrades >= PDT_LIMIT:
        reasons.append(f"PDT: daytrade_count {daytrades} >= {PDT_LIMIT}")

    return (len(reasons) == 0, reasons)


def evaluate_risk(equity, state):
    state = dict(state)
    hwm = max(float(state.get("high_water_mark") or 0.0), equity)
    state["high_water_mark"] = hwm
    drawdown = (equity - hwm) / hwm if hwm else 0.0
    last = float(state.get("last_equity") or 0.0)
    daily = (equity - last) / last if last else 0.0

    if drawdown <= MAX_DRAWDOWN:
        return state, True, f"drawdown {drawdown:.1%} <= {MAX_DRAWDOWN:.0%}"
    if last and daily <= MAX_DAILY_LOSS:
        return state, True, f"daily P&L {daily:.1%} <= {MAX_DAILY_LOSS:.0%}"
    return state, False, ""


PROTECTIVE_TYPES = {"stop", "stop_limit", "trailing_stop"}


def find_naked_positions(positions, orders):
    protected = {
        o["symbol"] for o in orders
        if o.get("side") == "sell" and o.get("type") in PROTECTIVE_TYPES
    }
    return [p["symbol"] for p in positions if p["symbol"] not in protected]


def is_trading_day(client, ref):
    iso = ref.isoformat()
    cal = client.calendar(iso, iso)
    return any(c.get("date") == iso for c in cal)


def place_buy(client, order, state_path=STATE_PATH, trades_path=TRADES_PATH, ref=None):
    ref = ref or date.today()
    account = client.account()
    positions = client.positions()
    records = read_jsonl(trades_path)
    state = load_state(state_path)
    wc = weekly_trade_count(records, ref)

    ok, reasons = validate_buy(order, account, positions, wc, state["halted"])
    if not ok:
        raise GateError("; ".join(reasons))

    buy_body = {
        "symbol": order["symbol"], "qty": str(order["qty"]),
        "side": "buy", "type": "market", "time_in_force": "day",
    }
    fill = client.submit_order(buy_body)
    fill_price = float(fill.get("filled_avg_price") or order["price"])

    stop_price = round(fill_price * (1 - INITIAL_STOP_PCT), 2)
    stop_body = {
        "symbol": order["symbol"], "qty": str(order["qty"]),
        "side": "sell", "type": "stop", "stop_price": f"{stop_price:.2f}",
        "time_in_force": "gtc",
    }
    client.submit_order(stop_body)

    append_jsonl(trades_path, {
        "date": ref.isoformat(), "symbol": order["symbol"], "side": "buy",
        "qty": float(order["qty"]), "price": fill_price, "stop": stop_price,
        "sector": order.get("sector", ""), "thesis": order.get("thesis", ""),
        "target": order.get("target", ""), "rr": order.get("rr", ""),
    })
    return {"fill_price": fill_price, "stop_price": stop_price}


def wait_for_fill(client, order_id, tries=15, delay=1.0):
    """Safety-net poller: re-check an order until filled. Paper market orders
    usually fill immediately, so this rarely loops."""
    for _ in range(tries):
        for o in client.orders(status="all"):
            if o.get("id") == order_id and o.get("status") == "filled":
                return o
        time.sleep(delay)
    raise GateError(f"order {order_id} did not fill in time")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="guard.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("resume")
    h = sub.add_parser("halt"); h.add_argument("reason", nargs="?", default="manual")
    b = sub.add_parser("buy"); b.add_argument("json")
    r = sub.add_parser("reconcile"); r.add_argument("--fix", action="store_true")
    sub.add_parser("weekly-trades")
    sub.add_parser("check-risk")
    sub.add_parser("is-trading-day")
    args = parser.parse_args(argv)

    if args.cmd == "status":
        s = load_state()
        print(f"HALTED: {s['halt_reason']}" if s["halted"] else "not halted")
        return 0
    if args.cmd == "halt":
        save_state(set_halt(load_state(), args.reason)); print(f"halted: {args.reason}"); return 0
    if args.cmd == "resume":
        save_state(clear_halt(load_state())); print("resumed"); return 0
    if args.cmd == "weekly-trades":
        print(weekly_trade_count(read_jsonl(), date.today())); return 0

    client = AlpacaClient()
    if args.cmd == "is-trading-day":
        ok = is_trading_day(client, date.today())
        print("open" if ok else "closed"); return 0 if ok else 1
    if args.cmd == "check-risk":
        equity = float(client.account()["equity"])
        state, halt, reason = evaluate_risk(equity, load_state())
        if halt:
            state = set_halt(state, reason); print(f"HALT: {reason}")
        else:
            print("risk ok")
        save_state(state); return 0
    if args.cmd == "reconcile":
        positions = client.positions()
        naked = find_naked_positions(positions, client.orders())
        if not naked:
            print("all positions protected"); return 0
        print("naked: " + ", ".join(naked))
        if args.fix:
            for sym in naked:
                pos = next(p for p in positions if p["symbol"] == sym)
                price = float(pos["current_price"])
                stop = round(price * (1 - INITIAL_STOP_PCT), 2)
                client.submit_order({"symbol": sym, "qty": pos["qty"], "side": "sell",
                                     "type": "stop", "stop_price": f"{stop:.2f}",
                                     "time_in_force": "gtc"})
                print(f"placed stop for {sym} @ {stop:.2f}")
        return 0
    if args.cmd == "buy":
        try:
            result = place_buy(client, json.loads(args.json), ref=date.today())
            print(f"BOUGHT: fill {result['fill_price']} stop {result['stop_price']}")
            return 0
        except GateError as e:
            print(f"BLOCKED: {e}", file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
