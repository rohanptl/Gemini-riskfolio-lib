# V5.16 Allocation Explanation Report

Generated at: `2026-07-20T09:39:21`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-17`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| EIS | 11.93% | -2.22% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 10.56% | 2.10% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SGOV | 9.19% | -1.71% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| THD | 8.43% | 2.49% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 7.06% | -1.31% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 6.56% | -1.22% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 6.19% | 2.91% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XOP | 6.19% | 2.91% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 5.60% | -1.04% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 5.42% | -1.01% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 5.02% | -0.94% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.38% | -0.82% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 3.43% | 3.43% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| KIE | 3.43% | 3.43% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SPYD | 3.36% | 3.36% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| DIV | 3.27% | 3.27% | Selected by latest signal basket | DIV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EIS | 11.93% | -0.332 | False | False | False | True | 26.70% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.1057522828896188 | 0.1193421636679346 |
| XBI | 10.56% | 21.413 | True | True | True | True | 30.26% | Selected by latest signal basket | 0.1199999994531909 | 1.1166666666666667 | 0.1199999999999999 | 0.1199999999999999 | 0.0935685933424149 | 0.105592787935409 |
| SGOV | 9.19% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.0813987596764307 | 0.0918590486581834 |
| THD | 8.43% | 18.03 | True | True | True | True | 22.54% | Selected by latest signal basket | 0.1199999994664385 | 1.0933333333333333 | 0.1199999999999999 | 0.1199999999999999 | 0.074709316341362 | 0.0843099667894315 |
| LIT | 7.06% | -13.432 | False | False | False | False | 34.27% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0625356576955262 | 0.0705719109966755 |
| AVDV | 6.56% | 2.361 | False | False | False | True | 18.40% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0581202795388879 | 0.0655891270015975 |
| MLPA | 6.19% | 18.497 | True | True | True | True | 15.54% | Selected by latest signal basket | 0.1199999997039745 | 1.0 | 0.12 | 0.12 | 0.0548098579611349 | 0.061853293949611 |
| XOP | 6.19% | 21.984 | True | True | True | True | 31.98% | Selected by latest signal basket | 0.1199999996180949 | 1.14 | 0.1199999999999999 | 0.1199999999999999 | 0.0548098579611349 | 0.061853293949611 |
| EWY | 5.60% | 9.337 | False | True | True | True | 77.68% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0496186177229351 | 0.0559949443686997 |
| OIH | 5.42% | 2.973 | False | False | False | True | 29.85% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0480438067917946 | 0.0542177596237955 |
| EWT | 5.02% | 20.709 | False | True | True | True | 41.46% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0445018105103565 | 0.0502205929586389 |
| TUR | 4.38% | -1.466 | False | False | False | True | 32.09% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0387960776578632 | 0.0437816349964878 |
| AVUV | 3.43% | 18.671 | True | True | True | True | 13.00% | Selected by latest signal basket | 0.1199999929133057 | 1.0233333333333334 | 0.12 | 0.12 | 0.0303586851255174 | 0.0342599806831069 |
| KIE | 3.43% | 18.482 | True | True | True | True | 19.56% | Selected by latest signal basket | 0.1199999994357756 | 0.9766666666666668 | 0.12 | 0.12 | 0.0303586851255174 | 0.0342599806831068 |
| SPYD | 3.36% | 18.158 | True | True | True | True | 12.03% | Selected by latest signal basket | 0.1199999993243099 | 0.93 | 0.1175757547106306 | 0.1175757547106306 | 0.0297453776304592 | 0.0335678590432326 |
| DIV | 3.27% | 17.188 | True | True | True | True | 12.06% | Selected by latest signal basket | 0.1199999996785743 | 0.9066666666666668 | 0.1146258253809732 | 0.1146258253809732 | 0.0289990778332792 | 0.0327256546944777 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 9.19% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 71.98% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.29% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 23.90% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 3.90% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 87.44% | 25.88% | 17.38% | 1.297 | -15.29% |
| SPY | 76.33% | 23.09% | 15.62% | 1.280 | -18.76% |
| QQQ | 91.87% | 26.96% | 20.67% | 1.161 | -22.77% |
| VTI | 75.86% | 22.97% | 15.77% | 1.264 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| SPYD | DIV | 0.903 |
| XOP | OIH | 0.816 |
| AVUV | SPYD | 0.785 |
| AVUV | DIV | 0.779 |
| EWY | EWT | 0.761 |
| OIH | AVUV | 0.695 |
| MLPA | XOP | 0.671 |
| AVDV | EWT | 0.670 |
| KIE | SPYD | 0.657 |
| AVDV | AVUV | 0.650 |
| KIE | DIV | 0.631 |
| LIT | AVDV | 0.619 |
| MLPA | DIV | 0.613 |
| AVUV | KIE | 0.605 |
| XOP | AVUV | 0.602 |
| AVDV | EWY | 0.600 |
| MLPA | OIH | 0.598 |
| AVDV | DIV | 0.586 |
| OIH | DIV | 0.581 |
| AVDV | SPYD | 0.581 |

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
