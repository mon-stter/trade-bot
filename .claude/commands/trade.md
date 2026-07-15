---
description: Manual trade helper with rule validation. Usage — /trade SYMBOL SHARES buy|sell
---
Args: SYMBOL SHARES SIDE. If missing, ask.
1. bash scripts/alpaca.sh quote SYMBOL  (capture ask price P)
2. For BUY: run
   python3 scripts/guard.py buy '{"symbol":"SYM","qty":"N","price":"P","thesis":"...","sector":"..."}'
   The guard validates all rules, places the buy, and sets the -7% stop.
   If it prints BLOCKED, stop and show the reason.
3. For SELL: confirm the position exists, then bash scripts/alpaca.sh close SYM.
4. Append the result to memory/TRADE-LOG.md and send bash scripts/discord.sh "<summary>".
