import sys, json
from datetime import date, datetime, timezone
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
    positions = [{"symbol": "AAA", "qty": "10"}, {"symbol": "BBB", "qty": "5"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "trailing_stop", "qty": "10"}]
    assert guard.find_naked_positions(positions, orders) == ["BBB"]


def test_find_naked_positions_ignores_buy_orders():
    positions = [{"symbol": "AAA", "qty": "10"}]
    orders = [{"symbol": "AAA", "side": "buy", "type": "market", "qty": "10"}]
    assert guard.find_naked_positions(positions, orders) == ["AAA"]


def test_find_naked_positions_none_when_all_protected():
    positions = [{"symbol": "AAA", "qty": "10"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "stop", "qty": "10"}]
    assert guard.find_naked_positions(positions, orders) == []


def test_find_naked_positions_flags_partial_coverage():
    positions = [{"symbol": "AAA", "qty": "50"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "stop", "qty": "10"}]
    assert guard.find_naked_positions(positions, orders) == ["AAA"]


def test_unprotected_qty_counts_uncovered_shares():
    pos = {"symbol": "AAA", "qty": "50"}
    orders = [{"symbol": "AAA", "side": "sell", "type": "stop", "qty": "10"}]
    assert guard.unprotected_qty(pos, orders) == 40


def test_fix_naked_places_stop_for_uncovered_qty_only():
    positions = [{"symbol": "AAA", "qty": "50", "current_price": "100"}]
    orders = [{"symbol": "AAA", "side": "sell", "type": "stop", "qty": "10"}]
    client = FakeClient(positions=positions, orders=orders)
    placed = guard.fix_naked(client)
    assert placed == [("AAA", 40.0)]
    stop = client.submitted[0]
    assert stop["qty"] == "40" and stop["type"] == "stop"
    assert abs(float(stop["stop_price"]) - 93.0) < 0.01


def test_is_trading_day_true_when_calendar_lists_today():
    client = FakeClient(calendar=[{"date": "2026-07-15", "open": "09:30", "close": "16:00"}])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is True


def test_is_trading_day_false_when_calendar_empty():
    client = FakeClient(calendar=[])
    assert guard.is_trading_day(client, date(2026, 7, 15)) is False


def _cal(day="2026-07-15"):
    return FakeClient(calendar=[{"date": day, "open": "09:30", "close": "16:00"}])


def test_confirm_bar_end_is_30min_after_open_in_utc_during_edt():
    end = guard.confirm_bar_end(_cal(), date(2026, 7, 15))
    assert end == datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)


def test_confirm_bar_end_shifts_with_dst_in_est():
    """Same 09:30 local open is 15:00Z in winter, not 14:00Z — the gate must
    follow the exchange calendar, never a hardcoded UTC hour."""
    end = guard.confirm_bar_end(_cal("2026-01-15"), date(2026, 1, 15))
    assert end == datetime(2026, 1, 15, 15, 0, tzinfo=timezone.utc)


def test_confirm_bar_closed_false_while_bar_still_building():
    now = datetime(2026, 7, 15, 13, 34, tzinfo=timezone.utc)  # 4 min into the bar
    closed, remaining = guard.confirm_bar_closed(_cal(), date(2026, 7, 15), now=now)
    assert closed is False
    assert remaining == 26


def test_confirm_bar_closed_true_at_the_instant_it_closes():
    now = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)
    closed, remaining = guard.confirm_bar_closed(_cal(), date(2026, 7, 15), now=now)
    assert closed is True
    assert remaining == 0


def test_confirm_bar_closed_false_before_the_open():
    now = datetime(2026, 7, 15, 11, 50, tzinfo=timezone.utc)  # premarket
    closed, _ = guard.confirm_bar_closed(_cal(), date(2026, 7, 15), now=now)
    assert closed is False


def test_confirm_bar_closed_false_when_not_a_trading_day():
    closed, remaining = guard.confirm_bar_closed(
        FakeClient(calendar=[]), date(2026, 7, 18),
        now=datetime(2026, 7, 18, 20, 0, tzinfo=timezone.utc))
    assert closed is False
    assert remaining is None


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


def test_pdt_not_enforced_above_25k_equity():
    ok, reasons = guard.validate_buy(
        _order(qty="10", price="100"),
        _account(equity="100000", cash="50000", daytrade_count="3"), [], 0, False)
    assert ok, reasons


