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
