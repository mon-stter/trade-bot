# Weekly Review

Friday reviews appended here (stats table, closed trades, what worked / didn't,
lessons, adjustments, letter grade A-F).

## Week ending Jul 17, 2026

### Stats
| Metric | Value |
|---|---|
| Starting portfolio (baseline) | $100,000.00 |
| Ending portfolio | $100,000.00 |
| Week return | $0.00 (0.0%) |
| S&P 500 week return | -1.6% |
| Trades (W/L/open) | 0 / 0 / 0 |
| Win rate | N/A (no trades) |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

Note: bot launched mid-week (Jul 16), so no Mon-Wed data exists; baseline = $100,000 launch equity.

### Closed Trades
| Ticker | Entry | Exit | P&L $ | P&L % | Days Held |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### Open Positions
None.

### What Worked
- No forced trades — every research session (Jul 16, Jul 17) correctly defaulted to HOLD when no idea had both a specific catalyst and a confirmed entry trigger.
- Avoided binary earnings-day risk (UNH Jul 16; TRV/TFC/FITB Jul 17) by refusing pre-print entries.
- Sidestepped the NFLX-led tech/semi selloff (Nasdaq -1.6% Thu, S&P -1.6% for the week) entirely by holding 100% cash — flat week vs. S&P's decline.
- Research log correctly flagged CAT's unexplained ~7% pullback as a reason to skip rather than dip-buy blind.
- Sector rotation thesis (industrials/energy/financials/small-caps) identified early and tracked consistently across both sessions.

### What Didn't
- Zero trades placed in the bot's first two live sessions — three ideas (CAT, XOM, UNH/financials) were flagged repeatedly but never got a confirmed trigger; can't tell yet if the entry bar is calibrated right or too strict.
- No track record yet to evaluate stop discipline, trailing-stop logic, or sector-exit rule in practice.
- XOM specifically has been "watch for breakout" two sessions running with no follow-through check on whether the breakout already happened intraday.

### Key Lessons
- First week is a launch week, not a full trading week (2 of 5 sessions) — stats are not yet meaningful for grading trade execution, only decision discipline.
- Patience paid off this week by pure luck of timing (market rotation down), but the process (require catalyst + confirmed trigger) is the right one to keep testing regardless of outcome.

### Adjustments
None — 2 sessions is too small a sample to change any TRADING-STRATEGY.md rule (rules only change after 2+ weeks proof or a bad failure). Continue as-is into week 2.

### Grade: B
Capital fully preserved, beat S&P 500 by +1.6pp this week, zero rule violations — but zero trades also means zero evidence the strategy can execute, not just avoid.

## Week ending Jul 24, 2026

### Stats
| Metric | Value |
|---|---|
| Starting portfolio (Monday baseline) | $100,000.00 |
| Ending portfolio | $100,000.00 |
| Week return | $0.00 (0.0%) |
| S&P 500 week return | -0.61% (7,457.69 → 7,411.98) |
| Trades (W/L/open) | 0 / 0 / 0 |
| Win rate | N/A (no trades) |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

### Closed Trades
| Ticker | Entry | Exit | P&L $ | P&L % | Days Held |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### Open Positions
None.

### What Worked
- Zero rule violations across all 5 sessions (Jul 20-24); every HOLD decision was documented with a specific reason in RESEARCH-LOG.md.
- Sidestepped real event risk: Thursday's tech-led rout (Mag7 -$797B, TSLA -15%, GOOGL -7%), Friday's sweeping new tariffs (99.4% of imports), and an escalating Iran/Red Sea conflict — all landed while the bot held 100% cash.
- Correctly declined to chase MMM/GM earnings gaps (Jul 21) and GEV's post-earnings drop (Jul 23) without confirmed post-open triggers — avoided binary/gap risk.
- Beat the S&P 500 by +0.61pp this week on pure capital preservation.
- Defense sector thesis (LMT/RTX/NOC) identified and tracked correctly ahead of a real 3-4% sector rally this week, even though no position was taken.

### What Didn't
- Second consecutive week, 10th consecutive session, with zero trades placed. XOM was flagged as a watchlist idea in every single session this week (and last) — 7+ sessions running — without ever getting a confirmed entry, including today when it broke out to $156.89 (+2.3%) on oil >$100/bbl.
- LMT/RTX/NOC were already-reported, already-rallying (3-4% this week) defense names with a live catalyst (Middle East escalation) — the bot never got a same-day post-open confirmation to act on despite watching for it across multiple sessions.
- Elevated-volatility days (rising VIX, Iran escalation, tariff headlines) kept pushing the decision to HOLD even when a specific name had a real catalyst and price action — reasonable individually, but the cumulative effect is a strategy that has never executed a single trade.
- Still no track record on stop discipline, trailing-stop logic, or sector-exit rules — those remain completely untested.

