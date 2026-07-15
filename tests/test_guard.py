import sys, json
from datetime import date
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import guard  # noqa: E402
from conftest import FakeClient  # noqa: E402


def test_load_dotenv_fills_missing_but_does_not_override(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comment\nFOO_NEW=abc\nFOO_EXISTING=fromfile\n\n")
    monkeypatch.setenv("FOO_EXISTING", "fromenv")
    monkeypatch.delenv("FOO_NEW", raising=False)
    guard.load_dotenv(env)
    import os
    assert os.environ["FOO_NEW"] == "abc"          # gap filled
    assert os.environ["FOO_EXISTING"] == "fromenv"  # process env wins


def test_load_dotenv_missing_file_is_noop(tmp_path):
    guard.load_dotenv(tmp_path / "nope.env")  # must not raise


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
    new_state, halt, reason = guard.evaluate_risk(9400.0, state)  # -6% day
    assert halt and "daily" in reason


def test_risk_no_daily_halt_when_last_equity_zero():
    state = {**guard.DEFAULT_STATE, "high_water_mark": 10000.0, "last_equity": 0.0}
    new_state, halt, reason = guard.evaluate_risk(9700.0, state)  # -3% dd only
    assert not halt


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


def test_is_trading_day_true_when_calendar_lists_today():
    client = FakeClient(calendar=[{"date": "2026-07-15", "open": "09:30", "close": "16:00"}])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is True


def test_is_trading_day_false_when_calendar_empty():
    client = FakeClient(calendar=[])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is False


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


def test_cli_status_prints_not_halted(mem):
    import subprocess, os
    env = dict(os.environ)
    env["GUARD_STATE_PATH"] = str(mem / "state.json")
    env["GUARD_TRADES_PATH"] = str(mem / "trades.jsonl")
    out = subprocess.run(
        [sys.executable, "scripts/guard.py", "status"],
        capture_output=True, text=True, env=env,
        stdin=subprocess.DEVNULL,
    )
    assert out.returncode == 0
    assert "not halted" in out.stdout.lower()
