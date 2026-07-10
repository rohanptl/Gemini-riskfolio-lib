# V5.16 Allocation Explanation Report

Generated at: `2026-07-10T15:22:43`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-10`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| EIS | 11.61% | -1.30% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 10.65% | -1.19% | Carryover / turnover-constrained holding | MLPA is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 9.57% | 2.63% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| DIV | 8.20% | -0.92% | Carryover / turnover-constrained holding | DIV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 7.48% | 2.86% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.65% | -0.75% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 6.58% | 2.96% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SMH | 6.24% | -0.70% | Carryover / turnover-constrained holding | SMH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.06% | -0.68% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.57% | -0.62% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.88% | -0.55% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| IXC | 4.47% | -0.50% | Carryover / turnover-constrained holding | IXC is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| VTV | 3.33% | 3.33% | Selected by latest signal basket | VTV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SPYD | 3.25% | -0.37% | Carryover / turnover-constrained holding | SPYD is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XLE | 3.25% | -0.37% | Carryover / turnover-constrained holding | XLE is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SGOV | 2.19% | -0.25% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIS | 11.61% | -2.573 | False | False | False | True | 26.13% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0986684337182893 | 0.1160877682572304 |
| MLPA | 10.65% | 11.9 | True | True | True | True | 15.17% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0904996168299083 | 0.1064767945533036 |
| EWT | 9.57% | 31.324 | True | True | True | True | 39.83% | Selected by latest signal basket | 0.1199999994741144 | 1.163333333333333 | 0.12 | 0.12 | 0.0813725860835889 | 0.0957384399425427 |
| DIV | 8.20% | 12.101 | True | True | True | True | 11.65% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0697343502389348 | 0.0820455416695791 |
| XBI | 7.48% | 24.788 | True | True | True | True | 30.81% | Selected by latest signal basket | 0.1199999997716499 | 1.1166666666666667 | 0.12 | 0.12 | 0.0635687000156185 | 0.0747913819823678 |
| OIH | 6.65% | -2.325 | False | False | False | True | 30.03% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0565499306578443 | 0.0665334899701912 |
| AVUV | 6.58% | 15.234 | True | True | True | True | 13.00% | Selected by latest signal basket | 0.119999999135967 | 1.0 | 0.12 | 0.12 | 0.0559487745350361 | 0.0658262032520274 |
| SMH | 6.24% | 29.442 | True | True | True | True | 50.34% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0530774593096103 | 0.0624479741272561 |
| EWY | 6.06% | 24.44 | False | True | True | True | 74.35% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0515419260780915 | 0.0606413514900632 |
| GLDM | 5.57% | -9.948 | False | False | False | False | 23.72% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0473023287549272 | 0.05565327807075 |
| TUR | 4.88% | -1.184 | False | False | False | True | 31.84% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0414739324069544 | 0.0487959124568743 |
| IXC | 4.47% | 1.094 | False | False | False | True | 23.34% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0379757381489724 | 0.0446801324750127 |
| VTV | 3.33% | 15.474 | True | True | True | True | 10.18% | Selected by latest signal basket | 0.1199999988205932 | 1.0233333333333334 | 0.12 | 0.12 | 0.0282951267739785 | 0.0332904658152865 |
| SPYD | 3.25% | 13.066 | True | True | True | True | 11.52% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0276536477610576 | 0.0325357374367409 |
| XLE | 3.25% | 1.322 | False | False | False | True | 24.35% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0276536477610576 | 0.0325357374367409 |
| SGOV | 2.19% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0186306575118912 | 0.0219197910640326 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 2.19% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 79.04% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 14.76% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 11.78% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 83.28% | 24.85% | 15.72% | 1.363 | -13.01% |
| SPY | 79.17% | 23.81% | 15.61% | 1.318 | -18.76% |
| QQQ | 99.34% | 28.75% | 20.61% | 1.232 | -22.77% |
| VTI | 78.65% | 23.68% | 15.77% | 1.300 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| IXC | XLE | 0.976 |
| DIV | SPYD | 0.902 |
| VTV | SPYD | 0.858 |
| AVUV | VTV | 0.838 |
| OIH | XLE | 0.834 |
| OIH | IXC | 0.834 |
| DIV | VTV | 0.801 |
| AVUV | SPYD | 0.785 |
| DIV | AVUV | 0.779 |
| EWT | SMH | 0.774 |
| EWT | EWY | 0.764 |
| OIH | AVUV | 0.697 |
| MLPA | XLE | 0.684 |
| MLPA | IXC | 0.683 |
| SMH | EWY | 0.641 |
| MLPA | DIV | 0.612 |
| OIH | VTV | 0.610 |
| MLPA | OIH | 0.601 |
| DIV | OIH | 0.584 |
| DIV | IXC | 0.583 |

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
