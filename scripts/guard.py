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
PDT_EQUITY_MIN = 25000          # PDT rule only binds under $25k equity
MAX_SECTOR_LOSSES = 2           # sit out a sector after 2 straight losses
FILL_TRIES = 15
FILL_DELAY = 1.0
TRAIL_TIERS = ((0.20, 5.0), (0.15, 7.0))  # (min unrealized gain, trail %)


class GateError(Exception):
    """Raised when a rule blocks an action."""


def load_dotenv(path=ROOT / ".env"):
    """Load KEY=VALUE lines from a local .env into the environment, WITHOUT
    overriding anything already set. Cloud routines set real process env vars,
    so those always win; this only fills gaps for local runs."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())


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
            raw = r.read().decode()
            return json.loads(raw) if raw else None

    def account(self):
        return self._req("GET", f"{self.api}/account")

    def positions(self):
        return self._req("GET", f"{self.api}/positions")

    def orders(self, status="open"):
        return self._req("GET", f"{self.api}/orders?status={status}")

    def submit_order(self, body):
        return self._req("POST", f"{self.api}/orders", body)

    def cancel_order(self, order_id):
        return self._req("DELETE", f"{self.api}/orders/{order_id}")

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


def _qty_str(qty):
    return f"{float(qty):g}"


def _last_buy(records, symbol):
    for r in reversed(records):
        if r.get("symbol") == symbol and r.get("side") == "buy":
            return r
    return None


def sector_streak(records, sector):
    """Consecutive losing sells in a sector, most recent first."""
    n = 0
    for r in reversed(records):
        if r.get("side") != "sell" or r.get("sector") != sector:
            continue
        pnl = r.get("pnl")
        if pnl in (None, ""):
            continue
        if float(pnl) < 0:
            n += 1
        else:
            break
    return n


def notify(msg, log_path=None):
    """Discord webhook if configured, else committed fallback log. Never raises."""
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if url:
        try:
            req = urllib.request.Request(
                url, data=json.dumps({"content": msg}).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req)
            return "discord"
        except Exception:
            pass
    path = Path(log_path or os.environ.get("GUARD_NOTIFY_PATH", MEMORY / "notifications.log"))
    with open(path, "a") as f:
        f.write(f"\n{msg}\n")
    return "fallback"


def validate_buy(order, account, positions, weekly_count, halted, sector_streak=0):
    reasons = []
    symbol = order["symbol"]
    qty = float(order["qty"])
    price = float(order["price"])
    cost = qty * price
    equity = float(account["equity"])
    cash = float(account["cash"])
    daytrades = int(account.get("daytrade_count") or 0)
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
    if equity < PDT_EQUITY_MIN and daytrades >= PDT_LIMIT:
        reasons.append(f"PDT: daytrade_count {daytrades} >= {PDT_LIMIT}")
    if sector_streak >= MAX_SECTOR_LOSSES:
        reasons.append(f"sector '{order.get('sector', '')}' has "
                       f"{sector_streak} consecutive losses — sit out")

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


def unprotected_qty(position, orders):
    """Shares of a position not covered by protective sell orders."""
    protected = sum(
        float(o.get("qty") or 0) for o in orders
        if o.get("symbol") == position["symbol"]
        and o.get("side") == "sell" and o.get("type") in PROTECTIVE_TYPES)
    return max(0.0, float(position["qty"]) - protected)


def find_naked_positions(positions, orders):
    return [p["symbol"] for p in positions if unprotected_qty(p, orders) > 0]


def fix_naked(client):
    """Place a -7% stop for every uncovered share. Returns [(symbol, qty), ...]."""
    positions = client.positions()
    orders = client.orders()
    placed = []
    for p in positions:
        qty = unprotected_qty(p, orders)
        if qty <= 0:
            continue
        stop = round(float(p["current_price"]) * (1 - INITIAL_STOP_PCT), 2)
        client.submit_order({"symbol": p["symbol"], "qty": _qty_str(qty),
                             "side": "sell", "type": "stop",
                             "stop_price": f"{stop:.2f}", "time_in_force": "gtc"})
        placed.append((p["symbol"], qty))
    return placed


def is_trading_day(client, ref):
    iso = ref.isoformat()
    cal = client.calendar(iso, iso)
    return any(c.get("date") == iso for c in cal)


def _resolve_fill(client, resp, symbol):
    """Return the filled order; on timeout cancel it and raise, so a stop is
    never placed for shares that were never bought."""
    if resp.get("status") == "filled" and resp.get("filled_avg_price"):
        return resp
    try:
        return wait_for_fill(client, resp["id"], tries=FILL_TRIES, delay=FILL_DELAY)
    except GateError:
        client.cancel_order(resp["id"])
        for o in client.orders(status="all"):  # may have filled in the race window
            if o.get("id") == resp["id"] and o.get("status") == "filled":
                return o
        raise GateError(f"{symbol} order did not fill; canceled")


def place_buy(client, order, state_path=STATE_PATH, trades_path=TRADES_PATH, ref=None):
    ref = ref or date.today()
    account = client.account()
    positions = client.positions()
    records = read_jsonl(trades_path)
    state = load_state(state_path)
    wc = weekly_trade_count(records, ref)
    streak = sector_streak(records, order["sector"]) if order.get("sector") else 0

    ok, reasons = validate_buy(order, account, positions, wc, state["halted"],
                               sector_streak=streak)
    if not ok:
        raise GateError("; ".join(reasons))

    buy_body = {
        "symbol": order["symbol"], "qty": str(order["qty"]),
        "side": "buy", "type": "market", "time_in_force": "day",
    }
    resp = client.submit_order(buy_body)
    fill = _resolve_fill(client, resp, order["symbol"])
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
        "order_id": resp.get("id", ""),
    })
    return {"fill_price": fill_price, "stop_price": stop_price}


def place_sell(client, order, trades_path=TRADES_PATH, ref=None):
    """Only sanctioned sell path: cancel protective stops (frees the shares),
    market-sell, record realized P&L in trades.jsonl."""
    ref = ref or date.today()
    symbol = order["symbol"]
    pos = next((p for p in client.positions() if p["symbol"] == symbol), None)
    if pos is None:
        raise GateError(f"no open position in {symbol}")
    qty = float(order.get("qty") or pos["qty"])

    stops = [o for o in client.orders()
             if o.get("symbol") == symbol and o.get("side") == "sell"
             and o.get("type") in PROTECTIVE_TYPES]
    for o in stops:
        client.cancel_order(o["id"])

    resp = client.submit_order({"symbol": symbol, "qty": _qty_str(qty),
                                "side": "sell", "type": "market",
                                "time_in_force": "day"})
    try:
        fill = _resolve_fill(client, resp, symbol)
    except GateError:
        # sell didn't fill and stops are canceled — re-assert protection
        stop = round(float(pos["current_price"]) * (1 - INITIAL_STOP_PCT), 2)
        client.submit_order({"symbol": symbol, "qty": _qty_str(qty),
                             "side": "sell", "type": "stop",
                             "stop_price": f"{stop:.2f}", "time_in_force": "gtc"})
        raise

    fill_price = float(fill.get("filled_avg_price") or pos.get("current_price") or 0)
    records = read_jsonl(trades_path)
    buy = _last_buy(records, symbol)
    entry = float(pos.get("avg_entry_price") or (buy or {}).get("price") or 0)
    pnl = round((fill_price - entry) * qty, 2)
    append_jsonl(trades_path, {
        "date": ref.isoformat(), "symbol": symbol, "side": "sell",
        "qty": qty, "price": fill_price, "pnl": pnl,
        "sector": (buy or {}).get("sector", ""),
        "reason": order.get("reason", ""), "order_id": resp.get("id", ""),
    })
    return {"fill_price": fill_price, "pnl": pnl}


def sync_trades(client, trades_path=TRADES_PATH, ref=None):
    """Record broker-side sells (fired stops) that trades.jsonl doesn't know
    about yet. Idempotent via order_id."""
    ref = ref or date.today()
    records = read_jsonl(trades_path)
    known = {r.get("order_id") for r in records if r.get("order_id")}
    added = []
    for o in client.orders(status="closed"):
        if o.get("side") != "sell" or o.get("status") != "filled":
            continue
        if o.get("id") in known:
            continue
        symbol = o["symbol"]
        qty = float(o.get("filled_qty") or o.get("qty") or 0)
        price = float(o.get("filled_avg_price") or 0)
        buy = _last_buy(records, symbol)
        pnl = round((price - float(buy["price"])) * qty, 2) if buy else ""
        rec = {
            "date": (o.get("filled_at") or "")[:10] or ref.isoformat(),
            "symbol": symbol, "side": "sell", "qty": qty, "price": price,
            "pnl": pnl, "sector": (buy or {}).get("sector", ""),
            "reason": "sync: broker-side sell (stop fired)", "order_id": o["id"],
        }
        append_jsonl(trades_path, rec)
        added.append(rec)
    return added


def tighten_stops(client):
    """+15% -> 7% trail, +20% -> 5% trail. Cancel-then-place; on failure the
    old stop is re-asserted so a position is never left naked."""
    positions = client.positions()
    orders = client.orders()
    actions = []
    for p in positions:
        plpc = float(p.get("unrealized_plpc") or 0)
        trail = next((t for floor, t in TRAIL_TIERS if plpc >= floor), None)
        if trail is None:
            continue
        existing = [o for o in orders
                    if o.get("symbol") == p["symbol"] and o.get("side") == "sell"
                    and o.get("type") in PROTECTIVE_TYPES]
        if any(o.get("type") == "trailing_stop"
               and float(o.get("trail_percent") or 100) <= trail for o in existing):
            continue  # never loosen
        for o in existing:
            client.cancel_order(o["id"])
        try:
            client.submit_order({"symbol": p["symbol"], "qty": p["qty"],
                                 "side": "sell", "type": "trailing_stop",
                                 "trail_percent": f"{trail:g}",
                                 "time_in_force": "gtc"})
            actions.append((p["symbol"], trail))
        except Exception:
            for o in existing:
                body = {"symbol": o["symbol"], "qty": o.get("qty"), "side": "sell",
                        "type": o["type"], "time_in_force": "gtc"}
                if o.get("stop_price"):
                    body["stop_price"] = o["stop_price"]
                if o.get("trail_percent"):
                    body["trail_percent"] = o["trail_percent"]
                client.submit_order(body)
    return actions


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
    load_dotenv()
    parser = argparse.ArgumentParser(prog="guard.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("resume")
    h = sub.add_parser("halt"); h.add_argument("reason", nargs="?", default="manual")
    b = sub.add_parser("buy"); b.add_argument("json")
    s = sub.add_parser("sell"); s.add_argument("json")
    r = sub.add_parser("reconcile"); r.add_argument("--fix", action="store_true")
    ss = sub.add_parser("sector-streak"); ss.add_argument("sector")
    sub.add_parser("sync")
    sub.add_parser("tighten")
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
    if args.cmd == "sector-streak":
        print(sector_streak(read_jsonl(), args.sector)); return 0

    client = AlpacaClient()
    if args.cmd == "is-trading-day":
        ok = is_trading_day(client, date.today())
        print("open" if ok else "closed"); return 0 if ok else 1
    if args.cmd == "check-risk":
        equity = float(client.account()["equity"])
        state = load_state()
        was_halted = state["halted"]
        state, halt, reason = evaluate_risk(equity, state)
        if halt:
            state = set_halt(state, reason)
            print(f"HALT: {reason}")
            if not was_halted:
                notify(f"AUTO-HALT: {reason} (equity {equity:.2f}). "
                       "New buys blocked until /resume.")
        else:
            print("risk ok")
        save_state(state); return 0
    if args.cmd == "reconcile":
        naked = find_naked_positions(client.positions(), client.orders())
        if not naked:
            print("all positions protected"); return 0
        print("naked: " + ", ".join(naked))
        if args.fix:
            for sym, qty in fix_naked(client):
                print(f"placed stop for {sym} x{qty:g}")
        return 0
    if args.cmd == "sync":
        added = sync_trades(client)
        if not added:
            print("trade log in sync")
        for rec in added:
            print(f"recorded sell {rec['symbol']} x{rec['qty']:g} "
                  f"@ {rec['price']} pnl {rec['pnl']}")
        return 0
    if args.cmd == "tighten":
        actions = tighten_stops(client)
        if not actions:
            print("no stops tightened")
        for sym, trail in actions:
            print(f"{sym}: trailing {trail:g}%")
        return 0
    if args.cmd == "buy":
        try:
            result = place_buy(client, json.loads(args.json), ref=date.today())
            print(f"BOUGHT: fill {result['fill_price']} stop {result['stop_price']}")
            return 0
        except GateError as e:
            print(f"BLOCKED: {e}", file=sys.stderr); return 2
    if args.cmd == "sell":
        try:
            result = place_sell(client, json.loads(args.json), ref=date.today())
            print(f"SOLD: fill {result['fill_price']} pnl {result['pnl']}")
            return 0
        except GateError as e:
            print(f"BLOCKED: {e}", file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
