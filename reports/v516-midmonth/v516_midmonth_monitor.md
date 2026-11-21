# V5.16 Mid-Month Monitor

**Status: REVIEW_DRIFT_NO_TRADE**

**Instruction: NO TRADE. Keep the locked monthly Wealthfront targets.**

- Official month: 2026-11
- Source market-close signal date: 2026-10-30
- Allocation submitted date: not recorded
- Live effective date: 2026-11-01
- Latest common price date: 2026-11-20
- Next scheduled rebalance: 2026-12-01
- Estimated return since lock: -4.47%
- Current drawdown since lock: -4.21%
- Maximum drawdown since lock: -4.21%
- Maximum estimated weight drift: 2.26 percentage points

## Largest estimated drifts

| Ticker | Locked target | Estimated weight | Drift (percentage points) |
|---|---:|---:|---:|
| SGOV | 45.93% | 48.19% | +2.26 |
| ARKG | 2.86% | 2.21% | -0.65 |
| XBI | 5.51% | 5.18% | -0.33 |
| XOP | 2.33% | 2.02% | -0.32 |
| CIBR | 6.00% | 5.69% | -0.32 |
| XLE | 3.05% | 2.76% | -0.29 |
| WCLD | 3.05% | 2.80% | -0.24 |
| JQUA | 6.77% | 6.58% | -0.19 |
| XLP | 2.73% | 2.89% | +0.16 |
| BKLN | 2.95% | 3.09% | +0.14 |

## How to use this report

- `NORMAL_NO_TRADE`: everything is operating normally; take no action.
- `PENDING_EFFECTIVE_DATE_NO_TRADE`: the submitted target is not effective yet; wait.
- `REVIEW_DRIFT_NO_TRADE`: drift is notable, but wait for the monthly rebalance.
- `STALE_DATA` or `DATA_ERROR`: do not trade; repair the data problem.
- Market declines alone are not an emergency exit rule.

This report never computes or publishes a new model target.
