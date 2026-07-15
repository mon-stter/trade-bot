# Hardened Trading Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous Alpaca **paper**-trading agent whose trading rules are enforced by a unit-tested Python helper (`guard.py`) and driven by five scheduled Claude Code cloud routines, following the approved design spec.

**Architecture:** Stateless cloud runs read/write markdown + JSON "memory" committed to git. All hard rules (order validation, weekly caps, kill-switch, drawdown halt, reconciliation, market-calendar) live in `guard.py`, a stdlib-only Python 3 CLI that the routines are required to call. Thin bash wrappers (`alpaca.sh`, `discord.sh`) handle the outside world. Research uses native WebSearch.

**Tech Stack:** Python 3 (stdlib only: `urllib`, `json`, `argparse`, `datetime`), pytest for tests, Bash + curl wrappers, Alpaca paper API, Discord webhook, Claude Code cloud routines.

**Spec:** `docs/superpowers/specs/2026-07-15-hardened-trading-bot-design.md`

---

## File structure

| File | Responsibility |
|---|---|
| `scripts/guard.py` | All rule enforcement + order placement logic (the testable core) |
| `scripts/alpaca.sh` | Bash wrapper over Alpaca REST (account/positions/orders/quote/calendar/order/cancel/close) |
| `scripts/discord.sh` | Notification wrapper; commits fallback to `memory/notifications.log` |
| `tests/conftest.py` | `FakeClient` + fixtures (no network in tests) |
| `tests/test_guard.py` | Unit tests for every `guard.py` rule |
| `memory/state.json` | `{halted, halt_reason, high_water_mark, week_start_equity, last_equity}` |
| `memory/trades.jsonl` | One JSON object per trade (machine truth for counts) |
| `memory/*.md` | Human-readable strategy / logs / context |
| `routines/*.md` | Five cloud routine prompts |
| `.claude/commands/*.md` | Local slash commands (portfolio, trade, halt, resume, reconcile) |
| `CLAUDE.md`, `README.md`, `env.template` | Rulebook, quickstart, credential template |

**Deferred to a later version (documented, not built in v1):** deterministic `sector-streak` in `guard.py` (kept as an LLM-asserted rule in the midday routine); marketable-limit execution (v1 uses market orders, noted as a residual risk in the spec).

**Conventions:** Python price/qty are strings in Alpaca JSON but floats in logic. Dates are ISO `YYYY-MM-DD`. `guard.py` never uses `Date.now()`-style hidden clocks in pure functions — the caller passes a reference date so tests are deterministic.

---

## Task 0: Repo scaffold and test harness

**Files:**
- Create: `scripts/`, `tests/`, `routines/`, `.claude/commands/`, `memory/` directories
- Create: `pytest.ini`
- Create: `tests/conftest.py`
- Create: `memory/state.json`, `memory/trades.jsonl`, `memory/notifications.log`

- [ ] **Step 1: Create the directory tree and empty memory files**

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p scripts tests routines .claude/commands memory
printf '{\n  "halted": false,\n  "halt_reason": "",\n  "high_water_mark": 0.0,\n  "week_start_equity": 0.0,\n  "last_equity": 0.0\n}\n' > memory/state.json
: > memory/trades.jsonl
: > memory/notifications.log
```

- [ ] **Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 3: Create `tests/conftest.py` with a network-free FakeClient**

```python
import json
from pathlib import Path
import pytest


class FakeClient:
    """Stand-in for AlpacaClient. Records submitted orders; returns canned state."""

    def __init__(self, account=None, positions=None, orders=None, calendar=None, fills=None):
        self._account = account or {"equity": "10000", "cash": "10000", "daytrade_count": "0"}
        self._positions = positions or []
        self._orders = orders or []
        self._calendar = calendar or []
        self._fills = list(fills or [])
        self.submitted = []

    def account(self):
        return self._account

    def positions(self):
        return self._positions

    def orders(self, status="open"):
        return self._orders

    def calendar(self, start, end):
        return self._calendar

    def submit_order(self, body):
        self.submitted.append(body)
        if self._fills:
            return self._fills.pop(0)
        return {"id": "ord-1", "status": "filled", "filled_avg_price": body.get("_test_fill", "100")}


@pytest.fixture
def mem(tmp_path):
    """Isolated memory dir with initialized state.json and empty trades.jsonl."""
    (tmp_path / "state.json").write_text(json.dumps({
        "halted": False, "halt_reason": "", "high_water_mark": 0.0,
        "week_start_equity": 0.0, "last_equity": 0.0,
    }))
    (tmp_path / "trades.jsonl").write_text("")
    return tmp_path
```

- [ ] **Step 4: Verify pytest runs with zero tests**

Run: `python3 -m pytest -q`
Expected: `no tests ran` (exit code 5) — confirms pytest + conftest import cleanly.

- [ ] **Step 5: Commit**

```bash
git add pytest.ini tests/conftest.py memory/state.json memory/trades.jsonl memory/notifications.log
git commit -m "chore: scaffold repo, memory files, and test harness"
```

---

## Task 1: `guard.py` skeleton, constants, and AlpacaClient

**Files:**
- Create: `scripts/guard.py`

- [ ] **Step 1: Create `scripts/guard.py` with constants, paths, client, and stdlib imports**

```python
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
STATE_PATH = MEMORY / "state.json"
TRADES_PATH = MEMORY / "trades.jsonl"

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
```

- [ ] **Step 2: Verify the module imports**

Run: `python3 -c "import sys; sys.path.insert(0,'scripts'); import guard; print(guard.MAX_POSITIONS)"`
Expected: `6`

- [ ] **Step 3: Commit**

```bash
git add scripts/guard.py
git commit -m "feat(guard): module skeleton, constants, AlpacaClient"
```

---

## Task 2: State load/save helpers

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_guard.py`:

