# Production milestone: Mom126Skip21

Date: 2026-08-08

## Decision

Promote `mom126_skip21` to the production short-momentum score default while
retaining `raw21` as an explicit rollback option.

The change replaces this score component:

```text
1.5 * ZScore(Mom21)
```

with:

```text
1.5 * ZScore(Mom126Skip21)
```

`Mom126Skip21` measures performance from approximately 126 trading days ago
through 21 trading days ago. No eligibility, CVaR, cash, correlation, or
turnover rule changes are included in this production milestone.

## Fresh milestone regression

Both configurations were rerun with the current code, identical settings, and
market data through 2026-08-07 (`--end-date 2026-08-09`).

| Start window | Raw21 CAGR | Production CAGR | CAGR change | Raw21 Sharpe | Production Sharpe | Raw21 max DD | Production max DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 15.16% | 17.61% | +2.45 pp | 0.874 | 1.018 | -18.70% | -14.84% |
| 2021 | 13.24% | 15.14% | +1.90 pp | 0.807 | 0.921 | -13.85% | -13.37% |
| 2022 | 19.82% | 20.76% | +0.94 pp | 1.150 | 1.231 | -14.14% | -13.28% |
| 2023 | 23.97% | 25.69% | +1.72 pp | 1.313 | 1.416 | -13.64% | -13.38% |

## Rollback

```powershell
python main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py --end-date auto --short-momentum-score raw21
```

## Known production risks

- The backtest does not yet deduct commissions, bid/ask spreads, or slippage.
- Walk-forward start windows overlap and are not independent samples.
- The ETF universe is based on the current categorization file, creating
  possible survivorship and universe-selection bias.
- Re-downloaded vendor data can change historical results; immutable input
  snapshots are not yet stored with each production decision.
- Multiple tested variants create selection bias. The winning configuration
  needs parameter-neighborhood and future out-of-sample validation.
- CVXPY emits deprecated matrix-multiplication warnings through a dependency;
  runs completed, but dependency upgrades should be regression-tested.

This milestone is suitable for controlled production use with monitoring and
rollback capability, not evidence of guaranteed benchmark outperformance.
