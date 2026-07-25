# V5.16 Allocation Explanation Report

Generated at: `2026-07-25T15:30:42`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-24`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| XBI | 11.75% | 1.69% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SGOV | 10.70% | -1.78% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EIS | 8.05% | -1.34% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 7.85% | -1.30% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 7.66% | -1.27% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 6.27% | 2.95% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SPYD | 6.19% | 2.96% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVUV | 6.19% | 2.96% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWT | 5.62% | -0.93% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.37% | -0.89% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| IXC | 5.05% | -0.84% | Carryover / turnover-constrained holding | IXC is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SMH | 5.05% | -0.84% | Carryover / turnover-constrained holding | SMH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 3.98% | -0.66% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| THD | 3.42% | 3.42% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XOP | 3.42% | 3.42% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| KIE | 3.42% | 3.42% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XBI | 11.75% | 17.474 | True | True | True | True | 30.46% | Selected by latest signal basket | 0.106400893730088 | 0.93 | 0.1094270919528046 | 0.1094270919528046 | 0.1028543567010932 | 0.1175216588960399 |
| SGOV | 10.70% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0936846728217165 | 0.1070443539415366 |
| EIS | 8.05% | 0.286 | False | False | False | True | 26.16% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0704663093798295 | 0.0805149907131851 |
| EWY | 7.85% | 5.462 | False | True | True | True | 78.14% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0687224977120213 | 0.0785225069081611 |
| OIH | 7.66% | 3.077 | False | False | False | True | 29.66% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.06700550916043 | 0.0765606712663814 |
| MLPA | 6.27% | 20.028 | True | True | True | True | 15.48% | Selected by latest signal basket | 0.1199999995678443 | 1.1166666666666667 | 0.12 | 0.12 | 0.0548675088146634 | 0.0626917600985181 |
| SPYD | 6.19% | 19.082 | True | True | True | True | 12.20% | Selected by latest signal basket | 0.1199999973891828 | 1.0466666666666666 | 0.12 | 0.12 | 0.0541595333751703 | 0.0618828254964702 |
| AVUV | 6.19% | 17.971 | True | True | True | True | 12.99% | Selected by latest signal basket | 0.119999984839629 | 0.9533333333333334 | 0.12 | 0.12 | 0.0541595333751703 | 0.0618828254964702 |
| EWT | 5.62% | 17.974 | False | True | True | True | 42.15% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0491450665367753 | 0.0561532824782784 |
| GLDM | 5.37% | -11.285 | False | False | False | False | 24.00% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0470344904654756 | 0.0537417326997283 |
| IXC | 5.05% | 21.067 | True | True | True | True | 22.87% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0442022728151421 | 0.0505056333520933 |
| SMH | 5.05% | 14.357 | False | True | True | True | 53.24% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0442022728151421 | 0.0505056333520933 |
| LIT | 3.98% | -15.815 | False | False | False | False | 34.40% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0348679142133427 | 0.0398401706259788 |
| THD | 3.42% | 18.728 | True | True | True | True | 21.14% | Selected by latest signal basket | 0.1199999972425358 | 1.0233333333333334 | 0.12 | 0.12 | 0.0299409878265292 | 0.0342106515583549 |
| XOP | 3.42% | 22.309 | True | True | True | True | 30.28% | Selected by latest signal basket | 0.1199999996439093 | 1.14 | 0.12 | 0.12 | 0.0299409878265292 | 0.0342106515583549 |
| KIE | 3.42% | 19.758 | True | True | True | True | 20.11% | Selected by latest signal basket | 0.1199999993878799 | 1.07 | 0.12 | 0.12 | 0.0299409878265292 | 0.0342106515583549 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 10.70% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 70.82% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.69% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 20.82% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.82% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 80.01% | 24.03% | 16.21% | 1.287 | -14.97% |
| SPY | 80.42% | 24.13% | 15.59% | 1.336 | -18.76% |
| QQQ | 93.57% | 27.37% | 20.70% | 1.176 | -22.77% |
| VTI | 80.49% | 24.15% | 15.72% | 1.327 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| IXC | XOP | 0.916 |
| OIH | IXC | 0.830 |
| OIH | XOP | 0.815 |
| SPYD | AVUV | 0.784 |
| EWT | SMH | 0.776 |
| EWY | EWT | 0.759 |
| OIH | AVUV | 0.695 |
| MLPA | IXC | 0.682 |
| MLPA | XOP | 0.669 |
| SPYD | KIE | 0.655 |
| EWY | SMH | 0.646 |
| AVUV | KIE | 0.602 |
| AVUV | XOP | 0.602 |
| OIH | MLPA | 0.596 |
| EWT | LIT | 0.573 |
| EWT | THD | 0.539 |
| AVUV | IXC | 0.539 |
| XBI | AVUV | 0.537 |
| EIS | SMH | 0.536 |
| EWY | LIT | 0.530 |

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