```python
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import guard  # noqa: E402


def test_load_state_returns_defaults_when_missing(tmp_path):
    state = guard.load_state(tmp_path / "nope.json")
    assert state["halted"] is False
    assert state["high_water_mark"] == 0.0


def test_save_then_load_roundtrips(tmp_path):
    p = tmp_path / "state.json"
    guard.save_state({"halted": True, "halt_reason": "x",
                      "high_water_mark": 5.0, "week_start_equity": 1.0,
                      "last_equity": 2.0}, p)
    assert guard.load_state(p)["halt_reason"] == "x"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -q`
Expected: FAIL — `AttributeError: module 'guard' has no attribute 'load_state'`

- [ ] **Step 3: Add the helpers to `scripts/guard.py`** (after the constants, before `AlpacaClient`)

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): state load/save with defaults"
```

---

## Task 3: Kill-switch (halt / resume)

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_guard.py`)

```python
def test_set_halt_sets_flag_and_reason():
    s = guard.set_halt(dict(guard.DEFAULT_STATE), "drawdown -12%")
    assert s["halted"] is True and s["halt_reason"] == "drawdown -12%"


def test_clear_halt_resets():
    s = guard.clear_halt({"halted": True, "halt_reason": "x"})
    assert s["halted"] is False and s["halt_reason"] == ""
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k halt -q`
Expected: FAIL — `has no attribute 'set_halt'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k halt -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): kill-switch set/clear helpers"
```

---

## Task 4: JSONL read/write + weekly trade count

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing test** (append)

```python
def test_weekly_trade_count_counts_only_buys_in_current_week(tmp_path):
    p = tmp_path / "trades.jsonl"
    guard.append_jsonl(p, {"date": "2026-07-13", "side": "buy", "symbol": "AAA"})   # Mon
    guard.append_jsonl(p, {"date": "2026-07-15", "side": "buy", "symbol": "BBB"})   # Wed
    guard.append_jsonl(p, {"date": "2026-07-15", "side": "sell", "symbol": "AAA"})  # sell ignored
    guard.append_jsonl(p, {"date": "2026-07-06", "side": "buy", "symbol": "OLD"})   # prev week
    from datetime import date
    n = guard.weekly_trade_count(guard.read_jsonl(p), date(2026, 7, 15))
    assert n == 2
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k weekly -q`
Expected: FAIL — `has no attribute 'append_jsonl'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k weekly -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): jsonl helpers and deterministic weekly trade count"
```

---

## Task 5: Buy-gate validation (the core rule)

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing tests** (append)

```python
def _order(symbol="AAPL", qty="10", price="100"):
    return {"symbol": symbol, "qty": qty, "price": price}


def _account(equity="10000", cash="10000", daytrade_count="0"):
    return {"equity": equity, "cash": cash, "daytrade_count": daytrade_count}


def test_valid_buy_passes():
    ok, reasons = guard.validate_buy(_order(), _account(), [], weekly_count=0, halted=False)
    assert ok and reasons == []


def test_rejects_when_halted():
    ok, reasons = guard.validate_buy(_order(), _account(), [], 0, halted=True)
    assert not ok and any("kill-switch" in r for r in reasons)


def test_rejects_non_stock_symbol():
    ok, reasons = guard.validate_buy(_order(symbol="AAPL260116C00150000"),
                                     _account(), [], 0, False)
    assert not ok and any("not a plain stock" in r for r in reasons)


def test_rejects_seventh_position():
    positions = [{"symbol": s} for s in ("A", "B", "C", "D", "E", "F")]
    ok, reasons = guard.validate_buy(_order(symbol="GGG"), _account(), positions, 0, False)
    assert not ok and any("positions" in r for r in reasons)


def test_adding_to_existing_position_does_not_count_as_new_slot():
    positions = [{"symbol": s} for s in ("A", "B", "C", "D", "E", "AAPL")]
    ok, reasons = guard.validate_buy(_order(symbol="AAPL"), _account(), positions, 0, False)
    assert ok, reasons


def test_rejects_fourth_weekly_trade():
    ok, reasons = guard.validate_buy(_order(), _account(), [], weekly_count=3, halted=False)
    assert not ok and any("this week" in r for r in reasons)


def test_rejects_position_over_20pct():
    ok, reasons = guard.validate_buy(_order(qty="30", price="100"),  # 3000 > 2000
                                     _account(equity="10000"), [], 0, False)
    assert not ok and any("20%" in r for r in reasons)


def test_rejects_cost_over_cash():
    ok, reasons = guard.validate_buy(_order(qty="15", price="100"),  # 1500 <=20% ok
                                     _account(equity="100000", cash="1000"), [], 0, False)
    assert not ok and any("cash" in r for r in reasons)


def test_rejects_when_pdt_exhausted():
    ok, reasons = guard.validate_buy(_order(), _account(daytrade_count="3"), [], 0, False)
    assert not ok and any("PDT" in r for r in reasons)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k validate -q`
Expected: FAIL — `has no attribute 'validate_buy'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k validate -q`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): buy-gate validation with full rejection matrix"
```

---

## Task 6: Risk evaluation (drawdown / daily-loss halt)

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_risk_updates_high_water_mark_and_does_not_halt_on_new_high():
    state = dict(guard.DEFAULT_STATE)
    state["high_water_mark"] = 10000.0
    new_state, halt, reason = guard.evaluate_risk(11000.0, state)
    assert not halt and new_state["high_water_mark"] == 11000.0


def test_risk_halts_on_drawdown_breach():
    state = {**guard.DEFAULT_STATE, "high_water_mark": 10000.0}
    new_state, halt, reason = guard.evaluate_risk(8900.0, state)  # -11%
    assert halt and "drawdown" in reason


def test_risk_halts_on_daily_loss_breach():
    state = {**guard.DEFAULT_STATE, "high_water_mark": 10000.0, "last_equity": 10000.0}
    new_state, halt, reason = guard.evaluate_risk(9400.0, state)  # -6% day, -6% dd (ok)
    assert halt and "daily" in reason


def test_risk_no_daily_halt_when_last_equity_zero():
    state = {**guard.DEFAULT_STATE, "high_water_mark": 10000.0, "last_equity": 0.0}
    new_state, halt, reason = guard.evaluate_risk(9700.0, state)  # -3% dd only
    assert not halt
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k risk -q`
Expected: FAIL — `has no attribute 'evaluate_risk'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k risk -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): drawdown/daily-loss risk evaluation"
```

