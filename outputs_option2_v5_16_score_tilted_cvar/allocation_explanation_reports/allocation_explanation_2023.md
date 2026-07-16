# V5.16 Allocation Explanation Report

Generated at: `2026-07-16T13:06:41`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-15`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| EIS | 11.71% | -2.37% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 11.20% | 2.41% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| THD | 9.34% | 0.88% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWT | 9.18% | 2.82% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 7.50% | -1.52% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| VTV | 6.45% | 3.24% | Selected by latest signal basket | VTV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SMH | 5.29% | -1.07% | Carryover / turnover-constrained holding | SMH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 5.15% | -1.04% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.01% | -1.01% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 4.64% | 1.44% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| TUR | 4.51% | -0.91% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SGOV | 4.29% | -0.87% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| LIT | 4.26% | -0.86% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 3.89% | 3.89% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XOP | 3.89% | 3.89% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SPYD | 3.68% | 3.68% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIS | 11.71% | 0.138 | False | False | False | True | 26.46% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.101277879092927 | 0.117068533282357 |
| XBI | 11.20% | 22.923 | True | True | True | True | 29.64% | Selected by latest signal basket | 0.1199999999247452 | 1.0933333333333333 | 0.1199999999999999 | 0.1199999999999999 | 0.0968621610586333 | 0.1119643423347079 |
| THD | 9.34% | 16.303 | True | True | True | True | 22.97% | Selected by latest signal basket | 0.0680531333880127 | 0.9766666666666668 | 0.0712021525028554 | 0.0712021525028554 | 0.0808359761772151 | 0.093439448498236 |
| EWT | 9.18% | 27.359 | True | True | True | True | 40.62% | Selected by latest signal basket | 0.1199999995316968 | 1.14 | 0.1199999999999999 | 0.1199999999999999 | 0.079427825559584 | 0.0918117472773657 |
| EWY | 7.50% | 14.284 | False | True | True | True | 77.08% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0648719779638694 | 0.0749864371111811 |
| VTV | 6.45% | 15.986 | True | True | True | True | 10.08% | Selected by latest signal basket | 0.1199999991948495 | 0.9066666666666666 | 0.1165540914658867 | 0.1165540914658868 | 0.0557590143793316 | 0.0644526335772574 |
| SMH | 5.29% | 21.921 | False | True | True | True | 51.39% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0457768189020213 | 0.0529140726009335 |
| OIH | 5.15% | 1.593 | False | False | False | True | 29.82% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0445964238027077 | 0.0515496372058802 |
| GLDM | 5.01% | -11.912 | False | False | False | False | 23.90% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0433203029134426 | 0.0500745510159318 |
| CIBR | 4.64% | 29.001 | True | True | True | True | 32.67% | Selected by latest signal basket | 0.0489143044256005 | 1.163333333333333 | 0.0609591194927138 | 0.0609591194927138 | 0.0401687912793628 | 0.0464316741317754 |
| TUR | 4.51% | -2.495 | False | False | False | True | 31.88% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.039033164964316 | 0.0451189876078268 |
| SGOV | 4.29% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0371445284552374 | 0.0429358859473105 |
| LIT | 4.26% | -7.696 | False | False | False | True | 34.57% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0368957369982544 | 0.042648304382382 |
| AVUV | 3.89% | 17.547 | True | True | True | True | 12.77% | Selected by latest signal basket | 0.1199999995413595 | 1.0466666666666666 | 0.1199999999999999 | 0.1199999999999999 | 0.0336510066575627 | 0.0388976746764321 |
| XOP | 3.89% | 16.599 | True | True | True | True | 31.92% | Selected by latest signal basket | 0.1199999999433287 | 1.0 | 0.1199999999999999 | 0.1199999999999999 | 0.0336510066575627 | 0.0388976746764321 |
| SPYD | 3.68% | 15.95 | True | True | True | True | 11.56% | Selected by latest signal basket | 0.1199999998115091 | 0.8833333333333333 | 0.1135545380956928 | 0.1135545380956928 | 0.0318435376454551 | 0.0368083956739898 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 4.29% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 78.72% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 9.92% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 22.25% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 2.25% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 80.50% | 24.15% | 17.82% | 1.191 | -15.64% |
| SPY | 80.93% | 24.26% | 15.61% | 1.341 | -18.76% |
| QQQ | 99.63% | 28.82% | 20.63% | 1.233 | -22.77% |
| VTI | 80.76% | 24.21% | 15.76% | 1.328 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| VTV | SPYD | 0.857 |
| VTV | AVUV | 0.837 |
| OIH | XOP | 0.817 |
| AVUV | SPYD | 0.785 |
| EWT | SMH | 0.774 |
| EWT | EWY | 0.761 |
| OIH | AVUV | 0.697 |
| EWY | SMH | 0.643 |
| VTV | OIH | 0.610 |
| AVUV | XOP | 0.604 |
| SMH | CIBR | 0.603 |
| EWT | LIT | 0.570 |
| XBI | VTV | 0.552 |
| THD | EWT | 0.546 |
| XBI | AVUV | 0.540 |
| EIS | SMH | 0.535 |
| VTV | SMH | 0.527 |
| EWY | LIT | 0.526 |
| CIBR | AVUV | 0.525 |
| VTV | CIBR | 0.524 |

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
