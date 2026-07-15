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
