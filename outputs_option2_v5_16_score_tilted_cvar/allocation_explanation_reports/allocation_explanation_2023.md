# V5.16 Allocation Explanation Report

Generated at: `2026-07-09T20:51:20`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-09`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| MLPA | 11.31% | 2.48% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EIS | 10.27% | -1.42% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 9.70% | 2.70% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XBI | 7.66% | 2.98% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 7.58% | -1.04% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| DIV | 7.51% | -1.03% | Carryover / turnover-constrained holding | DIV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.21% | -0.86% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SMH | 6.15% | -0.85% | Carryover / turnover-constrained holding | SMH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.61% | -0.77% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 5.43% | -0.75% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 5.20% | -0.72% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| IXC | 4.45% | -0.61% | Carryover / turnover-constrained holding | IXC is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 3.55% | 3.55% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVUV | 3.55% | 3.55% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| KIE | 3.55% | 3.55% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SGOV | 2.29% | -0.32% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MLPA | 11.31% | 13.987 | True | True | True | True | 15.07% | Selected by latest signal basket | 0.1199999999421932 | 0.9066666666666668 | 0.12 | 0.12 | 0.0962779806531621 | 0.1130687471123456 |
| EIS | 10.27% | -2.125 | False | False | False | True | 26.23% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0874787439969132 | 0.1027349339442937 |
| EWT | 9.70% | 30.118 | True | True | True | True | 39.84% | Selected by latest signal basket | 0.1199999997916076 | 1.163333333333333 | 0.12 | 0.12 | 0.0825565802172926 | 0.0969543505973247 |
| XBI | 7.66% | 27.64 | True | True | True | True | 29.26% | Selected by latest signal basket | 0.1199999999530853 | 1.1166666666666667 | 0.12 | 0.12 | 0.0652406670334234 | 0.0766185625435697 |
| OIH | 7.58% | -0.93 | False | False | False | True | 29.97% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0645024584602818 | 0.0757516112645081 |
| DIV | 7.51% | 12.903 | True | True | True | True | 11.63% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0639222708363311 | 0.0750702396021079 |
| EWY | 6.21% | 23.777 | False | True | True | True | 74.36% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0528587112361293 | 0.062077208234904 |
| SMH | 6.15% | 28.159 | True | True | True | True | 50.38% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0523640187665963 | 0.0614962419811817 |
| GLDM | 5.61% | -10.252 | False | False | False | False | 23.80% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0477847791145586 | 0.0561183883258551 |
| LIT | 5.43% | -4.068 | False | False | False | True | 34.50% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.046268842802822 | 0.0543380745063574 |
| TUR | 5.20% | -0.993 | False | False | False | True | 31.99% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0442546377655512 | 0.0519725944823005 |
| IXC | 4.45% | 2.944 | False | False | False | True | 23.36% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0379202662210783 | 0.0445335159991549 |
| CIBR | 3.55% | 27.383 | True | True | True | True | 34.51% | Selected by latest signal basket | 0.1199999991077298 | 1.14 | 0.12 | 0.12 | 0.0301925614506963 | 0.035458108616143 |
| AVUV | 3.55% | 15.492 | True | True | True | True | 12.99% | Selected by latest signal basket | 0.119999999605223 | 1.0466666666666666 | 0.12 | 0.12 | 0.0301925614506963 | 0.035458108616143 |
| KIE | 3.55% | 15.958 | True | True | True | True | 18.76% | Selected by latest signal basket | 0.1199999997748127 | 0.9533333333333334 | 0.1199999999999999 | 0.1199999999999999 | 0.0301925614506963 | 0.035458108616143 |
| SGOV | 2.29% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0194918498886242 | 0.0228912055576673 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 2.29% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 78.51% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 12.50% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 18.79% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 88.54% | 26.15% | 16.43% | 1.374 | -14.45% |
| SPY | 79.86% | 23.99% | 15.61% | 1.327 | -18.76% |
| QQQ | 100.47% | 29.01% | 20.61% | 1.242 | -22.77% |
| VTI | 79.64% | 23.93% | 15.77% | 1.313 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| OIH | IXC | 0.834 |
| DIV | AVUV | 0.779 |
| EWT | SMH | 0.774 |
| EWT | EWY | 0.764 |
| OIH | AVUV | 0.697 |
| MLPA | IXC | 0.683 |
| EWY | SMH | 0.641 |
| DIV | KIE | 0.634 |
| MLPA | DIV | 0.613 |
| AVUV | KIE | 0.609 |
| SMH | CIBR | 0.605 |
| MLPA | OIH | 0.602 |
| OIH | DIV | 0.584 |
| DIV | IXC | 0.584 |
| EWT | LIT | 0.570 |
| IXC | AVUV | 0.543 |
| XBI | AVUV | 0.543 |
| EIS | SMH | 0.537 |
| CIBR | AVUV | 0.529 |
| EWT | CIBR | 0.526 |

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
