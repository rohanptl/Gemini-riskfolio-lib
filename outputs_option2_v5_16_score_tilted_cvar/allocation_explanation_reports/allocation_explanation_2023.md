# V5.16 Allocation Explanation Report

Generated at: `2026-07-21T17:39:51`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-21`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 17.77% | -1.31% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EIS | 11.48% | -0.85% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 10.47% | 2.71% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 6.79% | -0.50% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.32% | -0.47% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 6.30% | 3.02% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWT | 5.91% | -0.44% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 5.74% | -0.42% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.63% | -0.42% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWW | 3.72% | -0.27% | Carryover / turnover-constrained holding | EWW is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 3.56% | -0.26% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.33% | -0.25% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWP | 3.26% | -0.24% | Carryover / turnover-constrained holding | EWP is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SPYD | 3.24% | 3.24% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVUV | 3.24% | 3.24% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| THD | 3.24% | 3.24% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 17.77% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.1479171467834028 | 0.1777114411515987 |
| EIS | 11.48% | 0.065 | False | False | False | True | 26.38% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0955588266606679 | 0.1148068169912034 |
| XBI | 10.47% | 19.261 | True | True | True | True | 30.50% | Selected by latest signal basket | 0.1067289512326055 | 1.1166666666666667 | 0.12 | 0.12 | 0.0871309704513236 | 0.1046813751114046 |
| LIT | 6.79% | -14.215 | False | False | False | False | 35.15% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0564959938272555 | 0.0678757311147645 |
| EWY | 6.32% | 13.365 | False | True | True | True | 78.39% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0526158724078015 | 0.063214054059135 |
| MLPA | 6.30% | 17.634 | True | True | True | True | 15.51% | Selected by latest signal basket | 0.1199999998985533 | 1.0233333333333334 | 0.12 | 0.12 | 0.0523963891211389 | 0.0629503612281841 |
| EWT | 5.91% | 21.439 | False | True | True | True | 42.51% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.049199689296989 | 0.0591097643465352 |
| OIH | 5.74% | 2.363 | False | False | False | True | 30.01% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0477692283948708 | 0.0573911720537926 |
| GLDM | 5.63% | -11.714 | False | False | False | False | 24.26% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0468960161750855 | 0.0563420725721992 |
| EWW | 3.72% | 1.493 | False | False | False | True | 20.51% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0309255878269955 | 0.0371547917243383 |
| AVDV | 3.56% | 8.579 | False | True | True | True | 18.62% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0296475197111324 | 0.0356192880204133 |
| XAR | 3.33% | -7.221 | False | False | False | False | 32.11% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0276969807832798 | 0.0332758606935019 |
| EWP | 3.26% | 14.292 | True | True | True | True | 19.55% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0271601121230919 | 0.0326308529619045 |
| SPYD | 3.24% | 17.285 | True | True | True | True | 12.03% | Selected by latest signal basket | 0.1199999992872728 | 0.9766666666666668 | 0.12 | 0.12 | 0.0269780670216627 | 0.0324121393236747 |
| AVUV | 3.24% | 18.077 | True | True | True | True | 12.82% | Selected by latest signal basket | 0.1171998125380367 | 1.07 | 0.12 | 0.12 | 0.0269780670216627 | 0.0324121393236747 |
| THD | 3.24% | 17.472 | True | True | True | True | 21.98% | Selected by latest signal basket | 0.1199999983264029 | 1.0466666666666666 | 0.12 | 0.12 | 0.0269780670216627 | 0.0324121393236747 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 17.77% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 76.09% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.58% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 15.45% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 73.83% | 22.48% | 16.07% | 1.219 | -13.64% |
| SPY | 83.86% | 25.03% | 15.58% | 1.383 | -18.76% |
| QQQ | 103.33% | 29.73% | 20.67% | 1.266 | -22.77% |
| VTI | 83.76% | 25.01% | 15.73% | 1.371 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| SPYD | AVUV | 0.784 |
| AVDV | EWP | 0.774 |
| EWY | EWT | 0.763 |
| OIH | AVUV | 0.695 |
| EWT | AVDV | 0.671 |
| AVDV | AVUV | 0.650 |
| XAR | AVUV | 0.639 |
| LIT | AVDV | 0.621 |
| EWW | AVDV | 0.616 |
| AVDV | XAR | 0.614 |
| EWY | AVDV | 0.602 |
| MLPA | OIH | 0.597 |
| AVDV | SPYD | 0.579 |
| AVDV | THD | 0.576 |
| LIT | EWT | 0.574 |
| EIS | AVDV | 0.549 |
| EWW | EWP | 0.545 |
| EWT | THD | 0.541 |
| XBI | AVUV | 0.538 |
| LIT | EWY | 0.530 |

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
