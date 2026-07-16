import json
from pathlib import Path
import pytest


class FakeClient:
    """Stand-in for AlpacaClient. Records submitted orders; returns canned state."""

    def __init__(self, account=None, positions=None, orders=None, calendar=None,
                 fills=None, closed_orders=None):
        self._account = account or {"equity": "10000", "cash": "10000", "daytrade_count": "0"}
        self._positions = positions or []
        self._orders = orders or []
        self._calendar = calendar or []
        self._fills = list(fills or [])
        self._closed = closed_orders or []
        self.submitted = []
        self.canceled = []

    def account(self):
        return self._account

    def positions(self):
        return self._positions

    def orders(self, status="open"):
        if status == "closed":
            return self._closed
        if status == "all":
            return self._orders + self._closed
        return self._orders

    def calendar(self, start, end):
        return self._calendar

    def cancel_order(self, order_id):
        self.canceled.append(order_id)

    def submit_order(self, body):
        self.submitted.append(body)
        if self._fills:
            nxt = self._fills.pop(0)
            if isinstance(nxt, Exception):
                raise nxt
            return nxt
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
