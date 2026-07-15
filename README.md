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
  position/size/weekly caps, PDT room, kill-switch).
- A `-7%` stop is placed automatically on entry; reconcile sweeps catch any naked position.
- Kill-switch + drawdown/daily-loss auto-halt stop a bad day compounding.
- Market-calendar aware; runs skip holidays.
- Deterministic trade counting from `memory/trades.jsonl`.