### Key Lessons
- Two full weeks (10 sessions) of zero trades is no longer a "launch week" artifact — it's a pattern. The entry checklist's "confirmed trigger" requirement, combined with an unusually volatile macro backdrop (Iran, tariffs, AI-capex jitters, rising yields) since day 1, has produced consistent HOLDs even on ideas with real catalysts and real price action (XOM breakout, defense sector rally).
- Capital preservation during a genuinely rough 2-week stretch (S&P -1.6% then -0.6%) is a legitimate win, but it doesn't yet prove the strategy can pull the trigger when conditions are calmer — that's still unverified.
- "Watch for post-open confirmation" has repeatedly meant no trade ever, across earnings gaps (MMM/GM), oil breakouts (XOM), and sector rallies (defense) alike — the confirmation bar as currently applied may be too vague/too strict rather than the setups being genuinely absent.

### Adjustments
- Sharpened the Entry Checklist in TRADING-STRATEGY.md to define "confirmed entry trigger" concretely (hold above a specific level for a set window) instead of the vague "watch for confirmation" language that has produced 10 straight HOLDs. This is a process/documentation clarification, not a change to any risk rule (stop %, position size, trade cap all unchanged) — those still have zero trades to prove out.
- No change to position sizing, stop, or trade-frequency rules — untested, need actual trades first.

### Grade: C+
Capital fully preserved and index-beating for a second straight week, zero rule violations — but 10 sessions with zero executions despite recurring real catalysts (XOM breakout, defense rally) means the process needs to prove it can act, not just avoid, before another B is earned.

## Week ending Jul 31, 2026

### Stats
| Metric | Value |
|---|---|
| Starting portfolio (Monday baseline) | $100,000.00 |
| Ending portfolio | $100,000.00 |
| Week return | $0.00 (0.0%) |
| S&P 500 week return | +1.05% (7,411.98 → 7,489.72) |
| Trades (W/L/open) | 0 / 0 / 0 |
| Win rate | N/A (no trades) |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

### Closed Trades
| Ticker | Entry | Exit | P&L $ | P&L % | Days Held |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### Open Positions
None.

### What Worked
- Zero rule violations across all 5 sessions (Jul 27-31); every HOLD documented with a specific reason in RESEARCH-LOG.md.
- Sidestepped real event risk while fully in cash: Wednesday's Fed-driven selloff (worst single day in over a year, hawkish 9-3 dissent, 30Y yield at an 18-year high) and the actively widening Iran-US-Egypt conflict.
- The Jul 25 scheduling fix (market-open moved 13:30Z → 14:00Z) produced its first real confirmation check this week — AMZN on Jul 31 was mechanically evaluated (bar low $262.01 < L*0.99=$264.02) and correctly rejected per the coded rule, not skipped on vague judgment. First end-to-end proof the mechanism works.
- Correctly held XOM off the watchlist all week under the earnings-blackout rule ahead of Friday's report.
- Beat the S&P 500 by +1.05pp this week on capital preservation.

### What Didn't
- Third consecutive week, 15th consecutive session, with zero trades placed — even after the scheduling bug was fixed, the one real confirmation check this week (AMZN) still failed to clear the bar.
- Stop discipline, trailing-stop logic, and the sector-exit rule remain completely untested after three full weeks live.
- Defense sector thesis (LMT/RTX/NOC) has been tracked since mid-July but never produced a fresh premarket-high level this week to even attempt a confirmation check — an idea can go stale without ever being tested by the mechanism.
- Still can't fully separate "process too strict" from "genuinely no valid setups" — this was one of the most event-dense 3-week stretches on record (Iran war escalating and de-escalating twice, Fed dissent, chip-sector rout, four Mag7 earnings prints).

### Key Lessons
- The Jul 25 scheduling fix was necessary but not sufficient on its own — it enabled the first mechanical confirmation check ever run (AMZN, Jul 31), which is real progress, but one data point cannot validate or invalidate the 1% wick threshold either way.
- Three weeks of extraordinary macro event density (two Iran ceasefire/re-escalation cycles, a credibility-questioning Fed decision, a multi-day chip-sector crash) is a genuinely hard environment to justify new risk in — that's a separate question from whether the entry bar itself is well-calibrated, and both need more live data to answer.

### Adjustments
- No change to TRADING-STRATEGY.md this week. The confirmation-bar formula (added Jul 24, scheduling bug fixed Jul 25) has now fired exactly once — too small a sample to judge per the "2+ weeks proof" rule. Continue into week 4 and reassess once several real checks have accumulated.
- No change to position sizing, stop, or trade-frequency rules — still untested, need actual trades first.

