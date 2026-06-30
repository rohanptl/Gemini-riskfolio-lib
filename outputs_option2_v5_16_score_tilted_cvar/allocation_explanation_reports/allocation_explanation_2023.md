# V5.16 Allocation Explanation Report

Generated at: `2026-06-30T16:51:35`

Output folder: `outputs_option2_v5_16_score_tilted_cvar`  
Window folder: `outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023`  
Walk-forward window: `2023`  
Latest rebalance date: `2026-06-01`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `SGOV` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

| Ticker | FinalWeightPct | WeightChangePct | SelectionBucket | PlainEnglishExplanation |
| --- | --- | --- | --- | --- |
| SGOV | 21.78% | 3.88% | Cash / risk-control sleeve | SGOV is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile. |
| EIS | 11.09% | 1.33% | Selected by latest signal basket | EIS received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| OIH | 7.68% | -1.83% | Carryover / turnover-constrained holding | OIH is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWY | 7.52% | -1.79% | Carryover / turnover-constrained holding | EWY is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| LIT | 6.00% | 2.67% | Selected by latest signal basket | LIT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| EWT | 6.00% | 2.67% | Selected by latest signal basket | EWT received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| GLDM | 5.97% | -1.42% | Carryover / turnover-constrained holding | GLDM is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XBI | 5.07% | -1.21% | Carryover / turnover-constrained holding | XBI is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| TUR | 4.07% | -0.97% | Carryover / turnover-constrained holding | TUR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVDV | 4.03% | -0.96% | Carryover / turnover-constrained holding | AVDV is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| XAR | 3.87% | -0.92% | Carryover / turnover-constrained holding | XAR is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| THD | 3.64% | -0.87% | Carryover / turnover-constrained holding | THD is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| EWP | 3.34% | -0.80% | Carryover / turnover-constrained holding | EWP is likely a carryover holding. It may remain because V5.16 limits monthly turnover, so the portfolio does not fully replace old positions in one rebalance. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Carryover/kept holding from prior rebalance; still above pruning threshold. |
| AVUV | 3.31% | 3.31% | Selected by latest signal basket | AVUV received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| CIBR | 3.31% | 3.31% | Selected by latest signal basket | CIBR received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |
| SMH | 3.31% | 3.31% | Selected by latest signal basket | SMH received an allocation because it passed the latest ETF selection process, survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt. Main positives: above medium-term trend, above longer-term trend, positive 3-month momentum, positive 6-month momentum. Saved model note: Current eligible ETF selected by the V5.7/V5.9b signal layer. |

## Signal details behind each holding

