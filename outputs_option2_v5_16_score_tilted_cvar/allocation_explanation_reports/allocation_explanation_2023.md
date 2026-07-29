# V5.16 Allocation Explanation Report

Generated at: `2026-07-29T15:39:04`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-29`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 17.81% | -1.69% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| AVUV | 8.80% | 2.70% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 8.16% | -0.78% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EIS | 7.91% | -0.75% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 7.71% | -0.73% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XLE | 6.16% | 2.96% | Selected by latest signal basket | XLE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVDV | 6.11% | -0.58% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.79% | -0.55% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 5.57% | -0.53% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 4.80% | -0.46% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 4.61% | -0.44% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SPYD | 3.66% | 0.51% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWS | 3.23% | 3.23% | Selected by latest signal basket | EWS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| DIV | 3.23% | 3.23% | Selected by latest signal basket | DIV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| MLPA | 3.23% | 3.23% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| KIE | 3.23% | 3.23% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 17.81% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.1505626918936985 | 0.178055565614446 |
| AVUV | 8.80% | 18.291 | True | True | True | True | 13.13% | Selected by latest signal basket | 0.1199999575276198 | 1.0466666666666666 | 0.12 | 0.12 | 0.0743995330208588 | 0.0879849501019323 |
| EWY | 8.16% | -9.03 | False | False | False | True | 79.26% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0689906096205789 | 0.081588352755745 |
| EIS | 7.91% | -6.234 | False | False | False | False | 26.52% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0668649838227071 | 0.0790745859057743 |
| EWT | 7.71% | 10.145 | False | True | True | True | 42.88% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0651913892908893 | 0.0770953916098697 |
| XLE | 6.16% | 18.259 | True | True | True | True | 24.82% | Selected by latest signal basket | 0.1199999971168948 | 1.0699999999999998 | 0.12 | 0.12 | 0.0520725432718772 | 0.061581033313372 |
| AVDV | 6.11% | 3.074 | False | False | False | True | 18.45% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0516451702510251 | 0.061075621620747 |
| GLDM | 5.79% | -12.358 | False | False | False | False | 23.91% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0489294253452436 | 0.0578639794192056 |
| CIBR | 5.57% | 24.897 | True | True | True | True | 32.26% | Selected by latest signal basket | 2.9760614874743296e-08 | 1.163333333333333 | 0.0 | 0.0 | 0.047059879359014 | 0.0556530527690939 |
| LIT | 4.80% | -15.658 | False | False | False | False | 34.26% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0406009339593485 | 0.0480146985264491 |
| OIH | 4.61% | -1.303 | False | False | False | True | 29.98% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0389866972729586 | 0.046105700868293 |
| SPYD | 3.66% | 21.066 | True | True | True | True | 12.22% | Selected by latest signal basket | 0.0254508687622695 | 1.0933333333333333 | 0.0291788104127258 | 0.0291788104127258 | 0.0309313819053647 | 0.0365794781637181 |
| EWS | 3.23% | 22.386 | True | True | True | True | 16.27% | Selected by latest signal basket | 0.1199999854463101 | 1.14 | 0.12 | 0.12 | 0.0273396536618447 | 0.0323318973328383 |
| DIV | 3.23% | 19.135 | True | True | True | True | 11.94% | Selected by latest signal basket | 0.1199999917608791 | 1.0 | 0.12 | 0.12 | 0.0273396536618447 | 0.0323318973328383 |
| MLPA | 3.23% | 18.724 | True | True | True | True | 15.85% | Selected by latest signal basket | 0.1199999964266865 | 1.0233333333333332 | 0.12 | 0.12 | 0.0273396536618447 | 0.0323318973328383 |
| KIE | 3.23% | 21.732 | True | True | True | True | 20.67% | Selected by latest signal basket | 0.1199999928393909 | 1.1166666666666667 | 0.12 | 0.12 | 0.0273396536618447 | 0.0323318973328383 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 17.81% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 68.86% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 9.36% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 19.10% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 67.36% | 20.76% | 16.20% | 1.123 | -12.88% |
| SPY | 85.04% | 25.28% | 15.55% | 1.399 | -18.76% |
| QQQ | 96.31% | 28.03% | 20.63% | 1.204 | -22.77% |
| VTI | 85.14% | 25.31% | 15.69% | 1.389 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| SPYD | DIV | 0.903 |
| XLE | OIH | 0.830 |
| AVUV | SPYD | 0.783 |
| AVUV | DIV | 0.778 |
| EWY | EWT | 0.762 |
| AVDV | EWS | 0.720 |
| AVUV | OIH | 0.693 |
| XLE | MLPA | 0.684 |
| EWT | AVDV | 0.670 |
| SPYD | KIE | 0.656 |
| AVUV | AVDV | 0.650 |
| DIV | KIE | 0.630 |
| AVDV | LIT | 0.619 |
| DIV | MLPA | 0.611 |
| AVUV | KIE | 0.602 |
| EWY | AVDV | 0.595 |
| OIH | MLPA | 0.591 |
| EWT | EWS | 0.591 |
| AVDV | DIV | 0.584 |
| AVDV | SPYD | 0.578 |

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
