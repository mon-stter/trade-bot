# Hardened Autonomous Trading Bot — Design Spec

**Date:** 2026-07-15
**Status:** Approved (design), pending implementation plan
**Basis:** Nate Herk's "Opus 4.7 Trading Bot" setup guide, hardened for correctness and safety.

---

## 1. Goal & scope

Build an autonomous, cloud-scheduled trading agent on Claude Code that follows the
guide's proven architecture (stateless runs, git-as-memory, five daily routines) but
moves all "hard rules" from LLM-interpreted prose into a small, unit-tested enforcement
helper, and adds the safety systems the original lacks.

**v1 runs on an Alpaca _paper_ account.** No live capital until the strategy demonstrates
positive expectancy in paper.

### Non-goals (v1)
- Inventing a new trading strategy. We keep the guide's ruleset (swing, stocks only,
  5–6 positions, the stop/cut/tighten rules).
- Live trading.
- Backtesting infrastructure (paper trading is the validation path for v1).

---

## 2. Decisions locked in

| Decision | Choice | Rationale |
|---|---|---|
| Broker | Alpaca **paper** | Prove before risking money |
| Strategy | Guide's ruleset (baseline) | Build the system well, not a new strategy |
| Notifications | **Discord webhook** | Free, ~2-min setup, one secret |
| Research | **Native WebSearch** | Free, no extra account; citations best-effort |
| Rule enforcement | **`guard.py`** (tested Python), required by every routine | Real gate, not a guideline |
| Initial stop | **−7% fixed GTC**, convert to trailing once profitable | Continuous downside protection; resolves the guide's −7%/−10% contradiction |
| Language | Bash wrappers + Python 3 for logic (`python3` explicit) | Testable, cross-platform (Linux cloud + Windows/Git Bash local) |

---

## 3. The hardening diff (vs. guide)

1. **Real order gate.** All buys go through `guard.py buy`, which validates against live
   account state and only then places the order + protective stop. Routines never call
   raw `alpaca.sh order` for a buy. (Fixes: rules were unenforced prose.)
2. **Error visibility.** `alpaca.sh` uses `curl --fail-with-body`, so the agent can read
   Alpaca's JSON rejection reason and drive the PDT fallback ladder. (Fixes: `-f` hid bodies.)
3. **No naked positions.** `guard.py reconcile --fix` runs at market-open and midday: any
   open position lacking a protective sell order gets one. (Fixes: partial-failure leaves
   an unprotected position forever.)
4. **Circuit breaker.** `state.json` holds a kill-switch; `guard.py check-risk` auto-halts
   on a drawdown/daily-loss breach; `guard.py buy` refuses while halted. (Fixes: no
   portfolio-level stop.)
5. **Market-calendar aware.** `guard.py is-trading-day` (Alpaca `/calendar`); routines exit
   early on holidays/weekends. (Fixes: blind Mon–Fri crons.)
6. **Deterministic counting.** Weekly trade count and sector-loss streaks come from
   `trades.jsonl`, not the LLM counting markdown. (Fixes: nondeterministic gate.)
7. **Committed fallbacks.** Discord fallback writes to `memory/notifications.log` (inside
   `memory/`, added to commits) instead of an uncommitted root file. (Fixes: silent loss.)
8. **Paper first.**

---

## 4. Repository layout