### Grade: C
Capital fully preserved and index-beating for a third straight week, zero rule violations, and the entry mechanism finally proved it can mechanically fire and reject a setup — but 15 sessions with zero executions is a pattern that needs to turn into an actual trade soon, not just a better-tested reason to keep holding.

## Week ending Aug 7, 2026

### Stats
| Metric | Value |
|---|---|
| Starting portfolio (Monday baseline) | $100,000.00 |
| Ending portfolio | $100,000.00 |
| Week return | $0.00 (0.0%) |
| S&P 500 week return | +3.58% (7,489.72 → 7,757.64) |
| Trades (W/L/open) | 0 / 0 / 0 |
| Win rate | N/A (no trades) |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

### Closed Trades
| Ticker | Entry | Exit | P&L $ | P&L % | Days Held |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### Open Positions
None.

### What Worked
- Zero rule violations across all 5 sessions (Aug 3-7); every decision documented in RESEARCH-LOG.md.
- The Jul 31 producer-side fix now works as intended: pre-market generated real, data-backed numeric levels every single day this week — 8 valid `IDEA` lines across 5 sessions (PLTR, NVDA, LLY, DIS, COP, NET, VST, ABNB), the first full week without a "no numeric level" gap.
- The STEP 0b bar-closed hard gate did exactly its job under real, repeated stress: it fired early every day and correctly blocked STEP 3/4 rather than trading on a partial, noisy bar.
- Correctly stood aside from broken or negative post-earnings reactions (AMD Aug 5, CEG/DKNG Aug 7) and stale/faded setups (AMZN Aug 4-5, PLTR Aug 5, defense all week) without a single forced entry.
- guard.py sync/reconcile ran clean every session — no unprotected positions, no halt triggered.

### What Didn't
- Market-open fired early on all 5 sessions this week (13:35-13:55 UTC, vs. the 14:00Z target set Jul 25) — the confirmation bar had not closed by the time the routine ran, so STEP 3/4 never executed once. Zero mechanical confirmation checks occurred in a week that produced 8 real candidate levels.
- First week the bot actually lags the S&P 500 instead of beating it: $0 (0.0%) vs. S&P +3.58% — the prior three weeks' "beat the index" record came against a flat-to-down tape; this week shows the real cost of the scheduling bug once the market actually moves.
- Friday's highest-conviction idea (NET, L=332.33) was never tested — the routine fired just 5 minutes early even on the fifth straight day of the same failure, showing the bug is systemic, not a one-off fluke.
- 20 consecutive sessions (4 full weeks) with zero trades placed — stop discipline, trailing-stop logic, and the sector-exit rule remain completely untested.
- The Jul 25 retiming fix has silently regressed or was never fully reliable — this week is the first hard evidence, via `bar-closed`'s own "OPEN - Nm remaining" output, that the trigger's wall-clock timing (not the strategy logic) is now the active blocker.

### Key Lessons
- The strategy's decision logic (entry checklist, confirmation arithmetic) is validated as sound and conservative — every session this week that reached STEP 3 would have run a real, defensible check. The unsolved problem is entirely upstream: the routine firing at the correct wall-clock time.
- "Zero rule violations" stops being sufficient evidence of a well-functioning bot once the market actually moves — this week proves that discipline without execution capability still produces real opportunity cost (3.58pp of missed index performance), not just a defensible zero.
- `guard.py bar-closed`'s "OPEN - Nm remaining" output is a standing diagnostic signal, not just a pass/fail gate — five straight early fires this week should have been treated as a scheduler/cron problem to escalate, not just an expected daily skip.

### Adjustments
- No change to Core Rules (stop %, position size, sector-exit, trade cap) — still zero trades to prove or disprove any of them.
- Added a note to TRADING-STRATEGY.md documenting the Aug 3-7 early-fire pattern (5/5 sessions) for the operator to fix at the scheduling/cron layer. This is outside TRADING-STRATEGY.md's scope — it's an infra trigger-timing problem, not a trading-rule problem — but leaving it undocumented risks another silent multi-week gap like Jul 24-31.

### Grade: D+
Capital fully preserved and zero rule violations, and the entry mechanism finally proved it can reliably produce real, tradeable levels every session — but the bot lagged the S&P 500 by 3.58pp in the first week the market genuinely rallied, root-caused to a scheduling trigger that blocked all 5 sessions' confirmation checks before they could even run. Discipline without execution isn't enough once "no valid setups" is no longer the excuse.
