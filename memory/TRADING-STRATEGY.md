# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.
Running on an Alpaca PAPER account until proven.

## Capital & Constraints
- Starting capital: ~$100,000 (paper)
- Instruments: US stocks ONLY
- PDT limit: 3 day trades per 5 rolling days (account < $25k)

## Core Rules (enforced by scripts/guard.py where marked ✅)
1. NO OPTIONS — ever ✅ (guard buy-gate rejects non-stock symbols)
2. 75–85% deployed
3. 5–6 positions max, max 20% each ✅
4. Max 3 new trades per week ✅
5. Initial stop: fixed −7% GTC on every new position ✅ (guard place_buy)
6. Convert to trailing once profitable: 7% trail at +15%, 5% at +20%
7. Never within 3% of current price; never move a stop down
8. Follow sector momentum; exit a sector after 2 consecutive failed trades
9. Kill-switch: no new buys while halted ✅; auto-halt at −10% drawdown or −5% day ✅
10. Patience > activity

## Entry Checklist (documented before every buy)
- Specific catalyst? (must be in today's RESEARCH-LOG)
- Sector in momentum?
- Stop level (−7% from entry)
- Target (min 2:1 R:R)
