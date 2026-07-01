# V5.16 Allocation Explanation Report

Generated at: `2026-07-01T16:39:21`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-01`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 20.64% | -3.42% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EWT | 8.46% | 2.49% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EIS | 8.27% | -1.37% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 8.22% | 2.53% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.41% | -1.06% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 6.24% | 2.86% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| CIBR | 5.97% | 2.59% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| GLDM | 5.63% | -0.93% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 5.12% | -0.85% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 4.57% | -0.76% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.61% | -0.60% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWP | 3.61% | -0.60% | Carryover / turnover-constrained holding | EWP is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| JETS | 3.34% | 3.34% | Selected by latest signal basket | JETS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XLI | 3.34% | 3.34% | Selected by latest signal basket | XLI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XME | 3.34% | -0.55% | Carryover / turnover-constrained holding | XME is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| KIE | 3.20% | 3.20% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 20.64% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.1816436741894566 | 0.206399530488305 |
| EWT | 8.46% | 29.562 | True | True | True | True | 39.53% | Selected by latest signal basket | 0.119999999361976 | 1.163333333333333 | 0.12 | 0.12 | 0.0744616221965084 | 0.0846098490868831 |
| EIS | 8.27% | 2.895 | False | False | True | True | 26.63% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0727578317185937 | 0.0826738523820088 |
| XBI | 8.22% | 22.786 | True | True | True | True | 28.73% | Selected by latest signal basket | 0.1199999998578779 | 1.14 | 0.12 | 0.12 | 0.0723815278025428 | 0.0822462627511539 |
| OIH | 6.41% | 0.069 | False | False | False | True | 29.12% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0564237398116329 | 0.0641136194666959 |
| AVUV | 6.24% | 17.538 | True | True | True | True | 13.30% | Selected by latest signal basket | 0.1199999995530467 | 1.0466666666666666 | 0.12 | 0.12 | 0.0549421515183697 | 0.0624301084417673 |
| CIBR | 5.97% | 19.678 | True | True | True | True | 33.99% | Selected by latest signal basket | 0.0958862213911349 | 1.1166666666666667 | 0.1103230718111819 | 0.1103230718111819 | 0.0525697405678167 | 0.059734366305387 |
| GLDM | 5.63% | -10.614 | False | False | False | False | 23.98% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0495841720043239 | 0.0563419005204082 |
| LIT | 5.12% | 7.058 | False | True | True | True | 34.43% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0450422332632179 | 0.0511809499513664 |
| EWY | 4.57% | 27.142 | True | True | True | True | 74.98% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0402434988802898 | 0.0457282055715022 |
| XAR | 3.61% | 13.097 | True | True | True | True | 32.12% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0317899864281164 | 0.0361225806638834 |
| EWP | 3.61% | 12.555 | True | True | True | True | 20.50% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0317844783830962 | 0.0361163219383256 |
| JETS | 3.34% | 19.586 | True | True | True | True | 38.31% | Selected by latest signal basket | 0.1115125414995355 | 1.07 | 0.12 | 0.12 | 0.0294193889332905 | 0.0334288991355166 |
| XLI | 3.34% | 15.871 | True | True | True | True | 20.70% | Selected by latest signal basket | 0.1199999996834504 | 1.0 | 0.12 | 0.12 | 0.0294193889332905 | 0.0334288991355166 |
| XME | 3.34% | -7.997 | False | False | False | True | 38.98% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0294046023658529 | 0.0334120973361131 |
| KIE | 3.20% | 14.656 | True | True | True | True | 18.57% | Selected by latest signal basket | 0.1199999994252594 | 0.93 | 0.1149875382804925 | 0.1149875382804925 | 0.0281905259262953 | 0.0320325568251662 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 20.64% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 83.78% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 14.71% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 20.37% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.37% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 68.06% | 21.01% | 15.43% | 1.184 | -13.79% |
| SPY | 82.38% | 24.70% | 15.63% | 1.362 | -18.76% |
| QQQ | 105.94% | 30.39% | 20.55% | 1.297 | -22.77% |
| VTI | 82.65% | 24.77% | 15.79% | 1.354 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| AVUV | XLI | 0.803 |
| XAR | XLI | 0.795 |
| EWT | EWY | 0.762 |
| AVUV | JETS | 0.705 |
| OIH | AVUV | 0.700 |
| JETS | XLI | 0.694 |
| AVUV | XME | 0.687 |
| XLI | XME | 0.651 |
| XAR | XME | 0.649 |
| AVUV | XAR | 0.647 |
| AVUV | KIE | 0.615 |
| LIT | XME | 0.599 |
| EWT | XLI | 0.581 |
| XAR | JETS | 0.572 |
| EWT | LIT | 0.571 |
| XLI | KIE | 0.571 |
| EWT | XME | 0.564 |
| OIH | XLI | 0.558 |
| OIH | XME | 0.550 |
| XBI | AVUV | 0.545 |

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