def test_place_buy_waits_for_fill_and_anchors_stop_to_actual_fill(mem):
    client = FakeClient(
        fills=[{"id": "b1", "status": "accepted", "filled_avg_price": None}],
        closed_orders=[{"id": "b1", "status": "filled", "filled_avg_price": "105"}])
    guard.place_buy(client, _order(symbol="AAPL", qty="10", price="100"),
                    state_path=mem / "state.json",
                    trades_path=mem / "trades.jsonl",
                    ref=date(2026, 7, 15))
    buy, stop = client.submitted
    assert abs(float(stop["stop_price"]) - 105 * 0.93) < 0.01
    rec = guard.read_jsonl(mem / "trades.jsonl")[-1]
    assert rec["price"] == 105.0 and rec["order_id"] == "b1"


def test_place_buy_cancels_and_aborts_when_buy_never_fills(mem, monkeypatch):
    monkeypatch.setattr(guard, "FILL_TRIES", 2)
    monkeypatch.setattr(guard, "FILL_DELAY", 0)
    client = FakeClient(fills=[{"id": "b1", "status": "accepted"}],
                        orders=[{"id": "b1", "status": "accepted"}])
    with pytest.raises(guard.GateError):
        guard.place_buy(client, _order(symbol="AAPL", qty="10", price="100"),
                        state_path=mem / "state.json",
                        trades_path=mem / "trades.jsonl",
                        ref=date(2026, 7, 15))
    assert client.canceled == ["b1"]
    assert len(client.submitted) == 1          # buy only — no orphaned stop
    assert guard.read_jsonl(mem / "trades.jsonl") == []


def test_notify_falls_back_to_log_file_when_webhook_unset(tmp_path, monkeypatch):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    log = tmp_path / "notifications.log"
    assert guard.notify("AUTO-HALT: test", log_path=log) == "fallback"
    assert "AUTO-HALT: test" in log.read_text()


def test_place_sell_cancels_stop_first_and_records_pnl(mem):
    positions = [{"symbol": "AAPL", "qty": "10",
                  "avg_entry_price": "100", "current_price": "95"}]
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell", "type": "stop", "qty": "10"}]
    client = FakeClient(positions=positions, orders=orders,
                        fills=[{"id": "x1", "status": "filled", "filled_avg_price": "95"}])
    guard.append_jsonl(mem / "trades.jsonl",
                       {"date": "2026-07-13", "symbol": "AAPL", "side": "buy",
                        "qty": 10, "price": 100.0, "sector": "tech"})
    guard.place_sell(client, {"symbol": "AAPL", "reason": "cut at -7%"},
                     trades_path=mem / "trades.jsonl", ref=date(2026, 7, 15))
    assert client.canceled == ["s1"]           # stop canceled BEFORE selling
    sell = client.submitted[0]
    assert sell["side"] == "sell" and sell["type"] == "market" and sell["qty"] == "10"
    rec = guard.read_jsonl(mem / "trades.jsonl")[-1]
    assert rec["side"] == "sell" and rec["pnl"] == -50.0
    assert rec["sector"] == "tech" and rec["order_id"] == "x1"


def test_place_sell_rejects_when_no_position(mem):
    client = FakeClient()
    with pytest.raises(guard.GateError):
        guard.place_sell(client, {"symbol": "AAPL"},
                         trades_path=mem / "trades.jsonl", ref=date(2026, 7, 15))
    assert client.submitted == []


def test_sync_records_fired_stop_and_is_idempotent(mem):
    closed = [
        {"id": "st9", "symbol": "AAPL", "side": "sell", "type": "stop",
         "status": "filled", "filled_qty": "10", "filled_avg_price": "93",
         "filled_at": "2026-07-15T14:00:00Z"},
        {"id": "b1", "symbol": "AAPL", "side": "buy", "type": "market",
         "status": "filled", "filled_qty": "10", "filled_avg_price": "100"},
    ]
    client = FakeClient(closed_orders=closed)
    guard.append_jsonl(mem / "trades.jsonl",
                       {"date": "2026-07-13", "symbol": "AAPL", "side": "buy",
                        "qty": 10, "price": 100.0, "sector": "tech", "order_id": "b1"})
    added = guard.sync_trades(client, trades_path=mem / "trades.jsonl",
                              ref=date(2026, 7, 15))
    assert len(added) == 1
    rec = guard.read_jsonl(mem / "trades.jsonl")[-1]
    assert rec["order_id"] == "st9" and rec["pnl"] == -70.0
    assert rec["date"] == "2026-07-15" and rec["sector"] == "tech"
    assert guard.sync_trades(client, trades_path=mem / "trades.jsonl",
                             ref=date(2026, 7, 15)) == []


