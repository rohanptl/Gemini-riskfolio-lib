# V5.16 Allocation Explanation Report

Generated at: `2026-07-09T15:42:45`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-01`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 19.30% | -2.26% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EIS | 10.03% | -1.18% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 8.68% | 2.64% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XBI | 7.84% | 2.74% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.94% | -0.81% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.70% | -0.79% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 5.98% | 2.66% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 5.40% | -0.63% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.30% | -0.62% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 3.70% | -0.43% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 3.65% | -0.43% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.39% | -0.40% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| JETS | 3.28% | 3.28% | Selected by latest signal basket | JETS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XLI | 3.28% | 3.28% | Selected by latest signal basket | XLI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVUV | 3.28% | 3.28% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| THD | 3.27% | -0.38% | Carryover / turnover-constrained holding | THD is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 19.30% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.165246306869413 | 0.1930123392199123 |
| EIS | 10.03% | 2.549 | False | False | True | True | 26.55% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0859068249937116 | 0.1003415904483433 |
| EWT | 8.68% | 29.696 | True | True | True | True | 39.74% | Selected by latest signal basket | 0.119999999630151 | 1.163333333333333 | 0.1199999999999999 | 0.1199999999999999 | 0.0742920510618366 | 0.0867752074618041 |
| XBI | 7.84% | 22.751 | True | True | True | True | 28.81% | Selected by latest signal basket | 0.1199999999209567 | 1.14 | 0.1199999999999999 | 0.1199999999999999 | 0.0671246488751531 | 0.0784034798971152 |
| OIH | 6.94% | -0.487 | False | False | False | True | 29.59% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.059418016999633 | 0.0694019168729179 |
| EWY | 6.70% | 24.609 | False | True | True | True | 75.61% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0573676886246695 | 0.0670070756004082 |
| CIBR | 5.98% | 19.833 | True | True | True | True | 33.91% | Selected by latest signal basket | 0.0958858999916214 | 1.1166666666666667 | 0.1103226752159553 | 0.1103226752159553 | 0.0511696085499412 | 0.0597675435554287 |
| LIT | 5.40% | 7.088 | False | True | True | True | 34.45% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0462395255418046 | 0.0540090677868853 |
| GLDM | 5.30% | -10.844 | False | False | False | False | 23.75% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0453468334942923 | 0.0529663783400978 |
| TUR | 3.70% | 4.555 | False | False | True | True | 33.18% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0316384112397716 | 0.0369545551624077 |
| AVDV | 3.65% | 8.214 | False | True | True | True | 19.39% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0312246022940005 | 0.0364712146622384 |
| XAR | 3.39% | 12.407 | True | True | True | True | 31.91% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.029037912474788 | 0.0339170993833528 |
| JETS | 3.28% | 19.113 | True | True | True | True | 38.30% | Selected by latest signal basket | 0.1115123255024262 | 1.07 | 0.12 | 0.12 | 0.028052525520032 | 0.0327661396749187 |
| XLI | 3.28% | 15.493 | True | True | True | True | 20.84% | Selected by latest signal basket | 0.1199999985219475 | 0.9766666666666668 | 0.12 | 0.12 | 0.028052525520032 | 0.0327661396749187 |
| AVUV | 3.28% | 17.252 | True | True | True | True | 13.32% | Selected by latest signal basket | 0.119999999767827 | 1.0466666666666666 | 0.1199999999999999 | 0.1199999999999999 | 0.028052525520032 | 0.0327661396749187 |
| THD | 3.27% | 12.996 | True | True | True | True | 23.86% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0279737371020843 | 0.0326741125843312 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 19.30% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 81.46% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 14.73% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 17.88% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 77.12% | 23.18% | 15.47% | 1.297 | -13.50% |
| SPY | 82.72% | 24.59% | 15.59% | 1.359 | -18.76% |
| QQQ | 103.82% | 29.65% | 20.58% | 1.267 | -22.77% |
| VTI | 82.61% | 24.56% | 15.75% | 1.346 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| XLI | AVUV | 0.802 |
| XAR | XLI | 0.796 |
| EWT | EWY | 0.764 |
| JETS | AVUV | 0.705 |
| OIH | AVUV | 0.697 |
| JETS | XLI | 0.695 |
| AVDV | XLI | 0.686 |
| EWT | AVDV | 0.668 |
| AVDV | AVUV | 0.652 |
| XAR | AVUV | 0.645 |
| LIT | AVDV | 0.619 |
| AVDV | XAR | 0.613 |
| EWY | AVDV | 0.603 |
| EWT | XLI | 0.582 |
| AVDV | THD | 0.579 |
| XAR | JETS | 0.573 |
| AVDV | JETS | 0.573 |
| EWT | LIT | 0.570 |
| OIH | XLI | 0.552 |
| EWT | THD | 0.548 |

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