```
trade-bot/
├── CLAUDE.md                 # agent rulebook (auto-loaded)
├── README.md                 # human quickstart
├── env.template              # local .env template (gitignored real .env)
├── .gitignore                # excludes .env
├── scripts/
│   ├── alpaca.sh             # trading + calendar; --fail-with-body; paper default
│   ├── discord.sh            # notifications (replaces clickup.sh)
│   └── guard.py              # enforcement helper (Python 3)
├── tests/
│   └── test_guard.py         # pytest unit tests for every rule
├── routines/                 # 5 cloud routine prompts (hardened)
│   ├── pre-market.md
│   ├── market-open.md
│   ├── midday.md
│   ├── daily-summary.md
│   └── weekly-review.md
├── .claude/commands/         # local slash commands
│   ├── portfolio.md
│   ├── trade.md
│   ├── halt.md               # NEW: set kill-switch
│   ├── resume.md             # NEW: clear kill-switch
│   └── reconcile.md          # NEW: run reconcile --fix
└── memory/
    ├── TRADING-STRATEGY.md
    ├── TRADE-LOG.md
    ├── RESEARCH-LOG.md
    ├── WEEKLY-REVIEW.md
    ├── PROJECT-CONTEXT.md
    ├── trades.jsonl          # NEW: machine-readable trade records
    ├── state.json            # NEW: kill-switch + risk state
    └── notifications.log      # NEW: committed Discord fallback
```

---

## 5. `guard.py` — enforcement helper

Single-purpose CLI. Reads live state via `alpaca.sh` (or accepts injected JSON for tests).
Every subcommand exits non-zero with a human-readable reason on failure.

| Subcommand | Behavior |
|---|---|
| `buy '<json>'` | **Only sanctioned buy path.** Validates, then places market/marketable-limit buy, waits for fill, places −7% fixed GTC stop. Appends to `trades.jsonl` + `TRADE-LOG.md`. |
| `reconcile [--fix]` | Report positions lacking a protective sell order; `--fix` places one (PDT fallback ladder). |
| `weekly-trades` | Deterministic count of buys in the current week from `trades.jsonl`. |
| `sector-streak <sector>` | Count of consecutive failed trades in a sector. |
| `halt [reason]` / `resume` / `status` | Read/write kill-switch in `state.json`. |
| `check-risk` | Compare live equity to high-water mark + week-start; auto-`halt` on breach. |
| `is-trading-day` | Alpaca `/calendar`; exit 0 if open, non-zero if closed. |

### Buy-gate checks (ALL must pass)
- Instrument is a plain US stock (reject option-style symbols / non-equity asset class).
- Position count after fill ≤ 6.
- `weekly-trades` + 1 ≤ 3.
- Cost ≤ 20% of equity.
- Cost ≤ available cash.
- PDT day-trade room available (< 3 on sub-$25k account).
- Kill-switch not active.
- (Catalyst-documented check remains an LLM responsibility, asserted in the routine.)

### Risk thresholds (tunable, defaults)
- Auto-halt if drawdown from high-water mark ≤ −10%, **or** single-day P&L ≤ −5%.
- Halt blocks new buys only; protective sells always allowed.
- Cleared manually via `/resume` (or `guard.py resume`).

---

## 6. Stop-loss mechanics (the one strategy refinement)

The guide is internally contradictory: 10% trailing stop on every position **and** cut at
−7%. Since 7% < 10%, the −7% cut fires first on a fresh position, but is only checked once
daily (midday) — leaving real intraday exposure at −10%.

**Hardened behavior:**
1. On entry, place a **fixed −7% GTC stop** (a real broker order, continuous protection).
2. Once the position is **up ≥ +15%**, replace with a **7% trailing stop**.
3. Once **up ≥ +20%**, tighten to a **5% trailing stop**.
4. Never move a stop down; never place a stop within 3% of current price.
5. Stop replacement is cancel-then-place; if the replacement fails, re-assert the old stop
   (no naked window). `reconcile --fix` is the safety net.

This preserves the guide's philosophy (hard floor when fresh, loosen when winning) while
making downside protection continuous rather than once-a-day.

---

## 7. Memory model additions

- **`trades.jsonl`** — append-only, one JSON object per trade:
  `{ "date", "symbol", "side", "qty", "price", "stop", "sector", "thesis", "target", "rr" }`.
  Machine source of truth for counts and sector streaks.
- **`state.json`** — `{ "halted", "halt_reason", "high_water_mark", "week_start_equity" }`.
- **`notifications.log`** — Discord fallback, committed.
- Human-readable `*.md` files unchanged in format; they remain the audit narrative.

All are committed by the routine that touches them (never left in the ephemeral container).

