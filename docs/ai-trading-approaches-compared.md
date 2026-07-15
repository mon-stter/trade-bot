# Two philosophies of an "AI trading bot"

A short, honest comparison written while evaluating a popular "self-improving
trading agent" onboarding script (the "Hermes" prompt) against the bot we built
in this repo. The goal is to separate **real engineering** from **narrative**, so
the difference is legible to someone who cares about evidence.

## The two designs in one line

| | **This repo (disciplined executor)** | **The "Hermes" self-improving agent** |
|---|---|---|
| Where the rules live | Fixed, human-authored, in a unit-tested `guard.py` | An LLM rewrites the strategy file every few trades |
| Claim | "A disciplined executor of a chosen strategy" | "A self-improving agent that learns an edge" |
| Edge source | Whatever edge the *human* strategy has (honest about this) | Claims the *loop itself* creates edge |
| Safety | Kill-switch, drawdown halt, real order gate, paper-first | Paper-first, then a two-flag flip to live |
| Honesty | Doesn't pretend to learn | Uses the language of science without its substance |

## Why "self-improvement every 5 trades" cannot work

This is the heart of it, and it's a statistics point, not an opinion.

1. **Sample size.** Return, drawdown, and Sharpe ratio are *statistics estimated
   from data*. Estimated from 5 — or even 25 — trades, their sampling error is
   enormous. A Sharpe ratio from 25 trades has a confidence interval so wide it's
   consistent with "great strategy" and "worthless strategy" at the same time.
2. **You are therefore optimizing noise.** Each "reflection" nudges a parameter to
   fit the last handful of random outcomes. That is the textbook definition of
   **overfitting**. The strategy will *look* like it's improving while it chases
   fluctuations that won't repeat.
3. **"Change one variable per cycle, scientific method" is scientism.** Real method
   needs an out-of-sample holdout, and correction for the fact that you're testing
   many variants (multiple comparisons). The Hermes loop has neither. The
   one-variable rule slows the overfitting; it doesn't prevent it.
4. **An LLM doesn't know which variable to change.** It guesses, then writes a
   confident justification. If you genuinely wanted to tune parameters you'd use
   walk-forward analysis or Bayesian optimization — neither of which needs an LLM.
   The "brain" is narration layered over random search.

## The signal isn't the strategy — it's the strategy that's missing

The Hermes worker's actual entry rule is `RSI < 30 → go long`. That is one of the
most widely known, most arbitraged retail signals in existence, with no durable
edge in liquid crypto markets. No amount of loop around an empty center fills it.
And paper results omit fees and slippage — the exact costs that kill mean-reversion
strategies in live trading.

## Red flags worth naming (pattern-recognition for future research)

These are the tells that a "tutorial" is partly a funnel:

- **Load-bearing referral links.** The script insists a Railway URL be opened
  *exactly as written* because the `referralCode` "is load-bearing," plus a
  named third-party app and an install. Hard-coded, un-editable affiliate links
  in an "educational" flow signal monetization, not teaching.
- **`curl … | bash` / `iex (irm …)` run exactly as written.** Executing unreviewed
  remote scripts, with instructions engineered to remove the friction where you'd
  otherwise stop and read them ("one terminal session", "install X last so the
  reload doesn't break our session", "you act, the viewer only confirms").
- **Unverifiable dependencies.** Claims about a specific CLI/agent that may not
  exist as described. Verify the repo before trusting the installer.
- **Unsupervised mutation of a live config.** The end-state is an AI editing the
  strategy and auto-deploying it, with "go live" a two-flag change away.

## What the Hermes design gets right (credit where due)

The *DevOps* is competent and worth studying: persistent state volume, versioned
strategy history, heartbeat, per-adapter retries with circuit-breaking, a
paper-mode default, an explicit risk-accept flag. The plumbing is real. The alpha
and the "learning" are not.

## The honest takeaway

A trading system's results come from **edge minus costs**, discovered through
**validation**, and protected by **risk discipline**. An LLM can help you *build
and operate* such a system (as it did here). It cannot *manufacture edge* by
rewriting a config every few trades — and a system that claims otherwise is
selling the story of intelligence, not the substance.

This repo takes the honest path: a fixed, chosen strategy, enforced without
drift, on paper, with hard safety rails — so that whatever it earns or loses is a
clean, auditable test of *that strategy*, not a mirage produced by fitting noise.
