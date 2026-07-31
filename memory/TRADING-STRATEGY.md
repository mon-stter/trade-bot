# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.
Running on an Alpaca PAPER account until proven.

## Capital & Constraints
- Starting capital: ~$100,000 (paper)
- Instruments: US stocks ONLY
- PDT: not binding — account equity is $100k, well above the $25k threshold.
  Swing-trading horizon means day trades should be rare regardless.

## Core Rules (enforced by scripts/guard.py where marked ✅)
1. NO OPTIONS — ever ✅ (guard buy-gate rejects non-stock symbols)
2. 75–85% deployed
3. 5–6 positions max, max 20% each ✅
4. Max 3 new trades per week ✅
5. Initial stop: fixed −7% GTC on every new position ✅ (guard place_buy)
6. Convert to trailing once profitable: 7% trail at +15%, 5% at +20% ✅ (guard tighten)
7. Never within 3% of current price; never move a stop down ✅ (tighten never loosens)
8. Follow sector momentum; exit a sector after 2 consecutive failed trades ✅
   (guard buy-gate blocks the sector; sells recorded via guard sell/sync)
9. Kill-switch: no new buys while halted ✅; auto-halt at −10% drawdown or −5% day ✅
10. Patience > activity

## Entry Checklist (documented before every buy)
- Specific catalyst? (must be in today's RESEARCH-LOG)
- Sector in momentum?
- Confirmed entry trigger — a pass/fail arithmetic test, not a judgement call.
  Research must name a specific level L (premarket high / breakout level /
  post-earnings reaction high). On the first full 30-min bar of the regular
  session (the bar stamped 13:30Z / 14:30Z in winter):
      CONFIRMED = bar close > L  AND  bar low >= L * 0.99
  i.e. it finished above the level, and any dip below it was a wick shallower
  than 1%. Anything else is NOT CONFIRMED — skip. An idea with no level L in
  today's research cannot be confirmed today. "Watch and see" is not a trigger.

  Why 1% and not zero: requiring the low to never break L at all is nearly
  unsatisfiable on the opening bar — backtested over Jul 16-24 across the five
  recurring watchlist names (35 name-days), a zero-tolerance rule fired once,
  which is the same never-trade failure this rule exists to fix. At 1% it fired
  9 times: it took the defense rally (LMT/NOC Jul 17, LMT/RTX Jul 20,
  LMT/RTX/NOC Jul 24) and rejected CAT on all 7 days and XOM's faded spike on
  Jul 24. A 1% wick is immaterial against a -7% stop. Caveat: 7 days is a small
  sample and the threshold was chosen with those outcomes visible — revisit it
  in weekly review once real trades exist.
- Stop level (−7% from entry)
- Target (min 2:1 R:R)

Note (added Jul 24 wk2 review): 10 straight sessions of HOLD with no trades,
several with a real catalyst + real price action (XOM breakout, defense
rally), traced back to an undefined confirmation bar. Trigger definition
above added to close that gap — no risk-rule (stop/size/frequency) changed.

Note (Jul 25 evaluation): the Jul 24 note found the right symptom but the wrong
cause. Verified against the broker: zero orders ever placed, not one. The real
cause was scheduling — market-open, the only routine able to buy, fired at 13:30Z
(9:30 ET, the opening bell), 30 minutes BEFORE the confirmation bar it depends on
closes, and midday had no buy step at all. So no entry could ever qualify, no
matter how good the setup. Fixed by moving market-open to 14:00Z (10:00 ET) and
making the trigger a two-number arithmetic check. Still no risk-rule changed —
stop %, position size, and the 3-trades/week cap remain untested and untouched.

Note (Jul 31): the Jul 25 fix was necessary but not sufficient — four more
sessions (Jul 27-30) passed with zero trades, and all four logged the same line:
"no idea named a numeric level L for today". The retiming fixed the CONSUMER
(market-open now runs after the confirmation bar exists) but nothing was ever
fixed on the PRODUCER side: pre-market was only ever asked for "catalyst + entry
+ stop + target + R:R", which it satisfied in prose — "watch for a confirmed hold
above a fresh premarket high ... if a clean level appears". A prose entry names no
number, the arithmetic test has nothing to test, and every session dead-ends. The
bot was not being cautious; it was structurally incapable of buying.

Fixed by making the producer/consumer contract explicit and machine-checked:
pre-market STEP 3b now pulls real bars and sets L from data (pre-market high /
prior-session high / post-earnings reaction high), writes one strict
`- IDEA: SYM | L=... | stop=... | target=... | rr=...:1 | sector=... | catalyst=...`
line per candidate, and self-verifies with `guard.py ideas` before committing;
market-open consumes that parsed JSON instead of re-reading prose, and alerts on
Discord if a day produces no level. Still no risk-rule changed — stop %, position
size, and the 3-trades/week cap remain untested and untouched.

An all-NO-TRADE day is still a legitimate outcome. What is not legitimate is a day
where no idea was even expressible as a number.
