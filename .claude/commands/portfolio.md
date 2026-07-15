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
