# Research Log

Daily pre-market research entries are appended here.

Format:
## YYYY-MM-DD — Pre-market Research
### Account
- Equity / Cash / Buying power / Daytrade count
### Market Context
- Indices / VIX / catalysts / earnings / economic calendar / sector momentum
### Trade Ideas
Every candidate gets ONE machine-readable line. Prose around them is fine, but
these lines are what market-open actually reads — an idea written only as prose
names no number, can never pass the arithmetic entry test, and is invisible to
the executor. Verify with `python3 scripts/guard.py ideas` before committing.
- IDEA: SYM | L=<num> | stop=<num> | target=<num> | rr=<num>:1 | sector=<s> | catalyst=<specific catalyst>
- NO-TRADE: SYM — <reason>
### Risk Factors
### Decision
TRADE or HOLD (default HOLD if no edge)

## 2026-07-16 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders (Day 1 of bot).

### Market Context
- VIX ~15.7, down ~5% — low, calm vol regime.
- June CPI came in cooler than expected (-0.4% m/m headline, core flat); stocks lifted early. ([Schwab](https://www.schwab.com/learn/story/stock-market-update-open))
- Fed Chair Warsh testifies before Congress today (House FSC was 7/14, Senate Banking 7/15); markets watching for rate-path signals.
- Crude oil >$80/bbl, up ~16% off recent lows after US-Iran overnight exchange and reinstated Iran oil blockade — headwind for transports/consumer, tailwind for energy. ([TheStreet](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-july-15-2026))
- Heavy earnings day: TSM, GE Aerospace, UNH, ABT, USB, NFLX, ISRG all report today/pre-open. TSM Q2 revenue +36% YoY, beat.
- Sector momentum: Healthcare and Technology leading July (+30% avg each), Consumer Cyclical +28%. Broader rotation into Industrials/Energy/Consumer Defensive (CAT, XOM, WMT) on AI-capex and oil tailwinds. ([Morningstar](https://www.morningstar.com/stocks/6-stocks-driving-2026-stock-market-rotation))

### Trade Ideas
1. CAT — industrial/AI-datacenter capex momentum tailwind, sector rotation leader. Ref ~$900. Entry needs pullback confirmation, stop -7% (~$837), target ~$1,000+ (2:1+). No fresh catalyst today — watch only.
2. XOM — energy tailwind from Iran-driven crude spike (>$80/bbl, +16% off lows). Ref ~$137. Entry on confirmed breakout, stop -7% (~$127), target ~$150 (~2:1). Catalyst is geopolitical/volatile, not a clean setup yet.
3. UNH — healthcare sector momentum leader, reports earnings today — too binary/event-risk to enter pre-print; watch reaction for a post-earnings setup instead.

### Risk Factors
- Day 1: no track record, no held positions to manage — no urgency to force a trade.
- Heavy earnings day (UNH, NFLX, TSM, GE, ABT, USB) — elevated single-name gap risk; entries into unreported names carry binary risk.
- Geopolitical: active US-Iran exchange, oil blockade — crude spike could reverse sharply or extend; avoid entries reliant solely on this catalyst until it stabilizes.
- Fed Chair Warsh testimony today — rate-path headline risk intraday.

### Decision
HOLD — Day 1, no held positions to protect, no idea meets a clean specific-catalyst + confirmed-entry setup yet (CAT/XOM lack immediate trigger, UNH has earnings-day binary risk). Patience > activity; revisit post-earnings/post-testimony reaction tomorrow.

## 2026-07-17 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. guard sync: trade log in sync, not halted.

### Market Context
- VIX futures ~16.6, calm regime, slightly up from yesterday.
- Nasdaq futures -0.3% after underlying index -1.6% Thursday; NFLX -8%+ after-hours on guidance for a second straight quarter of slowing subscriber/revenue growth. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-16/stock-market-today-dow-s-p-live-updates))
- Data today: June housing starts/permits, June industrial production, prelim July Michigan consumer sentiment. No CPI/PPI/jobs/FOMC today. ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar))
- Earnings today: Travelers (TRV), Truist (TFC), Fifth Third (FITB) — regional banks/financials focus. ([Kiplinger earnings calendar](https://www.kiplinger.com/investing/stocks/17494/next-week-earnings-calendar-stocks))
- "Great Rotation" continuing: capital moving out of mega-cap tech/semis into industrials, energy, financials, small-caps; Russell 2000 +22.6% H1 2026 (best since 1991). Energy +22% YTD. ([Morningstar](https://www.morningstar.com/stocks/6-stocks-driving-2026-stock-market-rotation), [StockCharts](https://articles.stockcharts.com/article/the-great-rotation-continues-as-financials-take-lead/))
- CAT closed $840.75 Thu (down from ~$900 ref two sessions ago, a ~6-7% pullback) — despite industrial-rotation tailwind, watch for follow-through before treating as a dip-buy. XOM ~$137.75, flat vs yesterday.

### Trade Ideas
1. TFC/FITB (regional banks) — reporting today, rotation tailwind into financials, but earnings-day binary risk — watch reaction, no pre-print entry.
2. XOM — energy rotation tailwind persists, price stable ~$137.75. Entry only on confirmed breakout above recent range, stop -7% (~$128), target ~$150 (~2:1). Still no fresh trigger today.
3. CAT — industrial rotation theme intact but stock just pulled back ~7% in a session; contradicts the "rotation tailwind" thesis short-term. Skip until it stabilizes / find catalyst for the drop.

### Risk Factors
- Tech/semi leg of the market rotating down hard (NFLX -8%, Nasdaq futures red) — broad risk-off in growth names could spill into risk appetite generally.
- CAT's overnight drop despite favorable sector theme is unexplained from search results — avoid until catalyst is clear.
- Bank earnings today (TRV, TFC, FITB) — binary risk for financials sector ideas.

### Decision
HOLD — no held positions to protect, no idea has both a specific catalyst and a confirmed entry trigger today. Rotation theme (industrials/energy/financials/small-caps) still favored for future ideas, but today's setups are either binary (bank earnings) or unconfirmed (XOM) or contradicted by price action (CAT). Patience > activity.

## 2026-07-20 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted.

### Market Context
- VIX futures ~18.8, up from ~16.6 last week — vol regime creeping higher.
- S&P futures mixed/slightly up (+0.13%), Nasdaq 100 futures +0.43%, Dow futures flat; SPX "up open" odds ~68%. 10Y yield ~4.5%, easing on softer inflation reads. ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/us-stock-market-today-p-080840351.html), [Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Top catalyst: escalating US military campaign against Iran, rising American casualties, renewed oil-supply concerns — crude-driven volatility risk elevated. ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/us-stock-market-today-p-080840351.html))
- No CPI/PPI/jobs/FOMC today (FOMC meets July 28-29, after this week) — heavy earnings week instead: 42 reports today (Domino's, W.R. Berkley, Steel Dynamics), building to 168 Thursday; TSLA reports Wed after close; GM, 3M, Halliburton, Danaher, Northrop Grumman also this week. ([Kiplinger](https://www.kiplinger.com/investing/stocks/17494/next-week-earnings-calendar-stocks), [CNBC](https://www.cnbc.com/2026/07/17/stock-market-next-week-outlook-for-july-20-24-2026.html))
- Rotation theme intact and accelerating: capital out of mega-cap tech/Nasdaq into industrials, energy, financials, small-caps. Energy +22% YTD, consumer defensive +13.3%, Russell 2000 +22.6% H1 (best since 1991). Tech had a violent Q3-open reversal after a +43.5% Q2. ([Morningstar](https://www.morningstar.com/markets/is-stock-market-rotation-underway-these-sectors-are-outpacing-tech-2026), [Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026))

### Trade Ideas
1. XOM — energy rotation + Iran-driven crude/oil-supply spike, sector momentum leader (+22% YTD). Ref ~$137-138. Entry only on confirmed breakout above recent range, stop -7% (~$128), target ~$152 (~2:1). Catalyst still geopolitical/volatile — no clean trigger yet, third session watching without confirmation.
2. Small-cap industrial (e.g. Russell 2000 constituent in AI-capex/reshoring theme) — rotation tailwind strongest of the year (R2K +22.6% H1). No single name identified with a specific catalyst yet; needs a screen before sizing an entry.
3. Regional bank/financial — rotation into financials continuing, earnings season underway (KeyCorp, Synchrony this week). Binary earnings-day risk — watch reactions, no pre-print entry.

### Risk Factors
- Iran conflict escalation + oil supply risk = elevated headline/gap risk across the board, not just energy.
- VIX drifting up (15.7 -> 16.6 -> 18.8 over 3 sessions) — rising vol regime, size and timing need more confirmation than usual.
- Heavy earnings week — single-name gap risk high; avoid entries into unreported names.
- Tech reversal could spill into broad risk appetite even for rotation beneficiaries.

### Decision
HOLD — no held positions to protect, no idea has a confirmed entry trigger yet (XOM still lacks breakout confirmation, small-cap idea lacks a specific name/catalyst, financials are binary on earnings). Rising VIX and active Iran conflict argue for extra patience. Patience > activity.

## 2026-07-21 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~17.6, down from ~18.8 Monday — vol easing but still elevated vs last week's ~15.7. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures up on peace-talk hopes: Dow +166pts (+0.3%), S&P futures +0.6%, Nasdaq 100 futures +1.4%. Chips rebounding after last week's selloff. ([CNBC](https://www.cnbc.com/2026/07/20/stock-market-today-live-updates.html), [Schwab](https://www.schwab.com/learn/story/stock-market-update-open))
- Top catalyst: US-Iran situation whipsawing — deal declared void July 15 after US strikes, now Iran signaling openness to resume diplomacy; oil steady but Red Sea shipping risk flagged. Headline risk remains high and erratic. ([Schwab](https://www.schwab.com/learn/story/stock-market-update-open))
- 10Y yield ~4.52%, easing on cooler inflation data. No CPI/PPI/jobs/FOMC this week (FOMC meets July 28-29) — lighter macro calendar. ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar))
- Heavy earnings week: MMM and GM beat and reported pre-open today (MMM premarket +7%, GM premarket +2%); NOC also reports today. TSLA, GOOGL, IBM report later this week. 87% of ~54 S&P 500 reporters so far have beaten on EPS. ([Benzinga](https://www.benzinga.com/markets/prediction-markets/26/07/60569710/sp500-july-21-open-up-or-down-polymarket-iran-ceasefire-oil-earnings-ai))
- Rotation theme intact: capital continuing out of mega-cap tech into industrials, energy, financials, small-caps; Russell 2000 led H1 (+22.6%), energy +22% YTD, tech showing fatigue after +43.5% Q2. ([Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026), [Morningstar](https://www.morningstar.com/markets/is-stock-market-rotation-underway-these-sectors-are-outpacing-tech-2026))

### Trade Ideas
1. MMM — industrial rotation leader, Q2 beat, premarket +7%. Ref pre-market ~$182 (prior close ~$170). Entry only if it holds the gap and confirms above pre-market high after open, stop -7% (~$169), target ~$200 (~2:1). Big gap — chasing pre-confirmation is exactly what the rules warn against; watch for hold, not print.
2. GM — industrial/rotation beneficiary, Q2 beat, premarket +2%. Ref pre-market ~$52. Entry on confirmed breakout above premarket high, stop -7% (~$48), target ~$58 (~2:1). Smaller gap than MMM, less binary, but still needs open confirmation.
3. XOM — energy rotation still a theme but oil steady, no fresh breakout trigger; fourth session watching, no confirmed entry. Drop from active watchlist unless a new catalyst appears.

### Risk Factors
- Iran situation erratic (deal void → peace-talk hopes in days) — headline risk can reverse gains fast; avoid sizing into gap-driven moves tied to it.
- Heavy earnings week (NOC today, TSLA/GOOGL/IBM later) — single-name and index-level gap risk elevated.
- MMM/GM both gapped on earnings pre-open — chasing an unconfirmed gap violates entry-checklist discipline; need post-open confirmation, not pre-market print.
- VIX still above last week's low, regime not fully calm.

### Decision
HOLD — no held positions to protect. MMM/GM have real catalysts (earnings beats + rotation tailwind) but no confirmed entry yet pre-open; XOM has gone stale. Will watch MMM/GM for post-open hold/breakout confirmation before any buy. Patience > activity.

## 2026-07-22 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~17.4, up ~2% — vol ticking up again on Iran headline risk. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures red: S&P -0.3%, Dow -0.1%, Nasdaq-100 -0.7%; Polymarket pricing only ~15% odds of a green S&P open. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-wednesday-july-22-dow-sp-500-nasdaq-alphabet-tesla-083644887.html), [Benzinga](https://www.benzinga.com/markets/prediction-markets/26/07/60599715/sp500-july-22-open-up-or-down-polymarket-oil-fed-earnings-ai-stocks))
- Top catalyst: Trump played down near-term Iran talks and threatened broader strikes (incl. a suspected nuclear site) plus Red Sea shipping threats — Brent ~$92, WTI >$85. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-21/latest-oil-market-news-and-analysis-for-july-22))
- Tariff watch: Section 122 import surcharge deadline July 24 — fresh tariff headlines weighing on futures alongside oil. (Yahoo Finance, above)
- No CPI/PPI/jobs/FOMC today (FOMC meets July 28-29) — but huge earnings catalyst: GE Vernova (GEV) reports before open (options pricing an 11.5% swing, stock +62% YTD); Tesla (TSLA) and Alphabet (GOOGL) report after close today, kicking off Big Tech earnings — index-moving event risk into tomorrow's open. ([Benzinga](https://www.benzinga.com/markets/earnings/26/07/60592947/tesla-earnings-could-move-83-billion-in-market-value), [Yahoo Finance GEV](https://finance.yahoo.com/markets/stocks/articles/ge-vernovas-next-earnings-report-131225168.html))
- Rotation theme intact: financials/energy/industrials/small-caps continuing to draw inflows out of mega-cap tech; Russell 2000 +22.6% H1 (best since 1991), energy benefiting from stabilized-to-rising crude. ([Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026), [Morningstar](https://www.morningstar.com/markets/is-stock-market-rotation-underway-these-sectors-are-outpacing-tech-2026))

### Trade Ideas
1. XOM — energy rotation tailwind + fresh Iran-driven crude spike (Brent ~$92, WTI >$85), most concrete catalyst of the week for this name. Ref ~$138. Entry only on confirmed breakout above recent range, stop -7% (~$128), target ~$152 (~2:1). Fifth session watching — still no breakout confirmation; oil move is real but headline-driven and reversible.
2. GEV — industrial/AI-power-buildout theme, reports before open with large expected move (options implying 11.5% swing). Pure binary earnings-day risk — no pre-print entry; watch post-earnings reaction for a possible momentum setup tomorrow.
3. Broad market — futures red across the board (S&P -0.3%, Nasdaq -0.7%) ahead of TSLA/GOOGL after close tonight; any new position today carries overnight event risk into tomorrow's gap regardless of sector. Favor waiting for post-earnings clarity before sizing anything new.

### Risk Factors
- Iran escalation (strike threats incl. nuclear site, Red Sea shipping risk) driving oil and weighing on futures — headline risk can reverse or extend violently, avoid entries reliant solely on the oil spike.
- TSLA + GOOGL earnings after close tonight are index-moving; any position opened today is exposed to a large overnight gap risk tomorrow.
- GEV reporting before open with market pricing a double-digit swing — binary, avoid pre-print.
- Tariff deadline (Section 122 surcharge, July 24) adds a second source of headline risk this week.
- VIX ticking back up (~17.4) after easing — regime not calm.

### Decision
HOLD — no held positions to protect, no idea has a confirmed entry trigger, and today carries unusually high event risk (TSLA/GOOGL after close, GEV before open, active Iran escalation, tariff deadline in 2 days). Patience > activity; reassess post-earnings tomorrow.

## 2026-07-23 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $100,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~17.8, up ~7% — vol regime rising again on yields + energy. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures slightly lower: S&P -0.14%, weighed by rising yields and energy jitters. 10Y yield ~4.63%, near a two-month high. ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/us-stock-market-today-p-081301441.html))
- Energy: surprise US crude inventory build of 2.6M barrels; emergency reserves at 43-year low — mixed signal, adds oil-price uncertainty.
- No CPI/PPI/jobs/FOMC confirmed for today specifically (FOMC meets July 28-29, next week); heavy earnings day instead — 166 companies reporting. Notable: Intel (after close), Honeywell (before open), Blackstone (before open), RTX, T-Mobile, Thermo Fisher, Union Pacific, Lockheed Martin. ([Earnings Whispers](https://www.earningswhispers.com/calendar/20260723/1), [Kiplinger](https://www.kiplinger.com/investing/stocks/17494/next-week-earnings-calendar-stocks))
- Overnight: TSLA -3.8% after Q2 profitability miss; GOOGL -4%+ after raising 2026 capex guidance to $195-205B despite a revenue beat — both weigh on Nasdaq futures/tech sentiment this morning. ([CNBC](https://www.cnbc.com/2026/07/22/stocks-making-the-biggest-moves-after-hours-googl-tsla-ibm-lvs.html))
- GEV fell ~6% yesterday despite raising FY26 guidance to ~$46B (from $45B) — EPS missed ($2.47 vs $3.10 est); some retail pushback calling the drop an overreaction, but price action is negative. ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/gev-stock-drops-q2-earnings-121410119.html))
- Rotation theme intact: capital continuing out of mega-cap tech into small-caps/industrials/energy/financials. Russell 2000 +22.6% H1 (best since 1991); financials drawing inflows into bank earnings season; industrials (aerospace/defense/grid) benefiting from AI-linked physical buildout; energy supported by firm crude. ([Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026), [Morningstar](https://www.morningstar.com/markets/is-stock-market-rotation-underway-these-sectors-are-outpacing-tech-2026))

### Trade Ideas
1. LMT/RTX (defense/industrials) — reporting today, rotation tailwind into industrials/defense, AI-linked infra buildout theme. No pre-print entry; watch post-earnings reaction for a confirmed breakout, stop -7%, target ~2:1 if a clean setup emerges.
2. UNP (industrials, rail) — reports today, rotation-favored sector. Binary earnings-day risk — no pre-print entry; watch for post-open confirmation only.
3. GEV — post-earnings pullback (~6% down) despite raised guidance; could set up a mean-reversion/dip-buy if it stabilizes and reclaims a level, but no confirmed trigger yet and thesis (over-reaction) is unproven. Watch, don't chase.
4. XOM — sixth session on watchlist with no breakout confirmation despite firm energy rotation tailwind; dropping from active list until a fresh catalyst or clean trigger appears.

### Risk Factors
- TSLA/GOOGL both down post-earnings — Nasdaq/tech sentiment soft into the open, could spill into broad risk appetite.
- Heavy earnings day (166 reports) — high single-name gap risk; avoid entries into unreported/just-reported names without post-open confirmation.
- Rising 10Y yield (~4.63%, 2-month high) — headwind for equity valuations broadly, especially rate-sensitive growth names.
- Oil/energy signals mixed (crude inventory build vs. low reserves) — no clean directional edge for XOM/energy right now.
- VIX up ~7% this morning — vol regime firming, warrants extra caution on sizing.

### Decision
HOLD — no held positions to protect. No idea has a confirmed entry trigger pre-open; earnings reactions (LMT, RTX, UNP) need post-open confirmation, GEV dip-buy thesis is unconfirmed, XOM has gone stale after six sessions. Rising yields and firming VIX argue for patience. Patience > activity.

## 2026-07-24 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~18.9, up ~1% — elevated after Thursday's selloff, highest level in weeks. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures attempting tentative recovery: Dow +0.5%, S&P +0.2%, Nasdaq-100 +0.1%, after Thursday's rout. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-friday-july-24-dow-sp-500-nasdaq-081854465.html))
- Major event: new 10–12.5% tariffs on 60 countries (Section 301) took effect 12:01am ET today, covering ~99.4% of US imports (fuel/food/fertilizer/autos/metals/pharma exempt). ([Yahoo Finance](https://finance.yahoo.com/economy/policy/article/trump-announces-next-phase-of-global-tariffs-affecting-994-of-us-imports-210032314.html), [Benzinga](https://www.benzinga.com/news/politics/26/07/60658332/trump-hits-60-countries-with-10-to-12-5-tariffs-as-temporary-levies-expire))
- Thursday was the worst day in a month: S&P -0.8/-1.2%, Nasdaq-100 -1.9%, Mag7 lost ~$797B in market cap, TSLA -15% and GOOGL -7% on AI-capex/debt-sustainability fears (GOOGL raised 2026 capex guide to $195-205B). ([Motley Fool](https://www.fool.com/coverage/stock-market-today/2026/07/23/stock-market-today-july-23-tesla-drops-15-leading-tech-stock-slide/), [Bloomberg](https://www.bloomberg.com/news/articles/2026-07-23/tech-bonds-hit-by-selloff-as-ai-debt-fears-race-through-markets))
- Middle East: oil pushed above $100/bbl (Brent, first time in 2 months) after Houthi attacks on Saudi tankers in the Red Sea; Trump threatening "major military punishment" and reportedly considering a "massive attack" on Iran. Jordan/Kuwait reported incoming Iranian fire. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-23/latest-oil-market-news-and-analysis-for-july-24), [CNN](https://www.cnn.com/2026/07/23/world/live-news/iran-war-trump))
- 10Y yield ~4.67%, a 52-week high — oil-driven inflation fears pressuring bonds and adding to equity valuation headwinds. FOMC meets next week (Jul 28-29) — event risk building. No CPI/PPI/jobs today.
- Earnings before the bell today: VZ, AXP, NEE, CHTR, SLB, CNI, HCA, and others (166-name week continuing). ([Earnings Whispers](https://www.earningswhispers.com/calendar/20260724/1))
- Rotation theme intact and reinforced: capital continuing out of mega-cap tech (AI-capex jitters) into industrials/energy/defense/financials/small-caps. Defense names (NOC +4%, LMT +3.6%, RTX +3.3%) rallying on Middle East escalation and raised FY26 guides. ([Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026), [TipRanks](https://www.tipranks.com/news/major-defense-stocks-surge-amid-middle-east-tensions))

### Trade Ideas
1. XOM — energy rotation + oil >$100/bbl (first time in 2 months), breaking above the range it has stalled in for 7+ sessions. Trading ~$156.89 (+2.3%). Entry only on confirmed hold above premarket high after open, stop -7% (~$146), target ~$172 (~2:1). Reports Q2 earnings July 31 — avoid holding through that print or size down heading into it.
2. LMT/RTX/NOC (defense) — Middle East escalation intensifying (Red Sea attacks, threatened broader Iran strikes) plus raised FY26 guidance already reported this week; sector up 3-4% this week on the combined tailwind. No pre-print entry needed (already reported) — watch for post-open continuation/hold above recent highs before entering, stop -7%, target ~2:1.
3. Broad market — Thursday's rout (Mag7 -$797B, TSLA -15%, GOOGL -7%) plus today's sweeping new tariffs (99.4% of imports) stack two live shocks on top of active Iran escalation. Futures green but tentative. Avoid broad-market or momentum-chasing entries until the tape shows a clean post-open direction; favor standing aside on non-sector-specific ideas today.

### Risk Factors
- Iran/Red Sea conflict escalating and unpredictable — Trump weighing a "massive attack" on Iran; oil could spike further or reverse hard on any de-escalation headline. Avoid sizing purely on the oil spike.
- New tariffs covering 99.4% of imports just took effect — inflation/growth impact still being priced in, added uncertainty on top of Thursday's selloff.
- AI-capex/debt-sustainability fears (GOOGL/TSLA) could keep pressuring mega-cap tech and spill into broad risk appetite.
- 10Y yield at a 52-week high (4.67%) — headwind for equity valuations broadly, especially growth/rate-sensitive names.
- VIX ~18.9, elevated after worst session in a month — warrants smaller size and tighter discipline on any new entry.
- FOMC meets July 28-29 next week — event risk building into next week.

### Decision
HOLD — no held positions to protect. Two live shocks (new tariffs + Iran escalation) stacked on Thursday's tech-led selloff make today unusually high-risk for new sizing; no idea has a confirmed post-open entry trigger yet. XOM and defense names have real catalysts worth watching for confirmation on a calmer tape. Patience > activity.

## 2026-07-27 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~17.6, calm — below last week's levels after the weekend ceasefire news. ([Investing.com](https://www.investing.com/indices/volatility-s-p-500))
- Futures sharply higher: S&P +0.8%, Dow +0.8%, Nasdaq-100 +1.6% — entering "busiest week of the quarter" (Big Tech earnings + Fed decision). ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-monday-july-27-dow-sp-500-nasdaq-080412540.html))
- Top catalyst: US and Iran paused fighting over the weekend, raising hopes for a durable de-escalation after two weeks of strikes. Oil collapsed on the news — Brent -7.3% to ~$89.73, WTI -6.5% to ~$83.47, second straight down day after Friday's -3.9%; Brent was above $100 just last week. ([CNBC](https://www.cnbc.com/2026/07/27/oil-price-wti-brent-slide-as-iran-reportedly-may-halt-attacks.html), [US News](https://www.usnews.com/news/business/articles/2026-07-26/oil-prices-ease-after-us-and-iran-pause-their-attacks))
- Economic calendar: FOMC meets Jul 28-29, decision + Fed Chair Kevin Warsh press conference Wednesday — CME FedWatch prices ~64% odds of a hold. No CPI/PPI this week (next CPI print Aug 12); weekly jobless claims and PCE (Fed's preferred inflation gauge) also due. ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar))
- Earnings: light today (Nucor before open); the week's real event risk is MSFT/META Wednesday and AAPL/AMZN Thursday — all four land right alongside the FOMC decision. ([Earnings Whispers](https://www.earningswhispers.com/calendar), [Yahoo Finance](https://finance.yahoo.com/markets/article/4-big-tech-earnings-reports-a-fed-meeting-and-100-oil-its-the-busiest-week-of-the-quarter-100000261.html))
- XOM: reports Q2 earnings Friday Jul 31; Q2 net income tracking ~$15.7-15.9B (~3x Q1) on the oil spike + refining-margin recovery — but that windfall was priced during the now-reversing oil rally. ([StocksToTrade](https://stockstotrade.com/news/exxonmobil-holdings-corporation-xom-news-2026_07_13/))
- Rotation: energy/defense/industrials tailwind of the last two weeks was largely escalation- and oil-driven; today's ceasefire and oil collapse directly undercut that catalyst. No fresh read yet on whether capital rotates back to mega-cap tech ahead of Wed/Thu earnings.

### Trade Ideas
1. XOM — catalyst (oil >$100, energy rotation) reversed overnight: Brent -7.3%/WTI -6.5% on the Iran ceasefire, and the name reports earnings this Friday (Jul 31). No entry — thesis broken and earnings-week blackout applies. Drop from watchlist.
2. LMT/RTX/NOC (defense) — this week's rally was escalation-driven; the ceasefire pause removes the near-term catalyst, so no new entry. Watch only for a confirmed post-open hold if the ceasefire cracks and headlines re-escalate; otherwise stand aside.
3. Broad market / mega-cap tech — futures up 0.8-1.6% on ceasefire relief, but FOMC (Wed) and MSFT/META/AAPL/AMZN earnings (Wed/Thu) stack directly on top of this rally. Any breakout entry now would run straight into that event cluster before an exit could react. No pre-event entry; reassess post-FOMC/earnings for a confirmed trigger, stop -7%, target 2:1 minimum.

### Risk Factors
- Iran-US ceasefire is a fragile pause, not a resolved conflict — any breakdown could re-spike oil and reverse today's relief rally intraday.
- FOMC Wed: even at ~64% hold odds, a hawkish surprise or Warsh press-conference misstep could move the whole tape sharply.
- MSFT/META (Wed) and AAPL/AMZN (Thu) are index-moving; last Thursday's AI-capex fear (TSLA -15%, GOOGL -7%) shows single-name misses can spill into broad risk-off.
- Oil's sharp reversal invalidates the energy/defense rotation catalyst that has anchored the watchlist for two weeks — those ideas need a fresh catalyst, not just old momentum, before re-entry.
- Entering anything new today means holding through FOMC and/or Big Tech earnings within 1-3 days — event risk is unusually concentrated this week.

### Decision
HOLD — no held positions to protect. Ceasefire relief is genuine good news but lands directly ahead of FOMC (Wed) and four Big Tech earnings prints (Wed/Thu); XOM and defense theses both broke overnight as oil reversed. No idea has a confirmed entry trigger, and this week's event stacking argues for extra patience regardless. Reassess post-FOMC/earnings. Patience > activity.

### Execution (market-open)
- No idea named a level L for today (XOM: thesis broken/earnings blackout; defense: catalyst removed by ceasefire; broad market: no pre-event entry) — confirmation bar not applicable, no tickers checked.
- Result: no trades

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-07-28 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~19.0, up ~1.7% — highest in weeks, chip-driven risk-off. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures red, tech-led: Nasdaq-100 futures -0.9%, S&P futures -0.2%. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-tuesday-july-28-dow-sp-500-nasdaq-082832371.html))
- Top catalyst: Asian memory-chip rout — Samsung -13.4% (worst day in ~20 yrs), SK Hynix -14.7%, KOSPI -10.8% (biggest drop since the March Iran conflict), on AI-infrastructure-financing worries + rising China competition. Spilling into US premarket: NVDA -1.2%, INTC/AMD >-3%, MU -5%. ([CNBC](https://www.cnbc.com/2026/07/28/sk-hynix-plunges-semiconductor-selloff-deepens-samsung-softbank.html), [CNBC Daily Open](https://www.cnbc.com/2026/07/28/daily-open-ai-boom-chip-selloff-sk-hynix.html))
- FOMC decision Wed Jul 29, 2pm ET — fed funds expected to hold at 3.50-3.75% (~65% odds via CME FedWatch); no SEP/dot plot this meeting; September hike odds already ~82% per some analysts. Chair Warsh has dropped traditional forward guidance, adding uncertainty. ([CME Group](https://www.cmelitegroup.com/knowledge-hub/fomc-meeting-fed-decision-day/), [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262054021-july-fomc-fed-oil-us-oil-tradingkey))
- Earnings: MSFT + META report Wed (alongside FOMC); AAPL + AMZN report Thu (alongside June core PCE); KO/BA/F also this week. Mag7 capex (~$724B 2026, ~$950B 2027 combined) is the swing factor markets are fixated on. ([TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262054300-weekly-preview-fed-apple-microsoft-meta-amazon-earnings-reports-tradingkey), [Fortune](https://fortune.com/2026/07/26/big-tech-earnings-meta-microsoft-apple-amazon-market-revolt-ai-spending/))
- Rotation theme intact: industrials/energy/consumer-defensive continuing to outperform (energy +22% YTD, industrials led by defense/grid-buildout); small-caps +21% YTD despite still trading at a historic discount to S&P. Today's chip rout reinforces the out-of-mega-cap-tech flow. ([Intellectia](https://intellectia.ai/blog/market-rotation-beyond-magnificent-7-july-2026), [AlphaBetaStock](https://alphabetastock.com/sector-rotation-industrials-energy-tech-narrowing-2026/))

### Trade Ideas
1. LMT/RTX/NOC (defense/industrials) — today's tech/chip rout could reinforce the rotation into defense/industrials, but the Iran ceasefire (holding since Jul 26-27) already removed the escalation catalyst that drove last week's rally; no fresh catalyst today. No pre-print entry — watch only for a confirmed post-open hold above recent highs if flows rotate here; stop -7%, target 2:1.
2. XOM — thesis still broken (oil reversed hard last week on the ceasefire) and Q2 earnings land Friday Jul 31 — earnings blackout applies. No entry, stay off watchlist.
3. Broad market / mega-cap tech (MSFT/META/AAPL/AMZN, NVDA/semis) — no entry of any kind. FOMC decision Wed + two of four Mag7 prints Wed, other two Thu, stacked directly on top of today's AI-financing-driven chip selloff. Any position (long or short) opened today holds through the single highest event-risk 48 hours of the summer. Wait for post-FOMC/post-earnings clarity.

### Risk Factors
- AI-infrastructure-financing fears (chip rout, Samsung/SK Hynix worst days in years) could keep spilling into US semis/mega-cap tech and broad risk appetite through the week.
- FOMC Wed 2pm ET — even at ~65% hold odds, Warsh has dropped forward guidance, raising surprise risk; September-hike odds already elevated per some desks.
- MSFT/META (Wed) + AAPL/AMZN (Thu) are index-moving; last week's TSLA -15%/GOOGL -7% reaction shows single-name AI-capex misses can trigger broad selloffs.
- VIX ~19, highest in weeks — regime not calm, argues for smaller size/no size this week.
- No held positions to protect currently, but event stacking (FOMC + 4 Mag7 prints in 2 days) makes this an unusually poor week to initiate new risk regardless of setup quality.

### Decision
HOLD — no held positions to protect. No idea has a confirmed entry trigger, defense/industrials catalyst is stale (ceasefire removed it), XOM is earnings-blackout, and initiating anything into mega-cap tech/semis right before FOMC (Wed) and four Big Tech prints (Wed/Thu) violates the "no pre-event entry" principle regardless of setup. Reassess post-FOMC/post-earnings later this week. Patience > activity.

### Execution (market-open)
- No idea named a level L for today (defense/industrials: catalyst stale post-ceasefire; XOM: earnings blackout; broad market/mega-cap tech: no pre-event entry ahead of FOMC + Mag7 prints) — confirmation bar not applicable, no tickers checked.
- Result: no trades

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-07-29 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~18.9, elevated but roughly flat overnight — still highest-in-weeks regime from the chip selloff. ([Investing.com](https://www.investing.com/indices/volatility-s-p-500))
- Futures steadying: S&P +0.2%, Nasdaq-100 ~flat — but Nasdaq-100 sits on the brink of a technical correction after a 4th straight day of chip losses. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-wednesday-july-29-dow-sp-500-nasdaq-082009165.html))
- Major overnight escalation: the Iran-US ceasefire broke — Iran (IRGC) launched a surprise ballistic-missile attack on US forces in the Middle East; Jordan intercepted 5 missiles, US/Saudi forces struck Iran-linked PMF sites in Iraq in response. Reverses Sunday-Monday's de-escalation. ([CNN](https://www.cnn.com/2026/07/29/world/live-news/iran-trump-news), [OPB](https://www.opb.org/article/2026/07/28/the-us-says-it-thwarted-an-iranian-missile-attack-that-ended-a-brief-pause-in-fighting/))
- Oil jumped on the renewed attack: Brent +3.4% to ~$86.97, WTI +3.6% to ~$82.09, bouncing off Tuesday's brief-calm low (~$84) but still well below last week's >$100 escalation peak. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-28/latest-oil-market-news-and-analysis-for-july-29))
- FOMC decision today 2pm ET (Chair Warsh press conference) — rates expected to hold at 3.50-3.75% (~62-65% odds per CME FedWatch/Polymarket); Warsh has dropped traditional forward guidance, raising surprise risk. ([CME Group](https://www.cmelitegroup.com/knowledge-hub/fomc-meeting-fed-decision-day/), Polymarket)
- Big Tech earnings after close today: Microsoft (MSFT, est. $4.24 EPS / $87.63B rev) and Meta (META, est. $7.18 EPS / $60.22B rev, capex guide already raised to $125-145B) plus Qualcomm — both ~95% beat odds priced in, so FY27 capex commentary is the real stock-mover. ([TipRanks](https://www.tipranks.com/news/big-tech-earnings-showdown-meta-and-microsoft-in-focus-ahead-of-july-29-earnings-report), [Benzinga](https://www.benzinga.com/markets/options/26/07/60741589/microsoft-could-swing-189-billion-in-value-after-earnings))
- Semiconductor selloff extending to a 4th straight day: NVDA, MU, AMD, INTC, SNDK all lower pre-market; SMH ETF down >3%, pressured by SK Hynix's guidance miss despite record results and Nvidia losing its title as most-valuable company to Apple amid AI-financing concerns (report of NVDA backstopping $250B OpenAI-linked data-center funding). ([TipRanks](https://www.tipranks.com/news/semiconductor-stocks-nvda-amd-micron-and-sndk-extend-their-sell-off-in-pre-market-today-july-29-what-triggered-the-latest-slide))
- Rotation theme intact: energy (+21-22% YTD) and industrials (+12% YTD, defense/grid-buildout led) continuing to outperform mega-cap tech, which remains under AI-capex-financing pressure. ([AlphaBetaStock](https://alphabetastock.com/sector-rotation-industrials-energy-tech-narrowing-2026/))

### Trade Ideas
1. LMT/RTX/NOC (defense/industrials) — renewed Iran attack directly reignites the escalation catalyst that drove last week's 3-4% rally in these names. No pre-print entry; watch for a confirmed post-open hold above premarket high, stop -7%, target ~2:1 if a clean level forms today.
2. XOM — oil bounce (+3.4-3.6%) is escalation-driven and reversible, and the name still reports Q2 earnings this Friday Jul 31 — earnings-blackout applies. No entry, stay off watchlist.
3. Broad market / mega-cap tech / semis — no entry of any kind. FOMC (2pm ET) + MSFT/META/QCOM earnings after close stack directly on top of a 4th-day chip selloff and a fresh Iran-US military escalation. Any position opened today holds through the single highest event-risk window of the week. Wait for post-FOMC/post-earnings clarity.

### Risk Factors
- Iran-US conflict reignited overnight (ceasefire broken, missiles intercepted, retaliatory strikes in Iraq) — unpredictable, could escalate further intraday and whipsaw oil/risk sentiment either direction.
- FOMC 2pm ET — even at ~62-65% hold odds, Warsh has dropped forward guidance, raising surprise-move risk on the decision and press conference.
- MSFT/META/QCOM earnings after close — capex guidance is the real swing factor; last week's TSLA -15%/GOOGL -7% reaction shows AI-capex commentary can trigger broad tech selloffs.
- Semiconductor selloff now 4 sessions running, Nasdaq-100 near correction — could keep dragging broad tech/risk sentiment through the session.
- VIX ~18.9, still elevated — regime not calm, warrants smaller size/no size today regardless of setup.

### Decision
HOLD — no held positions to protect. No idea has a confirmed entry trigger pre-open. Today stacks a reignited Iran-US military conflict, the FOMC decision (2pm ET), and MSFT/META/QCOM earnings after close directly on top of a 4th-day chip selloff — the highest event-risk combination of the week. Defense/industrials (LMT/RTX/NOC) is worth watching for a confirmed post-open reaction to the Iran news; everything else stays off-limits until after FOMC/earnings clarity. Patience > activity.

### Execution (market-open)
- No idea named a numeric level L for today (LMT/RTX/NOC: "if a clean level forms today" — no level set; XOM: earnings blackout; broad market/tech: no pre-event entry ahead of FOMC + MSFT/META/QCOM) — confirmation bar not applicable, no tickers checked.
- Result: no trades

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-07-30 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~19.4, down ~6% overnight but still elevated after Wednesday's spike. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures rebounding: S&P +0.3-0.4%, Dow +0.2%, Nasdaq-100 +0.7%, as markets try to steady ahead of inflation data. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-thursday-july-30-dow-sp-500-nasdaq-082255995.html))
- FOMC (Wed 2pm ET): Fed held rates 3.50-3.75% but on an unusually split 9-3 vote — Hammack, Kashkari, and Logan all dissented in favor of a hike. Warsh's shorter, guidance-light statement raised credibility questions; 30Y Treasury yield spiked to its highest since 2007. Dow fell ~1,100 points Wednesday, its worst day in over a year. ([CNBC](https://www.cnbc.com/2026/07/29/fed-rate-decision-july-2026.html), [CNBC](https://www.cnbc.com/2026/07/29/kevin-warsh-fed-treasury-yields-inflation-credibility-interest-rates.html))
- Iran conflict re-escalated further overnight: after Tuesday's intercepted Iranian missile attack, the US completed retaliatory strikes on Iran; Trump says "it's our turn" and has vowed to "hit them very hard" again. Highly fluid, headline-driven. ([CNN](https://www.cnn.com/2026/07/29/world/live-news/iran-trump-news))
- Big Tech earnings (after Wed close): Microsoft beat and raised, capex +70% to $41B, shares +2.4% AH. Meta missed badly — EPS $6.18 vs $7.22 est, net income -14% YoY, capex guide raised to $130-145B — shares -6.2% AH. Mixed signal for mega-cap tech open. ([CNBC](https://www.cnbc.com/2026/07/29/microsoft-aces-earnings-call-while-meta-frustration-grows-do-we-just-need-to-be-a-bit-more-patient.html))
- Econ calendar today: Core PCE (Fed's preferred inflation gauge, ~8:30am ET, est. +0.1-0.2% MoM / ~3.3% YoY), Q2 GDP (est. +2.3%), and weekly jobless claims — all landing pre-open, could move rates/tape sharply. ([Investing.com](https://www.investing.com/news/stock-market-news/core-pce-price-index-gdp-and-jobless-claims-due-thursday-93CH-4821457))
- Defense (LMT/RTX/NOC): all three posted record backlogs and raised FY26 guidance last week (book-to-bill 2.4-3.2x) — strong fundamentals, but that catalyst is now several sessions old and largely priced; renewed Iran-US strikes could reignite momentum. ([Foreign Policy Journal](https://www.foreignpolicyjournal.com/2026/07/26/lockheed-martin-nyse-lmt-rtx-nyse-rtx-and-northrop-grumman-nyse-noc-post-record-backlogs-raise-guidance-after-q2-results/))
- XOM: still on earnings blackout, reports Q2 tomorrow (Fri Jul 31, consensus EPS ~$3.68-3.88). ([Alphastreet](https://news.alphastreet.com/exxon-mobil-xom-q2-2026-preview-eps-est-3-68-reports-july-31/))

### Trade Ideas
1. LMT/RTX/NOC (defense) — record backlogs/raised guidance from last week plus fresh Iran-US strikes overnight could reignite the rally, but no new pre-market catalyst level has formed since last week's earnings pop. No pre-open entry; watch for a confirmed post-open hold above a fresh premarket high, stop -7%, target ~2:1 if a clean level appears.
2. XOM — earnings blackout continues (reports tomorrow). No entry, stay off watchlist.
3. Broad market / mega-cap tech — no entry of any kind. Wednesday's Fed-driven selloff (worst day in over a year, credibility-questioning dissent, 30Y yield at an 18-year high) plus Core PCE/GDP/jobless claims all landing this morning plus mixed MSFT/META earnings reactions is too much stacked event risk. Wait for the data prints and post-open tape to clarify direction.

### Risk Factors
- Dow's ~1,100-point drop Wednesday was the worst single day in over a year, driven by a divided, credibility-challenged Fed — volatility regime not settled despite VIX pulling back this morning.
- Iran-US conflict actively escalating (US just struck Iran, Trump vowing further "very hard" retaliation) — unpredictable, headline risk can move oil/defense/broad risk appetite intraday in either direction.
- Core PCE + GDP + jobless claims all due pre-open — a hot inflation print on top of yesterday's yield spike could extend the selloff; a cool print could spark a sharp relief rally. Binary risk into the open.
- Mega-cap tech crosscurrents: MSFT strength vs. META's earnings miss and rising capex fatigue narrative could pull the Nasdaq either way.
- 30Y yield at its highest since 2007 — a standing headwind for equity valuations that isn't resolved by today's calm-ish futures.

### Decision
HOLD — no held positions to protect. Yesterday's Fed-driven selloff (worst day in over a year, hawkish 9-3 split, yield spike) plus an actively escalating Iran-US conflict plus this morning's Core PCE/GDP/jobless-claims data stack far too much event risk for a new entry before the tape shows a clean, confirmed post-data/post-open direction. Defense fundamentals remain strong but the catalyst is stale without a fresh level; mega-cap tech has no clear signal after mixed MSFT/META prints. Patience > activity.

### Execution (market-open)
- No idea named a numeric level L for today (LMT/RTX/NOC: "if a clean level appears" — no level set; XOM: earnings blackout; broad market/mega-cap tech: no entry ahead of stacked Fed/Iran/PCE event risk) — confirmation bar not applicable, no tickers checked.
- Result: no trades

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-07-31 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~18.5, elevated but off Wednesday's spike-highs. ([Investing.com](https://www.investing.com/indices/us-spx-vix-futures))
- Futures higher: S&P +0.3%, Nasdaq-100 +0.5%, riding Thursday's 1.66% rally to a close of 7,437.63 on strong AI-earnings momentum. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-30/stock-market-today-dow-s-p-live-updates))
- Top catalyst: Big Tech earnings crosscurrents dominate the tape — Amazon (AMZN) beat and surged ~13% premarket on cloud/AI monetization strength, while Apple (AAPL) tumbled ~7.2% premarket on a Services and China revenue miss. Mixed signal for mega-cap tech open. ([TheStreet](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-july-31-2026))
- Iran-US conflict still widening: US launched a "heavy wave" of fresh strikes on Iran Thursday after the 5-night pause broke; strikes killed civilians on Qeshm Island per Iranian state media; Egypt's Damietta port was struck (first time Egypt drawn into the conflict); IRGC vows Strait of Hormuz stays disrupted and threatens retaliation. ([Bloomberg](https://www.bloomberg.com/news/articles/2026-07-30/us-launches-fresh-strikes-against-iran-as-war-escalates-again), [CNN](https://www.cnn.com/2026/07/30/world/live-news/iran-war-trump))
- Oil calm despite the war: WTI ~$83.68 (+0.1%), Brent ~$89.34 (+0.35%) — Hormuz crude flows reported recovering to ~30-35% of pre-war levels, easing the spike-risk premium from earlier in the week. ([CNBC](https://www.cnbc.com/2026/07/31/oil-prices-today-brent-wti-hormuz-trump-iran-.html))
- Defense (LMT/RTX/NOC): mixed/flat premarket (LMT +0.86%, RTX -0.40%, NOC -0.04%) despite the active war — last week's earnings-driven pop (record backlogs, raised FY26 guidance) is priced in and the war catalyst hasn't moved these names further today. ([Defense World](https://www.defenseworld.net/2026/07/31/promising-defense-stocks-to-follow-today-july-29th.html))
- XOM reports Q2 2026 results before today's open (~8:30am CT call); consensus ~$3.68-3.87 EPS on ~$98B revenue, beat in each of the last 4 quarters (avg surprise +6%). Earnings-day volatility — no new position today regardless of print. ([Alphastreet](https://news.alphastreet.com/exxon-mobil-xom-q2-2026-preview-eps-est-3-68-reports-july-31/))
- Econ calendar: Employment Cost Index at 8:30am ET, Michigan Consumer Sentiment (final) at 10am ET — lighter than the last two days, no Core PCE/GDP today (released Thursday, came in benign). ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar))
- Rotation: energy/industrials/defense still leading 2026 YTD, but Thursday's AI-earnings-driven tech rally (AMZN) and today's premarket action show money flowing back into mega-cap tech on strong prints, not away from it — rotation signal is muddier than prior weeks. ([Kalkine](https://kalkine.com/news/premium/us-sector-performance-analysis-energy-surges-as-investors-rotate-toward-defensive-and-value-oriented-sectors))

### Trade Ideas
1. AMZN — beat-and-raise earnings, ~13% premarket gap on cloud/AI strength. No pre-open entry: chasing a 13%+ gap has poor risk/reward and high gap-fill risk. Watch only for a confirmed hold above the premarket high on the first 30-min bar (CONFIRMED = bar close > L and bar low >= L*0.99); stop -7%, target 2:1 minimum if it qualifies.
2. LMT/RTX/NOC (defense) — Iran war still active and widening (Egypt now involved, Hormuz disrupted) but premarket action is flat/mixed — no fresh catalyst move today, last week's guidance-raise pop already priced. No entry; watch only if headlines drive a fresh premarket high with room to confirm.
3. XOM — reports Q2 earnings today before open. Earnings-day volatility, no defined pre-print level, thesis was already broken by the oil reversal two weeks ago. No entry, stay off watchlist today regardless of print.

### Risk Factors
- Iran-US conflict is actively widening (Egypt struck for the first time, IRGC vows Hormuz stays disrupted) — a headline escalation could spike oil and risk sentiment intraday despite today's calm open.
- AAPL's ~7.2% premarket drop (Services/China miss) is a index-weight-heavy negative that could offset AMZN's positive pull on the Nasdaq/S&P — net tech direction is unsettled into the open.
- XOM earnings this morning adds single-name volatility risk to the energy complex on a day already carrying war-driven oil-price uncertainty.
- Friday session — end-of-week positioning/profit-taking on a strong Thursday close (+1.66%) could add chop regardless of headlines.
- VIX ~18.5 still elevated versus the summer's calmer weeks — regime not fully settled even as futures point higher.

### Decision
HOLD — no held positions to protect. AMZN's gap is too large to chase without a confirmed post-open hold; defense catalyst (Iran war) hasn't moved LMT/RTX/NOC further today despite active widening of the conflict; XOM is in earnings-day blackout. No idea has a confirmed entry trigger pre-open. Reassess AMZN and defense on the post-open tape for a qualifying level. Patience > activity.

### Execution (market-open)
- AMZN: L=266.69 (premarket high) | bar 13:30Z l=262.01 c=269.16 -> NOT CONFIRMED (low 262.01 < L*0.99=264.02 — wick under the level exceeded 1%)
- LMT/RTX/NOC: no fresh premarket high formed today (flat/mixed premarket per research) — no level L to check
- XOM: earnings blackout, no entry regardless of print
- Result: no trades

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-08-03 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~16.0, down sharply from last week's ~18.5-19.4 spike regime — risk-off has unwound. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-monday-august-3-dow-sp-500-nasdaq-092516872.html))
- Futures broadly higher: S&P +0.3-0.6%, Dow +0.56%, Nasdaq-100 +0.3%, Russell 2000 +0.55% — risk-on across the board. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-monday-august-3-dow-sp-500-nasdaq-092516872.html), [Benzinga](https://www.benzinga.com/markets/prediction-markets/26/08/60863465/stock-market-will-sp-500-open-up-or-down-today-12))
- Top catalyst: Trump called off a planned new wave of strikes on Iran over the weekend; negotiations (Strait of Hormuz reopening, denuclearization framework) resume today. Oil and Treasury yields eased on the news. ([Yahoo Finance](https://finance.yahoo.com/markets/live/stock-market-today-monday-august-3-dow-sp-500-nasdaq-092516872.html), [CNN](https://www.cnn.com/2026/08/02/world/live-news/iran-war-trump))
- Defense (LMT/RTX/NOC) reaction: names "wobbling" on the de-escalation headlines per press coverage; our own premarket tape confirms it — LMT trading ~582, essentially flat to Friday's 582.74 close on very thin volume (a few hundred shares/bar). No fresh catalyst, war-premium catalyst now working against the trade. ([HeyGoTrade](https://www.heygotrade.com/en/blog/reposition-defense-stocks-noc-lmt-rtx-iran-ceasefire/))
- AMZN continuing Friday's post-earnings strength (cloud/AI beat, +13% Fri) on a second, much smaller leg higher — premarket high 276.66 vs Friday's 271.58 close (+1.9%), steady volume all morning, no signs of gap-fill. ([Benzinga](https://www.benzinga.com/trading-ideas/movers/26/08/60864754/why-atkore-shares-are-trading-higher-by-26-here-are-20-stocks-moving-premarket))
- NVDA/chip names: headline claims of an "AI-optimism rebound," but our own premarket bars show NVDA flat-to-down (~200, vs Friday's 202 close, drifting sideways/down all morning on light volume) — no confirming price action, treat the rebound narrative as unconfirmed today. ([Finviz](https://finviz.com/?a=5989476))
- XOM: post-earnings (reported Thu Jul 31) pop has faded — premarket ~153.3-153.7 vs Friday's 155.44 close, pressured by oil easing on the Iran de-escalation. No fresh catalyst.
- Econ calendar this week: July jobs report Friday Aug 7 is the marquee event; nothing major pre-open today. Consumer confidence hit a 5-month high (55.2) per early prints. ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar), [ts2.tech](https://ts2.tech/en/stock-market-today-03-08-2026/))
- Heavy earnings week ahead: AMD, Pfizer, Amgen, McDonald's, Shopify and others report this week — no positions held in any of these, no blackout conflicts today. ([ts2.tech](https://ts2.tech/en/stock-market-today-03-08-2026/))

### Trade Ideas
1. AMZN — continuation breakout candidate. Premarket high L=276.66 (steady volume, no gap-fill signs) vs Friday close 271.58. This is a fresh, much smaller leg (not chasing Friday's 13% pop). stop = L*0.93 = 257.35 (6.98% below L), target = L + 2x risk = 315.28, rr = 2.0:1.
   - IDEA: AMZN | L=276.66 | stop=257.35 | target=315.28 | rr=2.0:1 | sector=mega-cap-tech | catalyst=Q2 cloud/AI beat, second-day continuation on steady premarket volume, no gap-fill
2. LMT/RTX/NOC (defense) — Iran de-escalation (Trump called off new strikes, talks resume today) removes the war-premium catalyst that drove July's rally; premarket flat/thin volume, no fresh level. Catalyst now runs against the trade, not for it.
   - NO-TRADE: LMT — de-escalation removes war catalyst; flat/thin premarket, no fresh level
   - NO-TRADE: RTX — same de-escalation reasoning, no premarket catalyst today
   - NO-TRADE: NOC — same de-escalation reasoning, no premarket catalyst today
3. NVDA / semis — headline "AI-rebound" narrative not confirmed by actual premarket tape (flat-to-down, light volume). No level to trade against unconfirmed price action.
   - NO-TRADE: NVDA — rebound narrative unconfirmed by premarket price action (flat-to-down on light volume)
4. XOM — post-earnings pop faded, oil easing on Iran de-escalation works against the thesis, no fresh catalyst.
   - NO-TRADE: XOM — post-earnings pop faded; oil easing on de-escalation; no fresh catalyst

### Risk Factors
- Iran de-escalation is fresh and fragile (Trump "called off" strikes, not a signed deal) — a headline reversal could snap back oil/defense/risk sentiment sharply and invalidate today's risk-on tape intraday.
- AMZN chasing risk: even at a much smaller premarket gap than Friday, a two-day cloud/AI move can still gap-fill hard if the broader tech tape sours; confirmation bar (close > L and low >= L x 0.99) is the only thing standing between this and a repeat of Friday's rejected AMZN setup.
- VIX ~16 is a fast, large drop from last week's ~18.5-19.4 — could mean genuine de-risking or complacency into a fragile geopolitical situation.
- Heavy earnings week (AMD, Pfizer, Amgen, MCD, Shopify) — no current exposure, but sets up potential candidates/blackouts for later in the week.
- NVDA/chip "rebound" headlines diverge from actual premarket price action — a reminder to trade the tape, not the narrative.

### Decision
HOLD entries pending open confirmation. AMZN is the only idea with a real, data-backed level (premarket high 276.66, steady volume, genuine second-leg continuation) — watch for CONFIRMED = bar close > L and bar low >= L x 0.99 on the first 30-min bar. Defense (Iran de-escalation killed the catalyst), NVDA/semis (narrative not confirmed by tape), and XOM (faded pop, no catalyst) are all NO-TRADE today. Patience > activity.

### Execution (market-open)
- skipped — confirmation bar still open, fired at 13:36 UTC (`guard.py bar-closed` returned "OPEN - 24m remaining")
- Sync: trade log in sync | Reconcile: all positions protected
- Result: no trades (gate blocked; routine fired ~24m early)

### Midday
- Positions checked: 0 | cuts: 0 | tightened: 0 | risk: OK

## 2026-08-04 — Pre-market Research
### Account
- Equity $100,000 / Cash $100,000 (100%) / Buying power $400,000 / Daytrade count 0
- No open positions, no open orders. Not halted, trading day open.

### Market Context
- VIX ~15.75-16.0, down further from last week's spike — calm vol regime holding. ([Investing.com](https://www.investing.com/indices/us-spx-500-futures))
- S&P 500 futures +0.2-0.3%, Polymarket implying 77% odds of a higher open — Monday's tech-led reversal (best day in weeks) continuing, driven by renewed confidence in AI-capex payoff. ([Benzinga](https://www.benzinga.com/markets/prediction-markets/26/08/60896308/sp500-aug-4-open-up-or-down-polymarket-trump-iran-tech-rally-amazon-ai-earnings))
- Top catalyst: Palantir (PLTR) blowout Q2 — EPS $0.41 vs $0.28 est, revenue $1.94B vs $1.80B est (+93% YoY), US commercial rev +149% YoY, FY26 US-commercial guide raised to >$3.42B from $3.22B. Stock +12% after Monday's close, extending the move premarket. Our own bars confirm real, sustained action: premarket high 147.51 (09:05-09:10Z) on steady volume all morning (not a thin/fading spike), last premarket print ~146.2. ([CNBC](https://www.cnbc.com/2026/08/03/palantir-pltr-earnings-q2-2026.html))
- Iran-US talks ongoing, no fresh escalation — Trump says this is Tehran's "last chance" to sign a deal, negotiations continuing; de-escalation trend from last week intact. ([Al Jazeera](https://www.aljazeera.com/amp/news/liveblog/2026/8/3/iran-war-live-trump-says-talks-set-to-begin-tehran-urges-us-to-honour-mou))
- Earnings before today's open: Caterpillar (CAT) and McDonald's (MCD), plus Pfizer, BP, Marathon Petroleum, Spotify, Toyota, Kimberly-Clark, Merck, Cummins, APTV, ADM and others — broad blackout list, none currently held. ([Benzinga](https://www.benzinga.com/markets/equities/26/08/60897120/stock-market-today-sp-500-dow-and-nasdaq-futures-rise-after-strong-monday-gains-mcdonalds-amd-palantir-in-focus))
- AMD reports today after the close (implied ~8.7% move) — blackout today regardless of direction; stock has rallied toward $500 into the print on MSFT/PLTR-driven AI optimism. ([Benzinga](https://www.benzinga.com/markets/tech/26/08/60872788/amd-options-price-9-percent-earnings-move-history))
- AMZN: no fresh catalyst today — premarket drifting down from Monday's 284.02 close to ~278, below Monday's range; second-leg continuation thesis from Aug 3 has faded, not extended. ([Benzinga](https://www.benzinga.com/markets/prediction-markets/26/08/60896308/sp500-aug-4-open-up-or-down-polymarket-trump-iran-tech-rally-amazon-ai-earnings))
- Defense (LMT/RTX/NOC): our bars show LMT premarket high 586.22 vs Monday's 586.29 close — flat, thin volume (only 4 bars printed). Iran de-escalation continues to remove the war-premium catalyst; no fresh level.
- Econ calendar: nothing major pre-open today (July jobs report is Friday Aug 7, the week's marquee event). ([Kiplinger](https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar))
- Rotation: energy/industrials still leading 2026 YTD, but Monday's rally shows AI-capex-driven mega-cap tech pulling capital back in on strong prints (MSFT, PLTR) — rotation signal mixed today, not a clean move away from tech. ([AlphaBetaStock](https://alphabetastock.com/sector-rotation-industrials-energy-tech-narrowing-2026/))

### Trade Ideas
1. PLTR — post-earnings reaction (blowout Q2, raised guidance), real premarket level with sustained volume, not a thin spike. Premarket high L=147.51. stop = L*0.93 = 137.18 (7.0% below L), target = L + 2x risk = 168.17, rr = 2.0:1.
   - IDEA: PLTR | L=147.51 | stop=137.18 | target=168.17 | rr=2.0:1 | sector=software-ai | catalyst=Q2 beat EPS 0.41 vs 0.28 est, rev +93% YoY, FY26 US-commercial guide raised to $3.42B+
2. AMZN — no fresh premarket catalyst; price below Monday's close, prior continuation thesis faded rather than extended.
   - NO-TRADE: AMZN — no fresh level, premarket trading below Monday's close, thesis faded
3. LMT/RTX/NOC (defense) — Iran de-escalation talks continue, war-premium catalyst still absent; premarket flat/thin, no fresh level.
   - NO-TRADE: LMT — flat premarket (586.22 vs 586.29 close), no fresh catalyst
   - NO-TRADE: RTX — same de-escalation reasoning, no premarket catalyst today
   - NO-TRADE: NOC — same de-escalation reasoning, no premarket catalyst today
4. CAT/MCD — reporting Q2 before today's open.
   - NO-TRADE: CAT — earnings blackout, reports this morning
   - NO-TRADE: MCD — earnings blackout, reports this morning
5. AMD — reports Q2 after today's close.
   - NO-TRADE: AMD — earnings blackout, reports after close today

### Risk Factors
- PLTR chase risk: stock is already ~17% above Monday's pre-earnings close — even with sustained premarket volume, a large single-day post-earnings gap carries real gap-fill risk (see AMZN's rejected 13% gap setup on Jul 31). Confirmation bar (close > L and low >= L x 0.99) is the only thing standing between this idea and a repeat of that outcome.
- Iran-US talks are fresh and unsigned ("last chance," not a deal) — a headline reversal could snap back risk sentiment and hit both broad tape and defense names in either direction intraday.
- AMD reports after close today with an ~8.7% implied move and 7-of-12 negative next-day reactions historically — no exposure held, but a bad print could pressure semis/broad tech into tomorrow's open.
- Heavy earnings morning (CAT, MCD, PFE, BP, MPC, and more) adds single-name and index-level volatility around the open independent of any position we'd take.
- VIX ~15.75-16.0 is calm, but calm-into-a-big-earnings-week can mask complacency risk (AMD, SNDK, WDC, and others still reporting this week).

### Decision
HOLD entries pending open confirmation. PLTR is the only idea with a real, data-backed level (premarket high 147.51, sustained volume, genuine post-earnings reaction) — watch for CONFIRMED = bar close > L and bar low >= L x 0.99 on the first 30-min bar. AMZN (faded, no fresh level), defense (de-escalation removed the catalyst, flat premarket), and CAT/MCD/AMD (earnings blackout) are all NO-TRADE today. Patience > activity.

### Execution (market-open)
- skipped — confirmation bar still open, fired at 13:36 UTC (`guard.py bar-closed` returned "OPEN - 24m remaining")
- Candidates from `guard.py ideas`: 1 (PLTR)
- Sync: trade log in sync | Reconcile: all positions protected
- Result: no trades (gate blocked; routine fired ~24m early)
