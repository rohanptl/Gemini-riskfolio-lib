# V5.16 Allocation Explanation Report

Generated at: `2026-07-17T18:04:24`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-17`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| EIS | 11.98% | -2.18% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 10.60% | 2.14% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SGOV | 9.22% | -1.68% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| THD | 8.46% | 2.52% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 7.08% | -1.29% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 6.58% | -1.20% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XOP | 6.21% | 2.93% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| MLPA | 6.21% | 2.93% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 5.62% | -1.02% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 5.44% | -0.99% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 5.04% | -0.92% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.39% | -0.80% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| KIE | 3.44% | 3.44% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SPYD | 3.44% | 3.44% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| DIV | 3.29% | 3.29% | Selected by latest signal basket | DIV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| GLDM | 3.01% | -0.55% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIS | 11.98% | -0.218 | False | False | False | True | 26.69% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.1057522266832086 | 0.1197660558739626 |
| XBI | 10.60% | 21.363 | True | True | True | True | 30.27% | Selected by latest signal basket | 0.1199999994253295 | 1.1166666666666667 | 0.12 | 0.1199999999999999 | 0.0935685750323084 | 0.105967879229023 |
| SGOV | 9.22% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0813988432603165 | 0.0921854670653371 |
| THD | 8.46% | 18.21 | True | True | True | True | 22.54% | Selected by latest signal basket | 0.1199999988289625 | 1.0933333333333333 | 0.12 | 0.1199999999999999 | 0.0747094273224922 | 0.084609598564964 |
| LIT | 7.08% | -13.661 | False | False | False | False | 34.27% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0625356696610234 | 0.0708226270182829 |
| AVDV | 6.58% | 2.184 | False | False | False | True | 18.42% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0581202560887782 | 0.0658221018739349 |
| XOP | 6.21% | 21.442 | True | True | True | True | 31.86% | Selected by latest signal basket | 0.1199999998436043 | 1.14 | 0.12 | 0.1199999999999999 | 0.0548098594630237 | 0.0620730257581879 |
| MLPA | 6.21% | 18.33 | True | True | True | True | 15.54% | Selected by latest signal basket | 0.1199999997610324 | 1.0 | 0.12 | 0.1199999999999999 | 0.0548098594630237 | 0.0620730257581879 |
| EWY | 5.62% | 11.013 | False | True | True | True | 77.71% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0496186206614147 | 0.0561938663696007 |
| OIH | 5.44% | 2.638 | False | False | False | True | 29.84% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0480437838262521 | 0.0544103389460367 |
| EWT | 5.04% | 20.152 | False | True | True | True | 41.56% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0445018057262187 | 0.0503989931773683 |
| TUR | 4.39% | -1.566 | False | False | False | True | 32.09% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0387960537733425 | 0.0439371395727326 |
| KIE | 3.44% | 18.035 | True | True | True | True | 19.49% | Selected by latest signal basket | 0.119999975101499 | 0.9533333333333334 | 0.12 | 0.12 | 0.0303586895330882 | 0.0343816921961553 |
| SPYD | 3.44% | 17.773 | True | True | True | True | 12.09% | Selected by latest signal basket | 0.1199999227840306 | 0.93 | 0.12 | 0.12 | 0.0303586895330882 | 0.0343816921961553 |
| DIV | 3.29% | 17.021 | True | True | True | True | 12.09% | Selected by latest signal basket | 0.1199999996628587 | 0.86 | 0.1148896235986936 | 0.1148896235986936 | 0.0290658201117175 | 0.0329174972925202 |
| GLDM | 3.01% | -11.799 | False | False | False | False | 24.17% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.026541794870804 | 0.0300589991075497 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 9.22% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 72.72% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.19% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 20.70% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.70% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 87.75% | 25.95% | 17.38% | 1.300 | -15.29% |
| SPY | 76.73% | 23.19% | 15.61% | 1.286 | -18.76% |
| QQQ | 92.93% | 27.21% | 20.66% | 1.172 | -22.77% |
| VTI | 76.30% | 23.08% | 15.76% | 1.270 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| SPYD | DIV | 0.904 |
| XOP | OIH | 0.816 |
| EWY | EWT | 0.758 |
| XOP | MLPA | 0.671 |
| AVDV | EWT | 0.670 |
| KIE | SPYD | 0.657 |
| KIE | DIV | 0.632 |
| LIT | AVDV | 0.619 |
| MLPA | DIV | 0.613 |
| AVDV | EWY | 0.598 |
| MLPA | OIH | 0.598 |
| AVDV | DIV | 0.586 |
| OIH | DIV | 0.581 |
| AVDV | SPYD | 0.581 |
| THD | AVDV | 0.576 |
| LIT | EWT | 0.571 |
| XOP | DIV | 0.559 |
| EIS | AVDV | 0.547 |
| THD | EWT | 0.542 |
| LIT | EWY | 0.528 |

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