def test_sector_streak_counts_consecutive_losses():
    records = [
        {"side": "sell", "sector": "tech", "pnl": -10},
        {"side": "sell", "sector": "energy", "pnl": -5},
        {"side": "sell", "sector": "tech", "pnl": 20},
        {"side": "sell", "sector": "tech", "pnl": -1},
        {"side": "sell", "sector": "tech", "pnl": -2},
    ]
    assert guard.sector_streak(records, "tech") == 2
    assert guard.sector_streak(records, "energy") == 1
    assert guard.sector_streak(records, "health") == 0


def test_rejects_buy_in_sector_with_two_straight_losses():
    ok, reasons = guard.validate_buy(_order(), _account(), [], 0, False,
                                     sector_streak=2)
    assert not ok and any("sector" in r for r in reasons)


def test_place_buy_blocked_by_sector_streak(mem):
    for pnl in (-5, -3):
        guard.append_jsonl(mem / "trades.jsonl",
                           {"date": "2026-07-13", "symbol": "XX", "side": "sell",
                            "qty": 1, "price": 10, "pnl": pnl, "sector": "tech"})
    client = FakeClient(account=_account(equity="100000", cash="100000"))
    with pytest.raises(guard.GateError):
        guard.place_buy(client, {**_order(), "sector": "tech"},
                        state_path=mem / "state.json",
                        trades_path=mem / "trades.jsonl",
                        ref=date(2026, 7, 15))
    assert client.submitted == []


def _pos(symbol="AAPL", qty="10", plpc="0.16", price="116"):
    return {"symbol": symbol, "qty": qty, "unrealized_plpc": plpc,
            "current_price": price}


def test_tighten_replaces_fixed_stop_with_7pct_trail_at_15pct_gain():
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell", "type": "stop",
               "qty": "10", "stop_price": "93.00"}]
    client = FakeClient(positions=[_pos(plpc="0.16")], orders=orders)
    assert guard.tighten_stops(client) == [("AAPL", 7.0)]
    assert client.canceled == ["s1"]
    new = client.submitted[0]
    assert new["type"] == "trailing_stop" and new["trail_percent"] == "7"


def test_tighten_uses_5pct_trail_at_20pct_gain():
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell", "type": "stop",
               "qty": "10", "stop_price": "93.00"}]
    client = FakeClient(positions=[_pos(plpc="0.21", price="121")], orders=orders)
    assert guard.tighten_stops(client) == [("AAPL", 5.0)]


def test_tighten_skips_when_already_trailing_at_target():
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell",
               "type": "trailing_stop", "qty": "10", "trail_percent": "7"}]
    client = FakeClient(positions=[_pos(plpc="0.16")], orders=orders)
    assert guard.tighten_stops(client) == []
    assert client.canceled == [] and client.submitted == []


def test_tighten_ignores_positions_below_15pct():
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell", "type": "stop",
               "qty": "10", "stop_price": "93.00"}]
    client = FakeClient(positions=[_pos(plpc="0.10", price="110")], orders=orders)
    assert guard.tighten_stops(client) == []
    assert client.canceled == [] and client.submitted == []


def test_tighten_reasserts_old_stop_when_replacement_fails():
    orders = [{"id": "s1", "symbol": "AAPL", "side": "sell", "type": "stop",
               "qty": "10", "stop_price": "93.00"}]
    client = FakeClient(positions=[_pos(plpc="0.16")], orders=orders,
                        fills=[RuntimeError("rejected")])
    assert guard.tighten_stops(client) == []   # failed replacement not counted
    reassert = client.submitted[-1]
    assert reassert["type"] == "stop" and reassert["stop_price"] == "93.00"


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


