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

## What makes this "hardened"
- Every buy is validated by `guard.py buy` before it reaches the broker (no options,
  position/size/weekly caps, PDT room when under $25k, sector loss-streaks, kill-switch).
- Buys wait for the actual fill; the `-7%` stop is anchored to the real fill price,
  and an unfilled buy is canceled (never an orphaned stop).
- Sells go through `guard.py sell` (cancels the stop first, records realized P&L);
  `guard.py sync` records broker-fired stops; `guard.py tighten` converts winners to
  trailing stops and re-asserts the old stop if a replacement fails.
- Reconcile sweeps are quantity-aware: partially covered positions get topped up.
- Kill-switch + drawdown/daily-loss auto-halt (with Discord alert) stop a bad day compounding.
- Market-calendar aware; runs skip holidays.
- Deterministic trade counting and sector streaks from `memory/trades.jsonl`.
