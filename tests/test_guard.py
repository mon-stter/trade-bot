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


def test_set_halt_sets_flag_and_reason():
    s = guard.set_halt(dict(guard.DEFAULT_STATE), "drawdown -12%")
    assert s["halted"] is True and s["halt_reason"] == "drawdown -12%"


def test_clear_halt_resets():
    s = guard.clear_halt({"halted": True, "halt_reason": "x"})
    assert s["halted"] is False and s["halt_reason"] == ""


def test_weekly_trade_count_counts_only_buys_in_current_week(tmp_path):
    p = tmp_path / "trades.jsonl"
    guard.append_jsonl(p, {"date": "2026-07-13", "side": "buy", "symbol": "AAA"})   # Mon
    guard.append_jsonl(p, {"date": "2026-07-15", "side": "buy", "symbol": "BBB"})   # Wed
    guard.append_jsonl(p, {"date": "2026-07-15", "side": "sell", "symbol": "AAA"})  # sell ignored
    guard.append_jsonl(p, {"date": "2026-07-06", "side": "buy", "symbol": "OLD"})   # prev week
    from datetime import date
    n = guard.weekly_trade_count(guard.read_jsonl(p), date(2026, 7, 15))
    assert n == 2


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
