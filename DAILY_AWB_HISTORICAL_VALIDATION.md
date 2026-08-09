# Daily AWB Historical Robustness Validation

## Decision

The Daily ATR-Confirmed Washout Breakout ETF Sleeve remains promising research,
but it is **not ready for a 10% production allocation**. It passed 7 of 10
predefined historical validation gates.

The valid causal backtest covers October 2020 through August 7, 2026. The
selected exit activates after a 3% peak gain and trails the highest post-entry
high by 3.0 ATR, with the stop floored at the entry price. Signals are evaluated
after the close; the independent trade ledger enters and exits at the next
session's adjusted open.

## Correction to the earlier experiment

The earlier 18.33% candidate CAGR was not fully as-of reproducible. Historical
midweek rows used the prior completed week's features, while a live run
truncated midweek treated the current partial week as complete. Six of the 21
historical entries changed under an as-of recalculation.

Weekly confirmation features now use the prior completed weekly state updated
with the current week-to-date OHLCV bar. Full-history and truncated-as-of
calculations now match exactly. The causal correction reduced the selected
entry set from 21 to 15 and produced the following aggregate result:

| Metric | Causal Daily AWB overlay | Production baseline | Difference |
|---|---:|---:|---:|
| CAGR | 18.10% | 17.61% | +0.49 percentage points |
| Sharpe | 1.045 | 1.018 | +0.027 |
| Max drawdown | -14.03% | -14.84% | +0.80 percentage points |
| MAR | 1.289 | 1.187 | +0.103 |
| Sortino | 1.487 | 1.447 | +0.040 |

## Validation gates

| Gate | Result | Evidence |
|---|---:|---|
| Full-period improvement | Pass | CAGR +0.49 points; Sharpe +0.027 |
| Parameter neighborhood | Pass | All 11 nearby ATR exits improved CAGR |
| Subperiod consistency | Pass | Three of four broad periods improved CAGR |
| Transaction-cost stress | Pass | CAGR delta remained positive at 50 bps per side |
| Walk-forward parameter choice | **Fail** | Only two of four test years beat production |
| Next-open trade excess | Pass | Closed trades averaged +2.02% versus SPY |
| Bootstrap confidence | **Fail** | 95% mean-excess interval was -0.71% to +5.66% |
| Ticker concentration | Pass | Every leave-one-ticker-out mean remained positive |
| As-of reproducibility | Pass | Zero signal mismatches; zero weekly-feature drift |
| Minimum sample | **Fail** | 14 closed trades versus a 30-trade target |

The 14 closed next-open trades had a 71.4% absolute win rate, a 3.60% mean net
return, a 50.0% beat-SPY rate, and a 90.0% bootstrap probability that mean
excess return is positive. The two-sided 95% interval still includes zero, so
the observed alpha is not statistically secure.

## Known-date findings

- XHB did not qualify on April 8, 2026; it lacked the required washout age,
  RSI recovery, and 20-day breakout. It qualified on April 17.
- XHB did not qualify on May 21 because most trend and recovery confirmations
  had failed.
- GNR did not qualify on July 13. The former July 21 entry disappears under
  causal week-to-date features because weekly RSI was above the allowed range.
- GLD did not qualify on July 24 or July 31. GLDM, the eligible gold proxy,
  qualified on August 5.

## Reproduce the validation

```powershell
python experiment_oversold_reversal_sleeve.py --variant-suite exit --output-dir outputs_experiment_oversold_reversal_sleeve_v7_causal_validation
python run_daily_awb_validation.py
```

The second command writes the detailed gate table, parameter results,
subperiods, cost tests, expanding walk-forward selections, next-open trades,
bootstrap summary, leave-one-ticker-out results, known-date diagnostics, and
as-of invariance checks under
`outputs_experiment_daily_awb_historical_validation/`.
