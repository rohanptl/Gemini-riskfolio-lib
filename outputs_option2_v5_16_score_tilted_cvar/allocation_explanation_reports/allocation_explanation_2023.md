# V5.16 Allocation Explanation Report

Generated at: `2026-07-08T00:59:21`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-01`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 18.74% | -3.04% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EIS | 9.54% | -1.55% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 8.48% | 2.48% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XBI | 7.68% | 2.61% | Selected by latest signal basket | XBI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 6.61% | -1.07% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 6.47% | -1.05% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 6.17% | 2.85% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| CIBR | 5.90% | 2.59% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 5.17% | -0.84% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 5.14% | -0.83% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 3.50% | -0.57% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 3.47% | -0.56% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.33% | -0.54% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XLI | 3.32% | 3.32% | Selected by latest signal basket | XLI received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| JETS | 3.32% | 3.32% | Selected by latest signal basket | JETS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| KIE | 3.18% | 3.18% | Selected by latest signal basket | KIE received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 18.74% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.164871479184601 | 0.1874326692544916 |
| EIS | 9.54% | 2.549 | False | False | True | True | 26.55% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0839589682107113 | 0.0954480034837731 |
| EWT | 8.48% | 29.696 | True | True | True | True | 39.74% | Selected by latest signal basket | 0.1199999996312146 | 1.163333333333333 | 0.12 | 0.12 | 0.0746012574532112 | 0.0848097735481644 |
| XBI | 7.68% | 22.751 | True | True | True | True | 28.81% | Selected by latest signal basket | 0.119999999921218 | 1.14 | 0.12 | 0.12 | 0.0675558112243056 | 0.0768002208996181 |
| OIH | 6.61% | -0.487 | False | False | False | True | 29.59% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0581148375204109 | 0.0660673342267136 |
| EWY | 6.47% | 24.609 | False | True | True | True | 75.61% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0569333618741241 | 0.0647241841856154 |
| AVUV | 6.17% | 17.252 | True | True | True | True | 13.32% | Selected by latest signal basket | 0.1199999997684997 | 1.0466666666666666 | 0.12 | 0.12 | 0.0542363538612984 | 0.0616581147032238 |
| CIBR | 5.90% | 19.833 | True | True | True | True | 33.91% | Selected by latest signal basket | 0.0958862858357776 | 1.1166666666666667 | 0.1103229922806487 | 0.1103229922806487 | 0.0518847226952734 | 0.0589846838058362 |
| LIT | 5.17% | 7.088 | False | True | True | True | 34.45% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0454397905920567 | 0.0516578202801118 |
| GLDM | 5.14% | -10.844 | False | False | False | False | 23.75% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0452165867124066 | 0.0514040729421387 |
| TUR | 3.50% | 4.555 | False | False | True | True | 33.18% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0307769178444111 | 0.0349884642967584 |
| AVDV | 3.47% | 8.214 | False | True | True | True | 19.39% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0305094454798988 | 0.0346843907269677 |
| XAR | 3.33% | 12.407 | True | True | True | True | 31.91% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0292646235287261 | 0.0332692260046712 |
| XLI | 3.32% | 15.493 | True | True | True | True | 20.84% | Selected by latest signal basket | 0.119999998527489 | 0.9766666666666668 | 0.12 | 0.12 | 0.0291614668611545 | 0.0331519532680525 |
| JETS | 3.32% | 19.113 | True | True | True | True | 38.30% | Selected by latest signal basket | 0.1115119210308254 | 1.07 | 0.12 | 0.12 | 0.0291614668611545 | 0.0331519532680525 |
| KIE | 3.18% | 14.748 | True | True | True | True | 18.40% | Selected by latest signal basket | 0.1199999997482033 | 0.93 | 0.11498737892982 | 0.11498737892982 | 0.027943338667608 | 0.0317671351058103 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 18.74% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 81.46% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 14.73% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 20.33% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.33% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 75.10% | 22.74% | 15.37% | 1.281 | -13.79% |
| SPY | 82.12% | 24.52% | 15.61% | 1.354 | -18.76% |
| QQQ | 100.35% | 28.94% | 20.60% | 1.240 | -22.77% |
| VTI | 81.93% | 24.47% | 15.77% | 1.340 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| AVUV | XLI | 0.802 |
| XAR | XLI | 0.796 |
| EWT | EWY | 0.764 |
| AVUV | JETS | 0.705 |
| OIH | AVUV | 0.699 |
| XLI | JETS | 0.694 |
| AVDV | XLI | 0.686 |
| EWT | AVDV | 0.670 |
| AVUV | AVDV | 0.652 |
| AVUV | XAR | 0.645 |
| LIT | AVDV | 0.618 |
| AVDV | XAR | 0.613 |
| AVUV | KIE | 0.609 |
| EWY | AVDV | 0.604 |
| EWT | XLI | 0.584 |
| AVDV | JETS | 0.573 |
| XAR | JETS | 0.573 |
| EWT | LIT | 0.572 |
| XLI | KIE | 0.564 |
| OIH | XLI | 0.556 |

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