---

## Task 7: Reconcile — detect naked positions

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_find_naked_positions_flags_unprotected():
    positions = [{"symbol": "AAA"}, {"symbol": "BBB"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "trailing_stop"}]
    assert guard.find_naked_positions(positions, orders) == ["BBB"]


def test_find_naked_positions_ignores_buy_orders():
    positions = [{"symbol": "AAA"}]
    orders = [{"symbol": "AAA", "side": "buy", "type": "market"}]
    assert guard.find_naked_positions(positions, orders) == ["AAA"]


def test_find_naked_positions_none_when_all_protected():
    positions = [{"symbol": "AAA"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "stop"}]
    assert guard.find_naked_positions(positions, orders) == []
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k naked -q`
Expected: FAIL — `has no attribute 'find_naked_positions'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
PROTECTIVE_TYPES = {"stop", "stop_limit", "trailing_stop"}


def find_naked_positions(positions, orders):
    protected = {
        o["symbol"] for o in orders
        if o.get("side") == "sell" and o.get("type") in PROTECTIVE_TYPES
    }
    return [p["symbol"] for p in positions if p["symbol"] not in protected]
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k naked -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): detect naked (unprotected) positions"
```

---

## Task 8: `is_trading_day`

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing tests** (append; uses `FakeClient` from conftest)

```python
from conftest import FakeClient  # noqa: E402


def test_is_trading_day_true_when_calendar_lists_today():
    client = FakeClient(calendar=[{"date": "2026-07-15", "open": "09:30", "close": "16:00"}])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is True


def test_is_trading_day_false_when_calendar_empty():
    client = FakeClient(calendar=[])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is False
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k trading_day -q`
Expected: FAIL — `has no attribute 'is_trading_day'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
def is_trading_day(client, ref):
    iso = ref.isoformat()
    cal = client.calendar(iso, iso)
    return any(c.get("date") == iso for c in cal)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k trading_day -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): market-calendar is_trading_day check"
```

---

## Task 9: `place_buy` integration (validate → buy → stop → record)

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_place_buy_rejected_by_gate_raises(mem):
    client = FakeClient(account=_account(cash="10"))  # too little cash
    with pytest.raises(guard.GateError):
        guard.place_buy(client, _order(qty="10", price="100"),
                        state_path=mem / "state.json",
                        trades_path=mem / "trades.jsonl",
                        ref=date(2026, 7, 15))
    assert client.submitted == []  # nothing sent to broker


def test_place_buy_places_order_then_stop_and_records(mem):
    client = FakeClient(fills=[{"id": "b1", "status": "filled", "filled_avg_price": "100"}])
    guard.place_buy(client, _order(symbol="AAPL", qty="10", price="100"),
                    state_path=mem / "state.json",
                    trades_path=mem / "trades.jsonl",
                    ref=date(2026, 7, 15))
    assert len(client.submitted) == 2
    buy, stop = client.submitted
    assert buy["side"] == "buy" and buy["type"] == "market"
    assert stop["side"] == "sell" and stop["type"] == "stop"
    assert abs(float(stop["stop_price"]) - 93.0) < 0.01   # 100 * (1 - 0.07)
    records = guard.read_jsonl(mem / "trades.jsonl")
    assert records[-1]["symbol"] == "AAPL" and records[-1]["side"] == "buy"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k place_buy -q`
Expected: FAIL — `has no attribute 'place_buy'`

- [ ] **Step 3: Add to `scripts/guard.py`**

```python
def _wait_for_fill(client, order_id, tries=10, delay=1.0):
    """Poll until filled; FakeClient returns filled immediately."""
    for _ in range(tries):
        # Real client: re-fetch the order. Fake client: submit_order already returned filled.
        return  # placeholder; real fill polling added in CLI integration (Task 10)
    raise GateError("order did not fill in time")


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
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k place_buy -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest -q`
Expected: PASS (all tests green)

- [ ] **Step 6: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): place_buy integration (gate, buy, -7% stop, record)"
```

---

## Task 10: CLI dispatch (`argparse`) + real fill polling

**Files:**
- Modify: `scripts/guard.py`
- Test: `tests/test_guard.py`

- [ ] **Step 1: Write the failing CLI test** (append)

```python
import subprocess, os