# --- research-log level contract (the never-traded deadlock) -----------------
#
# market-open can only buy an idea whose research entry names a NUMERIC level L.
# Before this contract existed, pre-market wrote prose ("if a clean level
# appears") and every session logged "no idea named a numeric level L" -> the
# pipeline was structurally incapable of ever placing a trade. These tests pin
# the machine-readable format so that regression is loud instead of silent.

_GOOD_LINE = ("- IDEA: LMT | L=512.40 | stop=476.53 | target=584.00 | rr=2.0:1 "
              "| sector=defense | catalyst=record backlog + Iran escalation")


def _log(*sections):
    return "# Research Log\n\n" + "\n\n".join(sections) + "\n"


def _entry(day, *lines):
    return f"## {day} — Pre-market Research\n### Trade Ideas\n" + "\n".join(lines)


def test_parse_research_ideas_extracts_numeric_level():
    text = _log(_entry("2026-07-31", _GOOD_LINE))
    ideas = guard.parse_research_ideas(text, date(2026, 7, 31))
    assert len(ideas) == 1
    idea = ideas[0]
    assert idea["symbol"] == "LMT"
    assert idea["level"] == 512.40
    assert idea["stop"] == 476.53
    assert idea["target"] == 584.00
    assert idea["rr"] == 2.0
    assert idea["sector"] == "defense"
    assert "record backlog" in idea["catalyst"]


def test_parse_research_ideas_ignores_prose_ideas():
    """The exact shape that produced 11 straight no-trade days."""
    prose = ("1. LMT/RTX/NOC (defense) — watch for a confirmed post-open hold "
             "above a fresh premarket high, stop -7%, target ~2:1 if a clean "
             "level appears.")
    text = _log(_entry("2026-07-31", prose))
    assert guard.parse_research_ideas(text, date(2026, 7, 31)) == []


def test_parse_research_ideas_only_reads_todays_section():
    text = _log(_entry("2026-07-30", _GOOD_LINE),
                _entry("2026-07-31", "- NO-TRADE: XOM — earnings blackout"))
    assert guard.parse_research_ideas(text, date(2026, 7, 31)) == []
    assert len(guard.parse_research_ideas(text, date(2026, 7, 30))) == 1


def test_parse_research_ideas_missing_section_is_empty():
    text = _log(_entry("2026-07-30", _GOOD_LINE))
    assert guard.parse_research_ideas(text, date(2026, 7, 31)) == []


def test_validate_research_idea_accepts_well_formed():
    idea = guard.parse_research_ideas(_log(_entry("2026-07-31", _GOOD_LINE)),
                                      date(2026, 7, 31))[0]
    assert guard.validate_research_idea(idea) == []


def test_validate_research_idea_rejects_stop_above_level():
    line = ("- IDEA: LMT | L=100.00 | stop=105.00 | target=130.00 | rr=2.0:1 "
            "| sector=defense | catalyst=x")
    idea = guard.parse_research_ideas(_log(_entry("2026-07-31", line)),
                                      date(2026, 7, 31))[0]
    assert any("stop" in p for p in guard.validate_research_idea(idea))


def test_validate_research_idea_rejects_target_below_level():
    line = ("- IDEA: LMT | L=100.00 | stop=93.00 | target=95.00 | rr=2.0:1 "
            "| sector=defense | catalyst=x")
    idea = guard.parse_research_ideas(_log(_entry("2026-07-31", line)),
                                      date(2026, 7, 31))[0]
    assert any("target" in p for p in guard.validate_research_idea(idea))


def test_validate_research_idea_rejects_sub_2to1_rr():
    line = ("- IDEA: LMT | L=100.00 | stop=93.00 | target=110.00 | rr=1.5:1 "
            "| sector=defense | catalyst=x")
    idea = guard.parse_research_ideas(_log(_entry("2026-07-31", line)),
                                      date(2026, 7, 31))[0]
    assert any("2:1" in p for p in guard.validate_research_idea(idea))


def test_validate_research_idea_rejects_missing_catalyst():
    line = ("- IDEA: LMT | L=100.00 | stop=93.00 | target=130.00 | rr=2.0:1 "
            "| sector=defense | catalyst=TBD")
    idea = guard.parse_research_ideas(_log(_entry("2026-07-31", line)),
                                      date(2026, 7, 31))[0]
    assert any("catalyst" in p for p in guard.validate_research_idea(idea))


