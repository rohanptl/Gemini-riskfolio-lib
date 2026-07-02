# V5.16 Allocation Explanation Report

Generated at: `2026-07-02T01:32:05`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-01`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 20.60% | -3.32% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EWT | 8.51% | 2.52% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EIS | 8.34% | -1.34% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 8.12% | 2.58% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.48% | -1.04% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 6.26% | 2.88% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| CIBR | 5.99% | 2.61% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| GLDM | 5.59% | -0.90% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 5.16% | -0.83% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 4.56% | -0.73% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.62% | -0.58% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWP | 3.50% | -0.56% | Carryover / turnover-constrained holding | EWP is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| JETS | 3.35% | 3.35% | Selected by latest signal basket | JETS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XLI | 3.35% | 3.35% | Selected by latest signal basket | XLI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| AVDV | 3.33% | -0.54% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XME | 3.23% | -0.52% | Carryover / turnover-constrained holding | XME is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 20.60% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.1806191230364789 | 0.2059940223789522 |
| EWT | 8.51% | 29.72 | True | True | True | True | 39.74% | Selected by latest signal basket | 0.1199999995981568 | 1.163333333333333 | 0.12 | 0.12 | 0.0746449501324902 | 0.0851317029424534 |
| EIS | 8.34% | 2.517 | False | False | True | True | 26.55% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0731185594108403 | 0.0833908719651539 |
| XBI | 8.12% | 22.742 | True | True | True | True | 28.81% | Selected by latest signal basket | 0.1199999999145891 | 1.14 | 0.12 | 0.12 | 0.0712166228070585 | 0.0812217352495269 |
| OIH | 6.48% | -0.517 | False | False | False | True | 29.59% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0568229449126946 | 0.0648059119610471 |
| AVUV | 6.26% | 17.229 | True | True | True | True | 13.32% | Selected by latest signal basket | 0.1199999997443859 | 1.0466666666666666 | 0.12 | 0.12 | 0.0549170668013485 | 0.0626322800015957 |
| CIBR | 5.99% | 19.835 | True | True | True | True | 33.91% | Selected by latest signal basket | 0.0958859249479957 | 1.1166666666666667 | 0.1103228444879532 | 0.1103228444879532 | 0.0525481500666327 | 0.0599305578436026 |
| GLDM | 5.59% | -10.895 | False | False | False | False | 23.75% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0489782197002244 | 0.0558590935189714 |
| LIT | 5.16% | 7.064 | False | True | True | True | 34.45% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0452695817391622 | 0.0516294347857032 |
| EWY | 4.56% | 24.652 | False | True | True | True | 75.61% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0399961247728337 | 0.0456151180617929 |
| XAR | 3.62% | 12.385 | True | True | True | True | 31.91% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0317486912507593 | 0.036209015446778 |
| EWP | 3.50% | 12.937 | True | True | True | True | 20.49% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0306522925447258 | 0.0349585853938023 |
| JETS | 3.35% | 19.106 | True | True | True | True | 38.30% | Selected by latest signal basket | 0.1115129244743962 | 1.07 | 0.12 | 0.1199999999999999 | 0.029375368393328 | 0.0335022681567502 |
| XLI | 3.35% | 15.47 | True | True | True | True | 20.84% | Selected by latest signal basket | 0.1199999987384766 | 0.9766666666666668 | 0.12 | 0.1199999999999999 | 0.029375368393328 | 0.0335022681567502 |
| AVDV | 3.33% | 8.181 | False | True | True | True | 19.39% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0291769922972515 | 0.0332760225118393 |
| XME | 3.23% | -12.292 | False | False | False | False | 39.26% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0283572462556067 | 0.0323411116252797 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 20.60% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 82.62% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 14.73% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 17.29% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 68.92% | 21.24% | 15.42% | 1.197 | -13.79% |
| SPY | 81.64% | 24.52% | 15.63% | 1.353 | -18.76% |
| QQQ | 104.80% | 30.13% | 20.56% | 1.286 | -22.77% |
| VTI | 81.76% | 24.54% | 15.79% | 1.342 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| AVUV | XLI | 0.803 |
| XAR | XLI | 0.795 |
| EWP | AVDV | 0.774 |
| EWT | EWY | 0.762 |
| AVUV | JETS | 0.705 |
| OIH | AVUV | 0.700 |
| JETS | XLI | 0.694 |
| AVDV | XME | 0.693 |
| AVUV | XME | 0.687 |
| XLI | AVDV | 0.685 |
| EWT | AVDV | 0.669 |
| AVUV | AVDV | 0.654 |
| XLI | XME | 0.652 |
| XAR | XME | 0.649 |
| AVUV | XAR | 0.647 |
| LIT | AVDV | 0.619 |
| XAR | AVDV | 0.610 |
| EWY | AVDV | 0.603 |
| LIT | XME | 0.599 |
| EWT | XLI | 0.582 |

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
