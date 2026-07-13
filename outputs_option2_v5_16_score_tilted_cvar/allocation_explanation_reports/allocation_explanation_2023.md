# V5.16 Allocation Explanation Report

Generated at: `2026-07-13T13:09:33`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-10`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| EIS | 11.59% | -1.31% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 10.63% | -1.20% | Carryover / turnover-constrained holding | MLPA is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 9.56% | 2.62% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| DIV | 8.19% | -0.93% | Carryover / turnover-constrained holding | DIV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 7.46% | 2.86% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.64% | -0.75% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 6.57% | 2.96% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SMH | 6.23% | -0.70% | Carryover / turnover-constrained holding | SMH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.04% | -0.68% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.57% | -0.63% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.87% | -0.55% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| IXC | 4.46% | -0.50% | Carryover / turnover-constrained holding | IXC is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 3.33% | 3.33% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| VTV | 3.33% | 3.33% | Selected by latest signal basket | VTV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XLE | 3.25% | -0.37% | Carryover / turnover-constrained holding | XLE is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SGOV | 2.28% | -0.26% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIS | 11.59% | -2.324 | False | False | False | True | 26.11% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.098628782069176 | 0.1159446435788557 |
| MLPA | 10.63% | 11.978 | True | True | True | True | 15.12% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0903887035569663 | 0.1062578873793332 |
| EWT | 9.56% | 31.715 | True | True | True | True | 39.84% | Selected by latest signal basket | 0.1199999997783257 | 1.163333333333333 | 0.12 | 0.12 | 0.0813109161610059 | 0.0955863490917465 |
| DIV | 8.19% | 12.452 | True | True | True | True | 11.36% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0696483856361854 | 0.0818762746433018 |
| XBI | 7.46% | 26.024 | True | True | True | True | 30.10% | Selected by latest signal basket | 0.1199999999004044 | 1.1166666666666667 | 0.12 | 0.12 | 0.0634590451270187 | 0.0746002963308028 |
| OIH | 6.64% | -1.887 | False | False | False | True | 30.15% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0564775007885514 | 0.0663930301254285 |
| AVUV | 6.57% | 15.004 | True | True | True | True | 12.99% | Selected by latest signal basket | 0.1199999996096277 | 1.0 | 0.12 | 0.12 | 0.0559212146016385 | 0.0657390789935549 |
| SMH | 6.23% | 29.707 | True | True | True | True | 50.33% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0530238570131507 | 0.062333043900451 |
| EWY | 6.04% | 23.82 | False | True | True | True | 74.37% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0514204843109878 | 0.0604481734541552 |
| GLDM | 5.57% | -9.896 | False | False | False | False | 23.71% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.047421785703619 | 0.0557474392963972 |
| TUR | 4.87% | -1.279 | False | False | False | True | 31.85% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0414213301868537 | 0.0486935077603252 |
| IXC | 4.46% | 1.476 | False | False | False | True | 23.38% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0379176119736427 | 0.0445746557284045 |
| CIBR | 3.33% | 26.665 | True | True | True | True | 33.87% | Selected by latest signal basket | 0.1098827012898172 | 1.14 | 0.12 | 0.12 | 0.0282870591478551 | 0.0332533051912954 |
| VTV | 3.33% | 15.344 | True | True | True | True | 10.18% | Selected by latest signal basket | 0.1199999995795041 | 1.0466666666666666 | 0.12 | 0.12 | 0.0282870591478551 | 0.0332533051912954 |
| XLE | 3.25% | 1.78 | False | False | False | True | 24.37% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0276341554537833 | 0.0324857738022594 |
| SGOV | 2.28% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0194061714811935 | 0.0228132355323926 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 2.28% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 80.09% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 15.44% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 15.09% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 81.86% | 24.49% | 15.75% | 1.343 | -13.96% |
| SPY | 79.70% | 23.95% | 15.61% | 1.325 | -18.76% |
| QQQ | 99.98% | 28.90% | 20.61% | 1.238 | -22.77% |
| VTI | 79.13% | 23.80% | 15.77% | 1.306 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| IXC | XLE | 0.976 |
| AVUV | VTV | 0.838 |
| OIH | XLE | 0.834 |
| OIH | IXC | 0.834 |
| DIV | VTV | 0.803 |
| DIV | AVUV | 0.779 |
| EWT | SMH | 0.774 |
| EWT | EWY | 0.763 |
| OIH | AVUV | 0.697 |
| MLPA | XLE | 0.684 |
| MLPA | IXC | 0.682 |
| SMH | EWY | 0.640 |
| MLPA | DIV | 0.613 |
| OIH | VTV | 0.610 |
| SMH | CIBR | 0.603 |
| MLPA | OIH | 0.601 |
| DIV | OIH | 0.585 |
| DIV | IXC | 0.585 |
| DIV | XLE | 0.584 |
| AVUV | XLE | 0.559 |

## How to explain this to a non-technical person

- The model does not simply buy the highest-return ETFs.
- It first checks whether each ETF is in an uptrend and has positive momentum.
- It avoids owning too many ETFs that behave almost the same.
- It uses a risk optimizer to spread the portfolio across the selected ETFs.
- It gives a small extra push to ETFs with stronger scores.
- It parks part of the portfolio in `SGOV` when the opportunity set is not strong enough or when the selected basket is too volatile.
- It limits monthly trading so the portfolio does not churn too aggressively.

## What this report can and cannot prove

This report explains the allocation using files already generated by V5.16.

It can explain:
- final weights,
- trend and momentum reasons,
- cash/SGOV logic,
- turnover impact,
- correlation/overlap context,
- and benchmark performance context.

If `final_allocation_attribution.csv` exists, this report can include raw CVaR weights, score-tilt multipliers, cash-scaled weights, turnover-capped weights, and final pruned weights. If that file does not exist, the report falls back to the older summary-level explanation.

To get that level of detail, the main V5.16 strategy script would need to save an additional internal attribution file during each monthly rebalance.