---

## 8. Wrapper scripts

- **`alpaca.sh`** — same subcommands as guide (`account`, `positions`, `position`, `quote`,
  `orders`, `order`, `cancel`, `cancel-all`, `close`, `close-all`) **plus `calendar`**.
  Uses `curl --fail-with-body -sS`. Default endpoint = Alpaca paper
  (`https://paper-api.alpaca.markets/v2`). Header translation
  (`ALPACA_API_KEY` → `APCA-API-KEY-ID`) unchanged.
- **`discord.sh`** — POST `{content: <msg>}` to `DISCORD_WEBHOOK_URL`. If unset, append to
  `memory/notifications.log` and exit 0.
- **Research** — no wrapper; routines use the native WebSearch tool directly.

### Environment variables (5 total)
```
ALPACA_API_KEY            (required)
ALPACA_SECRET_KEY         (required)
ALPACA_ENDPOINT           (optional; default paper URL)
ALPACA_DATA_ENDPOINT      (optional; default data URL)
DISCORD_WEBHOOK_URL       (required for notifications; graceful fallback if unset)
```
Same "never create a `.env` file in the cloud" discipline as the guide: cloud routines read
process env; local mode reads a gitignored `.env`.

---

## 9. Routine hardening (same 5 cron slots)

Every routine preamble: verify env vars → `guard.py is-trading-day` (exit if closed) →
`guard.py status` (respect halt) → commit-and-push discipline at the end (rebase on
conflict, never force-push).

- **Pre-market** (0 6 * * 1-5): WebSearch research → `RESEARCH-LOG.md`. Silent unless urgent;
  if `check-risk` is red, alert. Default decision: HOLD.
- **Market-open** (30 8 * * 1-5): `reconcile --fix` → `guard.py buy` per planned trade
  (gate is now real) → notify only if a trade fired.
- **Midday** (0 12 * * 1-5): `reconcile --fix` → deterministic −7% cuts + stop-tightening →
  `check-risk`. Notify only on action.
- **Daily-summary** (0 15 * * 1-5): pull final state; compute day/phase P&L; update
  high-water mark; **always** send one Discord message (≤15 lines); mandatory commit.
- **Weekly-review** (0 16 * * 5): full-week stats, grade, reset `week_start_equity`; may
  propose strategy tweaks; always send headline numbers.

Cron timezone: America/Chicago (adjust to the user's market timezone at setup).

---

## 10. Testing approach

`guard.py` is built **test-first** with pytest. Each rule gets a failing test, then the
implementing code:
- Buy gate: each rejection reason (options, over-count, over-size, over-cash, weekly cap,
  PDT, halted) + the happy path.
- `reconcile`: naked position detected and fixed; already-protected left alone.
- `check-risk`: halt triggers at threshold; no false halt below it.
- `weekly-trades` / `sector-streak`: correct counts from fixture `trades.jsonl`.
- `is-trading-day`: open vs. closed calendar responses.

Wrappers (`alpaca.sh`, `discord.sh`) are exercised via a local smoke test (`/portfolio`)
against the paper account.

---

## 11. Setup burden

Accounts/credentials the user provides:
1. Alpaca **paper** account → API key + secret.
2. A Discord channel **webhook URL**.
3. Claude GitHub App installed on the repo (for cloud push) + "allow unrestricted branch
   pushes" on each routine's environment.

Local prerequisites (Windows): Git Bash, Python 3 on PATH, curl.

---

## 12. Known residual risks (accepted for v1)

- Research quality (WebSearch, best-effort citations) still drives trade ideas.
- Only one active intraday management pass (midday); fast moves between noon and close rely
  on the broker stop. Acceptable given the anti-overtrading philosophy; a second scan can be
  added later.
- Market orders at the open carry slippage; mitigated by optional marketable-limit orders in
  `guard.py buy` (limit = ask + small buffer).
- Taxes/wash-sales are the user's responsibility (paper trading has none; relevant only if
  promoted to live).