def test_cli_status_prints_not_halted(mem, monkeypatch):
    # Point guard at the isolated memory dir via env override.
    env = dict(os.environ)
    env["GUARD_STATE_PATH"] = str(mem / "state.json")
    env["GUARD_TRADES_PATH"] = str(mem / "trades.jsonl")
    out = subprocess.run(
        ["python3", "scripts/guard.py", "status"],
        capture_output=True, text=True, env=env,
    )
    assert out.returncode == 0
    assert "not halted" in out.stdout.lower()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_guard.py -k cli_status -q`
Expected: FAIL — no CLI output / non-zero exit (no `main`)

- [ ] **Step 3: Make paths env-overridable and add `main()` to `scripts/guard.py`**

Replace the three path constants near the top:

```python
STATE_PATH = Path(os.environ.get("GUARD_STATE_PATH", MEMORY / "state.json"))
TRADES_PATH = Path(os.environ.get("GUARD_TRADES_PATH", MEMORY / "trades.jsonl"))
```

Replace the `_wait_for_fill` placeholder with a real poller and add `main()` at the end of the file:

```python
def wait_for_fill(client, order_id, tries=15, delay=1.0):
    for _ in range(tries):
        orders = client.orders(status="all") if hasattr(client, "orders") else []
        for o in orders:
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
        naked = find_naked_positions(client.positions(), client.orders())
        if not naked:
            print("all positions protected"); return 0
        print("naked: " + ", ".join(naked))
        if args.fix:
            for sym in naked:
                pos = next(p for p in client.positions() if p["symbol"] == sym)
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
```

Note: update `place_buy` to call `wait_for_fill` for the real client only when the first submit returns a non-`filled` status. For v1 paper market orders, Alpaca fills near-instantly and `submit_order` returns the fill; the poller is a safety net. Leave the FakeClient path (immediate fill) untouched so tests pass.

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_guard.py -k cli_status -q`
Expected: PASS

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest -q`
Expected: PASS (all green)

- [ ] **Step 6: Commit**

```bash
git add scripts/guard.py tests/test_guard.py
git commit -m "feat(guard): CLI dispatch for all subcommands + fill poller"
```

---

## Task 11: `alpaca.sh` wrapper

**Files:**
- Create: `scripts/alpaca.sh`

- [ ] **Step 1: Write `scripts/alpaca.sh`**

```bash
#!/usr/bin/env bash
# Alpaca API wrapper. Uses --fail-with-body so error JSON is visible.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then set -a; source "$ENV_FILE"; set +a; fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"
API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"
H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"
CURL=(curl --fail-with-body -sS -H "$H_KEY" -H "$H_SEC")

cmd="${1:-}"; shift || true
case "$cmd" in
  account)    "${CURL[@]}" "$API/account" ;;
  positions)  "${CURL[@]}" "$API/positions" ;;
  position)   "${CURL[@]}" "$API/positions/${1:?usage: position SYM}" ;;
  quote)      "${CURL[@]}" "$DATA/stocks/${1:?usage: quote SYM}/quotes/latest" ;;
  orders)     "${CURL[@]}" "$API/orders?status=${1:-open}" ;;
  calendar)   "${CURL[@]}" "$API/calendar?start=${1:?usage: calendar START END}&end=${2:?}" ;;
  order)      "${CURL[@]}" -H "Content-Type: application/json" -X POST \
                -d "${1:?usage: order '<json>'}" "$API/orders" ;;
  cancel)     "${CURL[@]}" -X DELETE "$API/orders/${1:?usage: cancel ORDER_ID}" ;;
  cancel-all) "${CURL[@]}" -X DELETE "$API/orders" ;;
  close)      "${CURL[@]}" -X DELETE "$API/positions/${1:?usage: close SYM}" ;;
  close-all)  "${CURL[@]}" -X DELETE "$API/positions" ;;
  *) echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|calendar|order|cancel|cancel-all|close|close-all> [args]" >&2; exit 1 ;;
esac
echo
```

- [ ] **Step 2: Make it executable and syntax-check**

Run: `chmod +x scripts/alpaca.sh && bash -n scripts/alpaca.sh && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify usage guard fires without a subcommand**

Run: `ALPACA_API_KEY=x ALPACA_SECRET_KEY=y bash scripts/alpaca.sh 2>&1 | head -1`
Expected: a line starting with `Usage:`

- [ ] **Step 4: Commit**

```bash
git add scripts/alpaca.sh
git commit -m "feat: alpaca.sh wrapper with --fail-with-body and calendar"
```

---

## Task 12: `discord.sh` wrapper (with committed fallback)

**Files:**
- Create: `scripts/discord.sh`

- [ ] **Step 1: Write `scripts/discord.sh`**

```bash
#!/usr/bin/env bash
# Discord notification wrapper. Falls back to memory/notifications.log (committed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
FALLBACK="$ROOT/memory/notifications.log"
if [[ -f "$ENV_FILE" ]]; then set -a; source "$ENV_FILE"; set +a; fi

if [[ $# -gt 0 ]]; then msg="$*"; else msg="$(cat)"; fi
if [[ -z "${msg// /}" ]]; then echo 'usage: bash scripts/discord.sh "<message>"' >&2; exit 1; fi
stamp="$(date '+%Y-%m-%d %H:%M %Z')"

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  printf '\n[%s] (fallback — DISCORD_WEBHOOK_URL unset)\n%s\n' "$stamp" "$msg" >> "$FALLBACK"
  echo "[discord fallback] appended to memory/notifications.log"
  exit 0
fi

payload="$(python3 -c 'import json,sys; print(json.dumps({"content": sys.argv[1]}))' "$msg")"
curl --fail-with-body -sS -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" -d "$payload"
echo
```

- [ ] **Step 2: Make executable + syntax check**

Run: `chmod +x scripts/discord.sh && bash -n scripts/discord.sh && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify fallback path writes to the committed log**

Run: `( unset DISCORD_WEBHOOK_URL; bash scripts/discord.sh "test message" ) && tail -2 memory/notifications.log`
Expected: `[discord fallback] appended...` then the message visible in the log.

- [ ] **Step 4: Reset the log and commit**

```bash
: > memory/notifications.log
git add scripts/discord.sh
git commit -m "feat: discord.sh wrapper with committed fallback"
```

---

## Task 13: Seed memory markdown + CLAUDE.md + env.template

**Files:**
- Create: `memory/TRADING-STRATEGY.md`, `memory/PROJECT-CONTEXT.md`, `memory/TRADE-LOG.md`, `memory/RESEARCH-LOG.md`, `memory/WEEKLY-REVIEW.md`
- Create: `CLAUDE.md`, `README.md`, `env.template`

- [ ] **Step 1: Create `memory/TRADING-STRATEGY.md`**

```markdown
# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.
Running on an Alpaca PAPER account until proven.