def test_confirms_entry_requires_close_above_level():
    assert guard.confirms_entry({"c": 101.0, "l": 100.5}, 100.0) is True
    assert guard.confirms_entry({"c": 99.0, "l": 98.0}, 100.0) is False


def test_confirms_entry_allows_shallow_wick_but_not_deep_one():
    # low may dip under L by up to 1%
    assert guard.confirms_entry({"c": 101.0, "l": 99.5}, 100.0) is True
    assert guard.confirms_entry({"c": 101.0, "l": 98.9}, 100.0) is False


def test_cli_ideas_exits_nonzero_when_no_numeric_level(mem, tmp_path):
    import subprocess, os
    research = tmp_path / "RESEARCH-LOG.md"
    research.write_text(_log(_entry(date.today().isoformat(),
                                    "1. LMT — watch for a clean level.")),
                        encoding="utf-8")
    env = dict(os.environ)
    env["GUARD_STATE_PATH"] = str(mem / "state.json")
    env["GUARD_TRADES_PATH"] = str(mem / "trades.jsonl")
    env["GUARD_RESEARCH_PATH"] = str(research)
    out = subprocess.run([sys.executable, "scripts/guard.py", "ideas"],
                         capture_output=True, text=True, env=env,
                         stdin=subprocess.DEVNULL)
    assert out.returncode == 1
    assert "no idea" in (out.stdout + out.stderr).lower()


def test_cli_ideas_emits_json_for_valid_idea(mem, tmp_path):
    import subprocess, os
    research = tmp_path / "RESEARCH-LOG.md"
    research.write_text(_log(_entry(date.today().isoformat(), _GOOD_LINE)),
                        encoding="utf-8")
    env = dict(os.environ)
    env["GUARD_STATE_PATH"] = str(mem / "state.json")
    env["GUARD_TRADES_PATH"] = str(mem / "trades.jsonl")
    env["GUARD_RESEARCH_PATH"] = str(research)
    out = subprocess.run([sys.executable, "scripts/guard.py", "ideas"],
                         capture_output=True, text=True, env=env,
                         stdin=subprocess.DEVNULL)
    assert out.returncode == 0
    payload = json.loads(out.stdout)
    assert payload[0]["symbol"] == "LMT" and payload[0]["level"] == 512.40


# --- position sizing --------------------------------------------------------
#
# Until the level-contract fix, no trade ever reached the buy step, so "qty"
# was never actually derived by anything. These pin the arithmetic so the first
# live order is sized by rule rather than by whatever number looked reasonable.

def test_position_size_uses_20pct_of_equity():
    assert guard.position_size(100000, 100000, 500.0) == 40   # 20000/500


def test_position_size_floors_partial_shares():
    assert guard.position_size(100000, 100000, 300.0) == 66   # 20000/300 = 66.67


def test_position_size_never_exceeds_the_20pct_cap():
    equity, price = 100000, 512.40
    qty = guard.position_size(equity, equity, price)
    assert qty * price <= guard.MAX_POSITION_PCT * equity


def test_position_size_is_capped_by_available_cash():
    # 20% of equity is 20000, but only 5000 cash is left
    assert guard.position_size(100000, 5000, 500.0) == 10


def test_position_size_returns_zero_when_cash_cannot_buy_one_share():
    assert guard.position_size(100000, 100, 500.0) == 0


def test_position_size_returns_zero_for_bad_price():
    assert guard.position_size(100000, 100000, 0) == 0


def test_position_size_output_passes_validate_buy():
    """The sizing helper must not produce an order the guard then blocks."""
    account = {"equity": "100000", "cash": "100000", "daytrade_count": "0"}
    qty = guard.position_size(100000, 100000, 512.40)
    ok, reasons = guard.validate_buy(
        {"symbol": "LMT", "qty": str(qty), "price": "512.40", "sector": "defense"},
        account, [], 0, False)
    assert ok, reasons


def test_cli_size_prints_share_count(mem):
    import subprocess, os
    env = dict(os.environ)
    env["GUARD_STATE_PATH"] = str(mem / "state.json")
    env["GUARD_TRADES_PATH"] = str(mem / "trades.jsonl")
    out = subprocess.run(
        [sys.executable, "scripts/guard.py", "size", "--equity", "100000",
         "--cash", "100000", "--price", "500"],
        capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
    assert out.returncode == 0
    assert out.stdout.strip() == "40"
