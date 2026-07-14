# V5.16 Allocation Explanation Report

Generated at: `2026-07-14T22:21:45`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-14`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| THD | 10.20% | 2.25% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EIS | 10.19% | -1.88% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 9.64% | 2.57% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWT | 9.17% | 2.66% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 7.87% | -1.45% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SGOV | 6.15% | -1.14% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| SPYD | 6.11% | 2.81% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 6.07% | -1.12% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.29% | -0.98% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| IXC | 5.09% | -0.94% | Carryover / turnover-constrained holding | IXC is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 4.87% | -0.90% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWP | 4.39% | -0.81% | Carryover / turnover-constrained holding | EWP is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.09% | -0.76% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 3.67% | 3.67% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XOP | 3.67% | 3.67% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVDV | 3.52% | -0.65% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| THD | 10.20% | 15.547 | True | True | True | True | 23.05% | Selected by latest signal basket | 0.1169864173268793 | 0.9066666666666668 | 0.1141750759720443 | 0.1141750759720443 | 0.0887282325210308 | 0.1020460537794533 |
| EIS | 10.19% | -2.641 | False | False | False | True | 26.32% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0886312747766682 | 0.1019345429906723 |
| XBI | 9.64% | 23.254 | True | True | True | True | 30.07% | Selected by latest signal basket | 0.1199999997191247 | 1.1166666666666667 | 0.12 | 0.12 | 0.0838474407074197 | 0.0964326708713691 |
| EWT | 9.17% | 26.695 | True | True | True | True | 40.83% | Selected by latest signal basket | 0.1199999927999424 | 1.14 | 0.12 | 0.12 | 0.0797425572988987 | 0.0917116577150997 |
| OIH | 7.87% | 1.759 | False | False | False | True | 30.17% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0684689593552689 | 0.0787459291148946 |
| SGOV | 6.15% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0534595171192237 | 0.0614836180544773 |
| SPYD | 6.11% | 15.147 | True | True | True | True | 11.56% | Selected by latest signal basket | 0.1143248067543468 | 0.8833333333333333 | 0.1087059495771713 | 0.1087059495771713 | 0.0531485491115981 | 0.0611259747528108 |
| EWY | 6.07% | 16.988 | False | True | True | True | 77.08% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0527607087403368 | 0.0606799207938954 |
| GLDM | 5.29% | -11.456 | False | False | False | False | 24.40% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.045977635656197 | 0.0528787303377457 |
| IXC | 5.09% | 11.967 | True | True | False | True | 24.15% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0442466491478477 | 0.0508879283426688 |
| LIT | 4.87% | -7.107 | False | False | False | True | 34.59% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0423142001824519 | 0.0486654250261276 |
| EWP | 4.39% | 13.146 | True | True | True | True | 19.75% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.038186811426563 | 0.0439185285425048 |
| TUR | 4.09% | -1.701 | False | False | False | True | 31.90% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0355338794175407 | 0.0408674000034373 |
| MLPA | 3.67% | 16.206 | True | True | True | True | 15.43% | Selected by latest signal basket | 0.119999999593605 | 0.9766666666666668 | 0.12 | 0.12 | 0.0319315426800723 | 0.0367243641511649 |
| XOP | 3.67% | 16.276 | True | True | True | True | 32.52% | Selected by latest signal basket | 0.1199999994272716 | 0.93 | 0.12 | 0.12 | 0.0319315426800723 | 0.0367243641511649 |
| AVDV | 3.52% | 5.587 | False | True | False | True | 18.22% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0305825494328487 | 0.0351728913725127 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 6.15% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 77.35% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.94% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 17.64% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 78.80% | 23.76% | 17.19% | 1.210 | -14.24% |
| SPY | 80.22% | 24.12% | 15.62% | 1.333 | -18.76% |
| QQQ | 100.17% | 28.99% | 20.65% | 1.239 | -22.77% |
| VTI | 80.15% | 24.10% | 15.77% | 1.321 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| IXC | XOP | 0.917 |
| OIH | IXC | 0.832 |
| OIH | XOP | 0.817 |
| EWP | AVDV | 0.774 |
| EWT | EWY | 0.763 |
| IXC | MLPA | 0.684 |
| MLPA | XOP | 0.671 |
| EWT | AVDV | 0.668 |
| LIT | AVDV | 0.619 |
| EWY | AVDV | 0.602 |
| OIH | MLPA | 0.600 |
| SPYD | AVDV | 0.585 |
| THD | AVDV | 0.579 |
| EWT | LIT | 0.570 |
| EIS | AVDV | 0.546 |
| THD | EWT | 0.546 |
| EWY | LIT | 0.526 |
| EWT | EWP | 0.526 |
| SPYD | EWP | 0.521 |
| SPYD | MLPA | 0.521 |

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
