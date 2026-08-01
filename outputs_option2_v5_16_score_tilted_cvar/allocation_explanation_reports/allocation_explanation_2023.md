# V5.16 Allocation Explanation Report

Generated at: `2026-08-01T14:20:06`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-07-31`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 16.67% | -1.96% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| AVUV | 8.74% | 2.58% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EIS | 7.62% | -0.90% | Carryover / turnover-constrained holding | EIS is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWT | 7.54% | -0.89% | Carryover / turnover-constrained holding | EWT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| THD | 6.99% | 2.78% | Selected by latest signal basket | THD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWY | 6.19% | -0.73% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| OIH | 6.17% | -0.73% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| SPYD | 5.94% | 2.91% | Selected by latest signal basket | SPYD received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XBI | 5.83% | -0.69% | Carryover / turnover-constrained holding | XBI is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 5.20% | -0.61% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| CIBR | 4.97% | -0.58% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| LIT | 4.50% | -0.53% | Carryover / turnover-constrained holding | LIT is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| GLDM | 3.83% | -0.45% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XLE | 3.37% | -0.40% | Carryover / turnover-constrained holding | XLE is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| MLPA | 3.22% | 3.22% | Selected by latest signal basket | MLPA received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| XOP | 3.22% | 3.22% | Selected by latest signal basket | XOP received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 16.67% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.0 | 0.1432998384702949 | 0.1667265472156917 |
| AVUV | 8.74% | 17.527 | True | True | True | True | 12.79% | Selected by latest signal basket | 0.1199999986014865 | 1.0 | 0.12 | 0.12 | 0.0751304851623866 | 0.087412843695292 |
| EIS | 7.62% | -1.946 | False | False | False | True | 26.94% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0655274033879824 | 0.0762398466844946 |
| EWT | 7.54% | 17.275 | False | True | True | True | 44.26% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0647626127858831 | 0.0753500278417647 |
| THD | 6.99% | 17.671 | True | True | True | True | 20.84% | Selected by latest signal basket | 0.11999999898955 | 1.0233333333333334 | 0.12 | 0.12 | 0.0600470012301257 | 0.0698635064255886 |
| EWY | 6.19% | -3.443 | False | False | False | True | 82.65% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0531659781172954 | 0.0618575711980245 |
| OIH | 6.17% | 1.778 | False | False | False | True | 30.72% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.053028393485501 | 0.0616974941815122 |
| SPYD | 5.94% | 17.281 | True | True | True | True | 12.27% | Selected by latest signal basket | 0.1199999991087719 | 0.93 | 0.12 | 0.12 | 0.0510407669220679 | 0.0593849297179865 |
| XBI | 5.83% | 14.888 | True | True | True | True | 30.91% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.050073805724026 | 0.0582598893581225 |
| AVDV | 5.20% | 9.376 | False | True | True | True | 18.62% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0446592617540695 | 0.0519601738071832 |
| CIBR | 4.97% | 29.484 | True | True | True | True | 32.35% | Selected by latest signal basket | 3.015784035589006e-09 | 1.163333333333333 | 0.0 | 0.0 | 0.0427212298823598 | 0.0497053117932871 |
| LIT | 4.50% | -14.011 | False | False | False | False | 34.53% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.038696534877927 | 0.0450226582128755 |
| GLDM | 3.83% | -12.187 | False | False | False | False | 24.04% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0329535997148953 | 0.0383408659593948 |
| XLE | 3.37% | 19.288 | True | True | True | True | 24.22% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0289541948900522 | 0.0336876370061598 |
| MLPA | 3.22% | 18.459 | True | True | True | True | 15.53% | Selected by latest signal basket | 0.1199999997220612 | 1.0466666666666666 | 0.12 | 0.12 | 0.0277145619678277 | 0.0322453484513109 |
| XOP | 3.22% | 21.993 | True | True | True | True | 31.05% | Selected by latest signal basket | 0.1199999997883752 | 1.14 | 0.12 | 0.12 | 0.0277145619678277 | 0.0322453484513109 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 16.67% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 74.72% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 0.00% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 8.27% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 14.71% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.00% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 79.11% | 23.80% | 15.28% | 1.344 | -12.84% |
| SPY | 84.76% | 25.22% | 15.58% | 1.393 | -18.76% |
| QQQ | 99.22% | 28.72% | 20.73% | 1.225 | -22.77% |
| VTI | 84.54% | 25.16% | 15.72% | 1.379 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| XLE | XOP | 0.932 |
| OIH | XLE | 0.829 |
| OIH | XOP | 0.812 |
| AVUV | SPYD | 0.783 |
| EWT | EWY | 0.762 |
| AVUV | OIH | 0.692 |
| XLE | MLPA | 0.682 |
| EWT | AVDV | 0.671 |
| MLPA | XOP | 0.665 |
| AVUV | AVDV | 0.647 |
| AVDV | LIT | 0.622 |
| EWY | AVDV | 0.600 |
| AVUV | XOP | 0.597 |
| OIH | MLPA | 0.593 |
| THD | AVDV | 0.574 |
| EWT | LIT | 0.573 |
| SPYD | AVDV | 0.571 |
| AVUV | XLE | 0.552 |
| EIS | AVDV | 0.552 |
| AVUV | XBI | 0.536 |

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