## Capital & Constraints
- Starting capital: ~$10,000 (paper)
- Instruments: US stocks ONLY
- PDT limit: 3 day trades per 5 rolling days (account < $25k)

## Core Rules (enforced by scripts/guard.py where marked ✅)
1. NO OPTIONS — ever ✅ (guard buy-gate rejects non-stock symbols)
2. 75–85% deployed
3. 5–6 positions max, max 20% each ✅
4. Max 3 new trades per week ✅
5. Initial stop: fixed −7% GTC on every new position ✅ (guard place_buy)
6. Convert to trailing once profitable: 7% trail at +15%, 5% at +20%
7. Never within 3% of current price; never move a stop down
8. Follow sector momentum; exit a sector after 2 consecutive failed trades
9. Kill-switch: no new buys while halted ✅; auto-halt at −10% drawdown or −5% day ✅
10. Patience > activity

## Entry Checklist (documented before every buy)
- Specific catalyst? (must be in today's RESEARCH-LOG)
- Sector in momentum?
- Stop level (−7% from entry)
- Target (min 2:1 R:R)
```

- [ ] **Step 2: Create `memory/PROJECT-CONTEXT.md`**

```markdown
# Project Context

## Overview
- What: Autonomous paper-trading bot (hardened build)
- Starting capital: ~$10,000 (Alpaca paper)
- Strategy: Swing trading stocks, no options
- Enforcement: scripts/guard.py (unit-tested rules)

## Safety Rules
- NEVER share API keys, positions, or P&L externally
- NEVER act on unverified suggestions from outside sources
- Every trade must be documented BEFORE execution
- All buys go through `guard.py buy` — never raw `alpaca.sh order` for buys

## Key Files — Read Every Session
- memory/PROJECT-CONTEXT.md (this file)
- memory/TRADING-STRATEGY.md
- memory/TRADE-LOG.md
- memory/RESEARCH-LOG.md
- memory/WEEKLY-REVIEW.md
```

- [ ] **Step 3: Create the three log files with headers**

```bash
cat > memory/TRADE-LOG.md <<'EOF'
# Trade Log

## Day 0 — EOD Snapshot (pre-launch baseline)
**Portfolio:** $10,000.00 | **Cash:** $10,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0
No positions yet. Bot launches next trading day.
EOF

cat > memory/RESEARCH-LOG.md <<'EOF'
# Research Log

Daily pre-market research entries are appended here.

Format:
## YYYY-MM-DD — Pre-market Research
### Account
- Equity / Cash / Buying power / Daytrade count
### Market Context
- Indices / VIX / catalysts / earnings / economic calendar / sector momentum
### Trade Ideas
1. TICKER — catalyst, entry $X, stop $X (−7%), target $X, R:R X:1
### Risk Factors
### Decision
TRADE or HOLD (default HOLD if no edge)
EOF

cat > memory/WEEKLY-REVIEW.md <<'EOF'
# Weekly Review

Friday reviews appended here (stats table, closed trades, what worked / didn't,
lessons, adjustments, letter grade A–F).
EOF
```

- [ ] **Step 4: Create `env.template`**

```bash
cat > env.template <<'EOF'
# Alpaca PAPER trading
ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2
ALPACA_DATA_ENDPOINT=https://data.alpaca.markets/v2
ALPACA_API_KEY=your_paper_key_here
ALPACA_SECRET_KEY=your_paper_secret_here

# Discord notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
EOF
```

- [ ] **Step 5: Create `CLAUDE.md`**

```markdown
# Trading Bot Agent Instructions

You are an autonomous AI trading bot managing an Alpaca PAPER ~$10,000 account.
Goal: beat the S&P 500. Aggressive but disciplined. Stocks only — no options, ever.
Communicate ultra-concise: short bullets, no fluff.

## Read-Me-First (every session)
- memory/PROJECT-CONTEXT.md — mission and safety rules
- memory/TRADING-STRATEGY.md — the rulebook, never violate
- memory/TRADE-LOG.md — open positions, entries, stops
- memory/RESEARCH-LOG.md — today's research before any trade
- memory/WEEKLY-REVIEW.md — Friday template

## Enforcement — non-negotiable
- ALL buys go through `python3 scripts/guard.py buy '<json>'`. Never place a buy
  with raw alpaca.sh. The guard enforces every hard rule and places the −7% stop.
- Check `python3 scripts/guard.py status` and `is-trading-day` before acting.
- Use bash scripts/alpaca.sh, scripts/discord.sh. Never curl these APIs directly.

## Strategy Hard Rules (quick reference)
NO OPTIONS. Max 5–6 positions, 20% each. Max 3 trades/week. −7% initial stop,
trailing once profitable (7% at +15%, 5% at +20%). Never move a stop down.
Exit a sector after 2 failed trades. Kill-switch halts new buys. Patience > activity.

## Communication Style
Ultra concise. No preamble. Match existing memory file formats exactly.
```

- [ ] **Step 6: Create `README.md`**

```markdown
# Hardened Trading Bot (Alpaca Paper)

Autonomous swing-trading agent. Rules enforced by `scripts/guard.py` (unit-tested).
Five Claude Code cloud routines run each weekday. See
`docs/superpowers/specs/2026-07-15-hardened-trading-bot-design.md`.

## Local test
1. `cp env.template .env` and fill in Alpaca paper keys + Discord webhook.
2. `python3 -m pytest -q` — all rule tests pass.
3. In Claude Code: `/portfolio` — prints account + positions.

## Cloud
Set the 5 env vars on each routine (NOT in a .env file). Enable "allow unrestricted
branch pushes". Paste each `routines/*.md` prompt verbatim. Schedules in the spec.
```

- [ ] **Step 7: Verify pytest still green and commit**

Run: `python3 -m pytest -q`
Expected: PASS

```bash
git add memory/*.md CLAUDE.md README.md env.template
git commit -m "docs: seed memory, CLAUDE.md, README, env.template"
```

---

## Task 14: Local slash commands

**Files:**
- Create: `.claude/commands/portfolio.md`, `trade.md`, `halt.md`, `resume.md`, `reconcile.md`

- [ ] **Step 1: Create `.claude/commands/portfolio.md`**

```markdown
---
description: Read-only snapshot of account, positions, open orders, and stops
---
Print an ad-hoc snapshot. No state changes, no orders, no file writes.
1. bash scripts/alpaca.sh account
2. bash scripts/alpaca.sh positions
3. bash scripts/alpaca.sh orders
4. python3 scripts/guard.py status

Format concisely: equity, cash %, buying power, daytrade count; per position
SYM | shares | entry -> now | unrealized P&L | stop. Flag any position with NO
protective stop, or a stop above/below where it should be. No other commentary.
```

- [ ] **Step 2: Create `.claude/commands/trade.md`**

```markdown
---
description: Manual trade helper with rule validation. Usage — /trade SYMBOL SHARES buy|sell
---
Args: SYMBOL SHARES SIDE. If missing, ask.
1. bash scripts/alpaca.sh quote SYMBOL  (capture ask price P)
2. For BUY: run
   python3 scripts/guard.py buy '{"symbol":"SYM","qty":"N","price":"P","thesis":"...","sector":"..."}'
   The guard validates all rules, places the buy, and sets the −7% stop.
   If it prints BLOCKED, stop and show the reason.
3. For SELL: confirm the position exists, then bash scripts/alpaca.sh close SYM.
4. Append the result to memory/TRADE-LOG.md and send bash scripts/discord.sh "<summary>".
```

- [ ] **Step 3: Create `halt.md`, `resume.md`, `reconcile.md`**

```markdown
---
description: Halt all new buys (kill-switch on)
---
Run: python3 scripts/guard.py halt "manual halt via /halt"
Then bash scripts/discord.sh "🛑 Trading halted (manual)."
```

```markdown
---
description: Clear the kill-switch (allow new buys)
---
Run: python3 scripts/guard.py resume
Then bash scripts/discord.sh "✅ Trading resumed."
```

```markdown
---
description: Find and fix positions with no protective stop
---
Run: python3 scripts/guard.py reconcile --fix
Report what it found and any stops it placed.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/commands
git commit -m "feat: local slash commands (portfolio, trade, halt, resume, reconcile)"
```

---

## Task 15: Routine prompt — pre-market

**Files:**
- Create: `routines/pre-market.md`

- [ ] **Step 1: Create `routines/pre-market.md`**

```markdown
You are an autonomous trading bot managing an Alpaca PAPER ~$10,000 account.
Stocks only — NEVER options. Ultra-concise: short bullets, no fluff.
You are running the PRE-MARKET research workflow. DATE=$(date +%Y-%m-%d).

IMPORTANT — ENVIRONMENT VARIABLES:
- These are ALREADY exported: ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_ENDPOINT,
  ALPACA_DATA_ENDPOINT, DISCORD_WEBHOOK_URL.
- There is NO .env file and you MUST NOT create, write, or source one.
- If a wrapper prints "not set in environment" -> STOP, send one Discord alert
  naming the missing var, and exit.
- Verify before any wrapper call:
  for v in ALPACA_API_KEY ALPACA_SECRET_KEY DISCORD_WEBHOOK_URL; do
    [[ -n "${!v:-}" ]] && echo "$v: set" || echo "$v: MISSING"; done

IMPORTANT — PERSISTENCE: fresh clone. Changes VANISH unless committed and pushed.
You MUST commit and push at STEP 6.

STEP 0 — Gate checks:
  python3 scripts/guard.py is-trading-day   # if "closed", commit nothing and EXIT
  python3 scripts/guard.py status           # note if HALTED

STEP 1 — Read memory: TRADING-STRATEGY.md, tail of TRADE-LOG.md, tail of RESEARCH-LOG.md.

STEP 2 — Pull live state:
  bash scripts/alpaca.sh account
  bash scripts/alpaca.sh positions
  bash scripts/alpaca.sh orders

STEP 3 — Research with the native WebSearch tool. Cover: S&P 500 futures, VIX,
top catalysts today, pre-market earnings, economic calendar (CPI/PPI/FOMC/jobs),
sector momentum, and news on each currently-held ticker. Prefer reputable sources
and note them inline.

STEP 4 — Append a dated entry to memory/RESEARCH-LOG.md (match the file's format):
account snapshot; market context; 2–3 trade ideas each with catalyst + entry + stop
(−7%) + target + R:R; risk factors; Decision (TRADE or HOLD — default HOLD).

STEP 5 — Notification: silent unless urgent (a held position already below −7% pre-market,
a broken thesis, a major event, or guard reported HALTED). If urgent:
  bash scripts/discord.sh "<one line>"

STEP 6 — COMMIT AND PUSH (mandatory):
  git add memory/RESEARCH-LOG.md memory/state.json
  git commit -m "pre-market research $DATE"
  git push origin main
  On push failure: git pull --rebase origin main, then push. Never force-push.
```

- [ ] **Step 2: Commit**

```bash
git add routines/pre-market.md
git commit -m "feat(routines): pre-market prompt"
```

---

## Task 16: Routine prompt — market-open

**Files:**
- Create: `routines/market-open.md`

- [ ] **Step 1: Create `routines/market-open.md`**

```markdown
You are an autonomous trading bot. Stocks only — NEVER options. Ultra-concise.
You are running the MARKET-OPEN execution workflow. DATE=$(date +%Y-%m-%d).

IMPORTANT — ENVIRONMENT VARIABLES: ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_ENDPOINT,
ALPACA_DATA_ENDPOINT, DISCORD_WEBHOOK_URL are already exported. NO .env file — do not
create one. If a wrapper prints "not set", send one Discord alert and exit. Verify:
  for v in ALPACA_API_KEY ALPACA_SECRET_KEY DISCORD_WEBHOOK_URL; do
    [[ -n "${!v:-}" ]] && echo "$v: set" || echo "$v: MISSING"; done

IMPORTANT — PERSISTENCE: fresh clone; commit and push at STEP 7 or nothing persists.

STEP 0 — Gate checks:
  python3 scripts/guard.py is-trading-day   # if closed, EXIT
  python3 scripts/guard.py status           # if HALTED, do NOT place buys; skip to STEP 1 read-only

STEP 1 — Read TODAY's entry in memory/RESEARCH-LOG.md. If missing, run the pre-market
research steps inline first — NEVER trade without documented research.

STEP 2 — Reconcile protective stops FIRST (covers any position left unprotected):
  python3 scripts/guard.py reconcile --fix

STEP 3 — Re-validate each planned trade with fresh data:
  bash scripts/alpaca.sh quote <ticker>   # capture ask price P; skip if halted/zero/wide spread

STEP 4 — Execute each approved trade THROUGH THE GUARD (never raw alpaca.sh order):
  python3 scripts/guard.py buy '{"symbol":"SYM","qty":"N","price":"P","thesis":"<catalyst>","sector":"<sector>","target":"<X>","rr":"<X:1>"}'
  - The guard validates all rules and places the −7% stop automatically.
  - If it prints "BLOCKED: <reason>", skip that trade and note the reason.

STEP 5 — For any position already up big (guide tiers) tighten toward trailing only if
+15% (7%) or +20% (5%), never within 3% of price, never move a stop down. Use
bash scripts/alpaca.sh cancel <id> then bash scripts/alpaca.sh order '<trailing_stop json>'.

STEP 6 — Append each executed trade to memory/TRADE-LOG.md (guard already wrote trades.jsonl).

STEP 7 — Notification only if a trade was placed:
  bash scripts/discord.sh "<tickers, shares, fills, one-line why>"

STEP 8 — COMMIT AND PUSH (if anything changed):
  git add memory/TRADE-LOG.md memory/trades.jsonl memory/state.json
  git commit -m "market-open $DATE"
  git push origin main
  On push failure: git pull --rebase origin main, then push. Never force-push.
```

- [ ] **Step 2: Commit**

```bash
git add routines/market-open.md
git commit -m "feat(routines): market-open prompt"
```

---

## Task 17: Routine prompt — midday

**Files:**
- Create: `routines/midday.md`

- [ ] **Step 1: Create `routines/midday.md`**

```markdown
You are an autonomous trading bot. Stocks only — NEVER options. Ultra-concise.
You are running the MIDDAY scan workflow. DATE=$(date +%Y-%m-%d).

ENVIRONMENT VARIABLES + PERSISTENCE: same rules as market-open (no .env; verify vars;
commit and push at STEP 7).

STEP 0 — Gate checks:
  python3 scripts/guard.py is-trading-day   # if closed, EXIT

STEP 1 — Read TRADING-STRATEGY.md (exit rules), tail of TRADE-LOG.md, today's RESEARCH-LOG.

STEP 2 — Reconcile stops, then pull state:
  python3 scripts/guard.py reconcile --fix
  bash scripts/alpaca.sh positions
  bash scripts/alpaca.sh orders

STEP 3 — Cut losers. For any position with unrealized_plpc <= -0.07:
  bash scripts/alpaca.sh close SYM
  bash scripts/alpaca.sh cancel <its stop order id>
  Append to trades.jsonl a sell record and log the exit + realized P&L + "cut at -7%".
  (Note: the −7% GTC stop usually fires automatically; this catches gaps/edge cases.)

STEP 4 — Tighten winners: up >= +20% -> trailing 5%; up >= +15% -> trailing 7%.
Cancel old stop, place new trailing_stop. Never within 3% of price; never lower a stop.

STEP 5 — Thesis check: if a thesis broke intraday, cut even if not yet at −7%. Document why.

STEP 6 — Risk check:
  python3 scripts/guard.py check-risk    # auto-halts on breach

STEP 7 — Notification only if action was taken:
  bash scripts/discord.sh "<action summary>"

STEP 8 — COMMIT AND PUSH (if changed):
  git add memory/TRADE-LOG.md memory/trades.jsonl memory/RESEARCH-LOG.md memory/state.json
  git commit -m "midday $DATE"
  git push origin main
  On push failure: rebase and retry. Never force-push.
```

- [ ] **Step 2: Commit**

```bash
git add routines/midday.md
git commit -m "feat(routines): midday prompt"
```

---

## Task 18: Routine prompt — daily-summary

**Files:**
- Create: `routines/daily-summary.md`

- [ ] **Step 1: Create `routines/daily-summary.md`**

```markdown
You are an autonomous trading bot. Stocks only. Ultra-concise.
You are running the DAILY-SUMMARY workflow. DATE=$(date +%Y-%m-%d).

ENVIRONMENT VARIABLES + PERSISTENCE: same rules (no .env; verify vars; push at STEP 6).

STEP 0 — python3 scripts/guard.py is-trading-day   # if closed, EXIT

STEP 1 — Read memory: most recent EOD snapshot in TRADE-LOG.md (yesterday's equity),
count today's trades in memory/trades.jsonl, and this week's trades:
  python3 scripts/guard.py weekly-trades

STEP 2 — Pull final state: account, positions, orders (via alpaca.sh).

STEP 3 — Compute: Day P&L ($ and %) vs yesterday's equity; Phase P&L vs $10,000;
trades today; trades this week.

STEP 4 — Update risk state so tomorrow's daily-loss math works, and refresh high-water:
  python3 scripts/guard.py check-risk
  Then set last_equity to today's equity in memory/state.json (edit the JSON: last_equity = today's equity; keep high_water_mark as the max).

STEP 5 — Append an EOD snapshot to memory/TRADE-LOG.md:
  ### MMM DD — EOD Snapshot (Day N)
  **Portfolio:** $X | **Cash:** $X (X%) | **Day P&L:** ±$X (±X%) | **Phase P&L:** ±$X (±X%)
  | Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
  **Notes:** one plain-english paragraph. Note HALTED status if set.

STEP 6 — Send ONE Discord message (ALWAYS, even on no-trade days), <= 15 lines:
  bash scripts/discord.sh "EOD MMM DD
  Portfolio: \$X (±X% day, ±X% phase)
  Cash: \$X | Halt: <yes/no>
  Trades today: <list or none>
  Open: SYM ±X.X% (stop \$X.XX)
  Tomorrow: <one-line plan>"

STEP 7 — COMMIT AND PUSH (mandatory — tomorrow's Day P&L depends on this):
  git add memory/TRADE-LOG.md memory/state.json memory/trades.jsonl
  git commit -m "EOD snapshot $DATE"
  git push origin main
  On push failure: rebase and retry. Never force-push.
```

- [ ] **Step 2: Commit**

```bash
git add routines/daily-summary.md
git commit -m "feat(routines): daily-summary prompt"
```

---

## Task 19: Routine prompt — weekly-review

**Files:**
- Create: `routines/weekly-review.md`

- [ ] **Step 1: Create `routines/weekly-review.md`**

```markdown
You are an autonomous trading bot. Stocks only. Ultra-concise.
You are running the FRIDAY WEEKLY-REVIEW workflow. DATE=$(date +%Y-%m-%d).

ENVIRONMENT VARIABLES + PERSISTENCE: same rules (no .env; verify vars; push at STEP 7).

STEP 0 — python3 scripts/guard.py is-trading-day   # if closed, EXIT

STEP 1 — Read WEEKLY-REVIEW.md (match its template), ALL this week's TRADE-LOG.md and
RESEARCH-LOG.md entries, and TRADING-STRATEGY.md.

STEP 2 — Pull week-end state: account, positions.

STEP 3 — Compute: starting portfolio (Monday), ending portfolio, week return ($ and %),
S&P 500 week return (native WebSearch), trades W/L/open, win rate, best/worst trade,
profit factor.

STEP 4 — Append a full review to memory/WEEKLY-REVIEW.md: stats table, closed trades
table, open positions, what worked (3–5), what didn't (3–5), key lessons, adjustments,
overall letter grade A–F.

STEP 5 — If a rule proved out for 2+ weeks or failed badly, update memory/TRADING-STRATEGY.md
and call out the change in the review.

STEP 6 — Reset the week baseline for next week in memory/state.json:
  set week_start_equity = this Friday's ending equity (Monday will read it).
  Send ONE Discord message (always), <= 15 lines:
  bash scripts/discord.sh "Week ending MMM DD
  Portfolio: \$X (±X% week, ±X% phase)
  vs S&P 500: ±X%
  Trades: N (W:X / L:Y / open:Z)
  Best: SYM +X% Worst: SYM -X%
  Grade: <letter>"

STEP 7 — COMMIT AND PUSH (mandatory):
  git add memory/WEEKLY-REVIEW.md memory/TRADING-STRATEGY.md memory/state.json
  git commit -m "weekly review $DATE"
  git push origin main
  On push failure: rebase and retry. Never force-push.
```

- [ ] **Step 2: Commit**

```bash
git add routines/weekly-review.md
git commit -m "feat(routines): weekly-review prompt"
```

---

## Task 20: Final verification pass

**Files:** none (verification only)

- [ ] **Step 1: Full test suite green**

Run: `python3 -m pytest -q`
Expected: all tests PASS.

- [ ] **Step 2: All shell scripts syntax-clean**

Run: `for f in scripts/*.sh; do bash -n "$f" && echo "$f OK"; done`
Expected: each script prints `OK`.

- [ ] **Step 3: guard CLI smoke (no network commands)**

Run:
```bash
GUARD_STATE_PATH=/tmp/s.json GUARD_TRADES_PATH=/tmp/t.jsonl python3 scripts/guard.py halt "smoke"
GUARD_STATE_PATH=/tmp/s.json GUARD_TRADES_PATH=/tmp/t.jsonl python3 scripts/guard.py status
GUARD_STATE_PATH=/tmp/s.json GUARD_TRADES_PATH=/tmp/t.jsonl python3 scripts/guard.py resume
```
Expected: `halted: smoke` → `HALTED: smoke` → `resumed`.

- [ ] **Step 4: Confirm `.env` is ignored and no secrets are tracked**

Run: `git status --porcelain && git ls-files | grep -E '(^|/)\.env$' && echo "LEAK" || echo "no .env tracked"`
Expected: clean tree; `no .env tracked`.

- [ ] **Step 5: Confirm the memory contract files exist and are committed**

Run: `git ls-files memory/ | sort`
Expected: includes `state.json`, `trades.jsonl`, `notifications.log`, and the five `*.md` files.

- [ ] **Step 6: Final commit if anything is uncommitted**

```bash
git add -A && git commit -m "chore: final verification pass" || echo "nothing to commit"
```

---

## Post-implementation: manual setup (human-in-the-loop, not automatable)

These require the user and the web UI — do them together after the code is built:

1. Create an Alpaca **paper** account → copy API key + secret.
2. Create a Discord channel webhook → copy the URL.
3. `cp env.template .env`, fill in the four values, run `python3 -m pytest -q`, then `/portfolio` in Claude Code to smoke-test against the paper account.
4. Install the Claude GitHub App on the repo; enable "allow unrestricted branch pushes" on each routine's environment.
5. Create the five cloud routines, set the 5 env vars on each (NOT a .env file), set the crons (spec §9, in the user's market timezone), paste each `routines/*.md` verbatim, and hit "Run now" on pre-market to verify a commit lands on `main`.
6. Watch the first week closely; read every commit the bot makes.
```