| Ticker | FinalWeightPct | Score | AboveSMA50 | AboveSMA126 | PositiveMom63 | PositiveMom126 | Vol63AnnPct | SelectionBucket | OptimizerRawWeight | ScoreTiltMultiplier | RiskWeightAfterScoreTilt | CashScaledTargetWeight | WeightAfterTurnoverCapBeforePrune | WeightAfterPruningFinal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SGOV | 21.78% |  |  |  |  |  | n/a | Cash / risk-control sleeve | 0.0 |  | 0.0 | 0.2096128025593493 | 0.1882485083274767 | 0.2177995127896438 |
| EIS | 11.09% | 13.59 | True | True | True | True | 25.85% | Selected by latest signal basket | 0.1199999999228702 | 0.8833333333333333 | 0.1161643835616439 | 0.0918148415657085 | 0.0958633411003778 | 0.1109118429227003 |
| OIH | 7.68% | 13.634 | False | True | True | True | 26.41% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0663553248028369 | 0.0767716968461472 |
| EWY | 7.52% | 46.231 | True | True | True | True | 68.16% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0650058530765268 | 0.0752103868143967 |
| LIT | 6.00% | 14.928 | True | True | True | True | 34.00% | Selected by latest signal basket | 0.1199999998626271 | 0.9766666666666668 | 0.1199999999999999 | 0.094846463692878 | 0.051882635461762 | 0.0600271036738149 |
| EWT | 6.00% | 31.486 | True | True | True | True | 36.01% | Selected by latest signal basket | 0.1199999999101764 | 1.14 | 0.1199999999999999 | 0.094846463692878 | 0.051882635461762 | 0.0600271036738149 |
| GLDM | 5.97% | -3.851 | False | False | False | True | 27.40% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0516275056178127 | 0.0597319238808702 |
| XBI | 5.07% | 8.481 | True | True | True | True | 31.02% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0438382327826477 | 0.0507199011904524 |
| TUR | 4.07% | 0.693 | False | False | True | True | 34.43% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0351406626140882 | 0.0406569978400012 |
| AVDV | 4.03% | 11.461 | True | True | True | True | 22.35% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0348352591048436 | 0.0403036524875801 |
| XAR | 3.87% | 7.803 | True | True | False | True | 33.19% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0334139805680037 | 0.0386592635061619 |
| THD | 3.64% | 12.394 | True | True | True | True | 28.31% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0314298113749611 | 0.036363622030028 |
| EWP | 3.34% | 9.871 | True | True | True | True | 26.56% | Carryover / turnover-constrained holding | 0.0 |  | 0.0 | 0.0 | 0.0289057194302617 | 0.03344330143532 |
| AVUV | 3.31% | 12.646 | True | True | True | True | 15.30% | Selected by latest signal basket | 0.1199999997917456 | 0.93 | 0.12 | 0.0948464636928781 | 0.0286302279269335 | 0.0331245636363559 |
| CIBR | 3.31% | 26.921 | True | True | True | True | 32.29% | Selected by latest signal basket | 0.1199999998901252 | 1.1166666666666667 | 0.1199999999999999 | 0.094846463692878 | 0.0286302279269335 | 0.0331245636363559 |
| SMH | 3.31% | 32.606 | True | True | True | True | 37.96% | Selected by latest signal basket | 0.1199999999210794 | 1.163333333333333 | 0.1199999999999999 | 0.094846463692878 | 0.0286302279269335 | 0.0331245636363559 |

## Cash / SGOV explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Final cash / SGOV weight | 21.78% | How much of the portfolio is parked in the cash/T-bill sleeve. |
| Signal breadth | 85.57% | How broad the market strength was across the ETF universe. |
| Breadth-driven cash | 0.00% | Cash suggested because not enough ETFs had strong signals. |
| Volatility-driven cash | 20.96% | Cash suggested because the selected risk sleeve was too volatile. |
| Active sleeve volatility | 22.77% | Estimated annualized volatility of the selected ETF basket. |
| Eligible ETF count | 15 | Number of ETFs that passed the latest selection process. |

## Turnover explanation

| Item | Value | Plain English |
| --- | --- | --- |
| Latest turnover | 20.49% | One-way movement at the latest rebalance. |
| Turnover before pruning | 20.00% | How much the model wanted to move before cleaning up tiny positions. |
| Extra turnover from pruning | 0.49% | Additional movement caused by removing very small positions. |

## Performance context

| Name | Total Return | CAGR | Annual Volatility | Sharpe | Max Drawdown |
| --- | --- | --- | --- | --- | --- |
| Strategy | 77.82% | 23.58% | 15.36% | 1.326 | -13.79% |
| SPY | 81.89% | 24.62% | 15.65% | 1.357 | -18.76% |
| QQQ | 107.89% | 30.89% | 20.55% | 1.315 | -22.77% |
| VTI | 82.13% | 24.68% | 15.80% | 1.348 | -19.30% |

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

| ETF 1 | ETF 2 | Correlation |
| --- | --- | --- |
| AVDV | EWP | 0.775 |
| EWT | SMH | 0.773 |
| EWY | EWT | 0.762 |
| OIH | AVUV | 0.701 |
| EWT | AVDV | 0.671 |
| AVDV | AVUV | 0.654 |
| XAR | AVUV | 0.648 |
| EWY | SMH | 0.634 |
| LIT | AVDV | 0.620 |
| AVDV | XAR | 0.611 |
| CIBR | SMH | 0.610 |
| EWY | AVDV | 0.610 |
| AVDV | THD | 0.579 |
| LIT | EWT | 0.572 |
| AVDV | SMH | 0.559 |
| EWT | THD | 0.548 |
| XBI | AVUV | 0.545 |
| EIS | AVDV | 0.543 |
| EIS | SMH | 0.537 |
| XAR | SMH | 0.531 |

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
