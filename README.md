python main_option2_all_etfs_v5_16_score_tilted_cvar_production_with_attribution.py

python explain_v516_allocation_fixed.py \
  --output-dir outputs_option2_v5_16_score_tilted_cvar \
  --window 2023 \
  --zip
  


Below is a clean explanation of **V5.16 production script** using block and sequence diagrams.

You can paste the Mermaid diagrams into a Mermaid viewer such as `mermaid.live`.

---

# 1. V5.16 high-level block diagram

```mermaid
flowchart TD
    A[Wealthfront_ETF_Categorization.csv] --> B[Load tickers]
    B --> C[Remove cash-like ETFs from risk universe]
    C --> D[Add SGOV + Benchmarks]
    D --> E[yfinance download prices]
    E --> F[Create daily return matrix]

    F --> G[Walk-forward windows]
    G --> G1[2020 start]
    G --> G2[2021 start]
    G --> G3[2022 start]
    G --> G4[2023 start]

    G1 --> H[Monthly rebalance loop]
    G2 --> H
    G3 --> H
    G4 --> H

    H --> I[Signal + scoring layer]
    I --> J[Eligibility filters]
    J --> K[Fast/slow correlation filter]
    K --> L[Riskfolio Classic CVaR optimizer]
    L --> M[Score-tilted CVaR sizing]
    M --> N[Cash sleeve decision]
    N --> O[Turnover cap]
    O --> P[Prune tiny positions]
    P --> Q[Hold weights until next month]

    Q --> R[Backtest returns]
    R --> S[Reports + CSV outputs]
```

## Plain-English explanation

V5.16 does this:

```text
1. Read ETF universe from the Wealthfront CSV.
2. Remove SGOV/cash-like ETFs from the risk universe.
3. Add SGOV separately as the cash sleeve.
4. Add SPY, QQQ, VTI for benchmark reporting.
5. Download prices from yfinance.
6. Convert prices into daily returns.
7. For each walk-forward start year, run a monthly rebalance backtest.
8. At each rebalance date:
   - score ETFs,
   - filter weak ETFs,
   - remove highly correlated duplicates,
   - optimize the selected basket with Riskfolio CVaR,
   - tilt weights toward higher-scoring ETFs,
   - add SGOV if risk/cash rules require it,
   - cap turnover,
   - prune small positions,
   - hold until next monthly rebalance.
```

---

# 2. Input and data-download flow

```mermaid
flowchart TD
    A[CSV_FILE = Wealthfront_ETF_Categorization.csv] --> B[load_tickers]
    B --> C[Clean tickers]
    C --> D[Risk ETF universe]

    D --> E[Remove cash equivalents]
    E --> F[Risk tickers only]

    F --> G[Add SGOV if cash sleeve enabled]
    F --> H[Add SPY, QQQ, VTI benchmarks]
    F --> I[Add SPY as market proxy]

    G --> J[download_tickers]
    H --> J
    I --> J

    J --> K[yfinance download]
    K --> L[extract_price_panel]
    L --> M[Adjusted Close if available]
    L --> N[Fallback to Close]
    M --> O[Price panel]
    N --> O

    O --> P[pct_change]
    P --> Q[Daily returns matrix]
```

## Important point

The script uses:

```python
prices = download_prices(...)
base_returns = prices.pct_change(fill_method=None)
```

So all later indicators are derived from **return-based pseudo-prices**, not directly from OHLC data.

V5.16 does **not** use:

```text
high / low / ATR / NATR
```

That was only in the V5.17 experiment.

---

# 3. Walk-forward structure

```mermaid
flowchart TD
    A[Downloaded return matrix] --> B[Walk-forward start dates]

    B --> C1[Start 2020-01-01]
    B --> C2[Start 2021-01-01]
    B --> C3[Start 2022-01-01]
    B --> C4[Start 2023-01-01]

    C1 --> D[Run same V5.16 strategy]
    C2 --> D
    C3 --> D
    C4 --> D

    D --> E[Per-window outputs]
    E --> F[benchmark_comparison.csv]
    E --> G[portfolio_backtest.csv]
    E --> H[weights_by_rebalance.csv]
    E --> I[final_target_weights_tradeable.csv]

    D --> J[Consolidated outputs]
    J --> K[walk_forward_summary.csv]
    J --> L[benchmark_comparison_by_window.csv]
    J --> M[rolling_12m_summary_by_window.csv]
```

## Why walk-forward matters

The strategy is not judged from only one start date. It runs from:

```text
2020
2021
2022
2023
```

This checks whether the strategy survives multiple market regimes.

---

# 4. Monthly rebalance sequence

```mermaid
sequenceDiagram
    participant Main as main()
    participant Data as Returns Matrix
    participant Loop as Monthly Rebalance Loop
    participant Signal as Signal/Scoring Layer
    participant Filter as Eligibility + Correlation Filter
    participant Riskfolio as Riskfolio Optimizer
    participant Cash as Cash Sleeve
    participant Turnover as Turnover Control
    participant Backtest as Forward Return Engine
    participant Reports as Output Reports

    Main->>Data: Load daily returns
    Main->>Loop: Run each walk-forward window

    loop Each month-start rebalance date
        Loop->>Data: Get returns up to rebalance date
        Loop->>Data: Use last 189 trading days as lookback
        Loop->>Signal: Compute ETF scores
        Signal->>Filter: Apply trend/momentum/volatility filters
        Filter->>Filter: Apply fast/slow correlation filter
        Filter->>Riskfolio: Send selected ETF basket
        Riskfolio->>Riskfolio: Classic CVaR Sharpe optimization
        Riskfolio->>Riskfolio: Apply score-rank tilt
        Riskfolio->>Cash: Send optimized risk weights
        Cash->>Cash: Determine SGOV cash weight
        Cash->>Turnover: Create target final weights
        Turnover->>Turnover: Apply 20% turnover cap
        Turnover->>Turnover: Prune tiny positions
        Turnover->>Backtest: Final weights for next month
        Backtest->>Backtest: Apply weights until next rebalance
    end

    Backtest->>Reports: Build equity curve and performance stats
    Reports->>Reports: Save CSV outputs
```

---

# 5. Technical indicators used

V5.16 uses these indicators in the scoring layer.

```mermaid
flowchart TD
    A[Training returns window] --> B[Pseudo-price series]
    B --> C[SMA 50]
    B --> D[SMA 126]
    B --> E[21-day momentum]
    B --> F[63-day momentum]
    B --> G[126-day momentum]
    A --> H[63-day annualized volatility]

    C --> I[Above SMA 50?]
    D --> J[Above SMA 126?]
    F --> K[Positive 63D momentum?]
    G --> L[Positive 126D momentum?]

    E --> M[Z-score Mom21]
    F --> N[Z-score Mom63]
    G --> O[Z-score Mom126]
    H --> P[Z-score Vol63]

    I --> Q[ETF Score]
    J --> Q
    K --> Q
    L --> Q
    M --> Q
    N --> Q
    O --> Q
    P --> Q
```

## Score formula

The script scores each ETF roughly like this:

```text
Score =
  2.00 × AboveSMA50
+ 3.00 × AboveSMA126
+ 2.50 × PositiveMom63
+ 3.50 × PositiveMom126
+ 1.50 × ZScore(Mom21)
+ 2.50 × ZScore(Mom63)
+ 3.50 × ZScore(Mom126)
- 2.00 × ZScore(Vol63)
```

So it prefers ETFs with:

```text
Positive trend
Positive medium-term momentum
Positive longer-term momentum
Lower realized volatility
```

---

# 6. ETF selection flow

```mermaid
flowchart TD
    A[All risk ETFs] --> B[Compute score table]
    B --> C[Apply hard filters]

    C --> D{Above SMA50?}
    D --> E{Above SMA126?}
    E --> F{Positive 63D momentum?}
    F --> G{Positive 126D momentum?}
    G --> H{Vol63 <= 45%?}

    H --> I[Eligible ETFs]

    I --> J{Enough ETFs?}
    J -- Yes --> K[Rank by score]
    J -- No --> L[Fallback to top-ranked ETFs]

    K --> M[Fast/slow correlation filter]
    L --> M

    M --> N[Final selected winner basket]
```

## Selection rules

V5.16 requires:

```text
Price above SMA50
Price above SMA126
63-day momentum positive
126-day momentum positive
63-day annualized volatility <= 45%
```

Then it chooses roughly:

```text
Minimum selected ETFs: 10
Maximum selected ETFs: 15
Max individual risk ETF weight: 12%
```

---

# 7. Fast/slow correlation filter

This is the V5.14 improvement that V5.16 keeps.

```mermaid
flowchart TD
    A[Ranked eligible ETFs] --> B[Calculate 63-day correlation]
    A --> C[Calculate 126-day correlation]

    B --> D[Fast corr matrix]
    C --> E[Slow corr matrix]

    D --> F[Effective corr = max abs fast, abs slow]
    E --> F

    F --> G[Walk down ranked ETF list]

    G --> H{Corr to selected ETFs <= 0.85?}
    H -- Yes --> I[Add ETF]
    H -- No --> J[Skip ETF]

    I --> K{Reached max 15 ETFs?}
    J --> K

    K -- No --> G
    K -- Yes --> L[Selected basket]
```

## Why this matters

This prevents the portfolio from becoming one crowded trade.

Example: if several tech/semiconductor ETFs score highly, the correlation filter tries to avoid owning too many nearly identical exposures.

V5.16 uses:

```python
effective_corr = max(abs(corr_63), abs(corr_126))
```

That means an ETF can be rejected if it is highly correlated over either:

```text
recent 63-day window
or
slower 126-day window
```

---

# 8. Riskfolio optimization flow

```mermaid
flowchart TD
    A[Selected ETF basket] --> B[Return matrix for selected ETFs]
    B --> C[Riskfolio Portfolio object]

    C --> D[Estimate expected returns using historical mean]
    C --> E[Estimate covariance using Ledoit shrinkage]

    D --> F[Classic CVaR Sharpe optimization]
    E --> F

    F --> G[Raw optimized weights]
    G --> H[Normalize weights]
    H --> I[Apply max 12% per ETF cap]
    I --> J[Base CVaR risk weights]

    J --> K[Apply score-rank tilt]
    K --> L[Re-apply 12% cap]
    L --> M[Final risk-sleeve weights]
```

## Riskfolio settings

V5.16 uses:

```python
model = "Classic"
rm = "CVaR"
obj = "Sharpe"
method_mu = "hist"
method_cov = "ledoit"
upperlng = 0.12
```

Meaning:

```text
Classic optimizer
CVaR risk measure
Sharpe objective
Historical mean returns
Ledoit covariance shrinkage
No shorting
Max 12% per ETF
```

## Important note

The script still contains `build_momentum_views()`, but **V5.16 does not use Black-Litterman**.

That function is dead code in V5.16.

Instead, V5.16 uses this practical bridge:

```text
Riskfolio CVaR sizing first
Then modestly tilt weights toward higher-scoring ETFs
```

---

# 9. Score-tilted CVaR sizing

```mermaid
flowchart TD
    A[CVaR optimized weights] --> B[Get ETF score ranks]
    B --> C[Convert scores to percentile ranks]
    C --> D[Center ranks around average]
    D --> E[Create tilt multiplier]

    E --> F[Clip multiplier between 0.70 and 1.30]
    F --> G[Multiply CVaR weights by tilt multiplier]
    G --> H[Normalize to 100% risk sleeve]
    H --> I[Apply 12% max cap again]
    I --> J[Score-tilted CVaR weights]
```

## What the score tilt does

Higher-ranked ETFs get a modest boost. Lower-ranked ETFs get a modest haircut.

Config:

```python
SCORE_TILT_STRENGTH = 0.35
SCORE_TILT_MIN_MULTIPLIER = 0.70
SCORE_TILT_MAX_MULTIPLIER = 1.30
```

So the score model influences sizing, but it does not overpower Riskfolio.

---

# 10. Cash sleeve logic

```mermaid
flowchart TD
    A[Optimized risk weights] --> B[Estimate active sleeve volatility]
    C[Signal breadth] --> D[Breadth-based cash weight]

    B --> E[Volatility-based cash weight]
    D --> F[Final cash weight = max breadth cash, vol cash]
    E --> F

    F --> G[Scale risk weights by 1 - cash weight]
    G --> H[Put cash weight into SGOV]
    H --> I[Final pre-turnover target weights]
```

## Cash comes from two sources

### 1. Signal breadth cash

The script checks how broad the market strength is across the ETF universe.

It measures:

```text
How many ETFs are above SMA50?
How many are above SMA126?
How many have positive 63D momentum?
How many have positive 126D momentum?
Plus SPY confirmation
```

If breadth is weak, it raises SGOV.

### 2. Volatility cash

The script estimates the volatility of the selected risk sleeve.

If active sleeve volatility is above the target:

```python
TARGET_ACTIVE_SLEEVE_VOL = 0.18
```

then it adds SGOV to bring portfolio risk down.

Final cash weight is:

```python
cash_weight = max(breadth_cash_weight, vol_cash_weight)
```

So either weak breadth or high volatility can increase SGOV.

---

# 11. Turnover and pruning

```mermaid
flowchart TD
    A[Previous month weights] --> C[Turnover cap]
    B[New target weights] --> C

    C --> D{One-way turnover > 20%?}
    D -- No --> E[Use target weights]
    D -- Yes --> F[Blend partially from old weights to target weights]

    E --> G[Post-turnover weights]
    F --> G

    G --> H[Prune tiny positions]
    H --> I[Remove sub-2% stale positions]
    I --> J[Limit to max 15 non-cash holdings]
    J --> K[Redistribute remaining weights]
    K --> L[Final monthly allocation]
```

## Turnover formula

The script uses one-way turnover:

```python
turnover = 0.5 * sum(abs(current_weight - previous_weight))
```

With:

```python
MAX_TURNOVER_PER_REBALANCE = 0.20
```

So the portfolio only moves partway toward the new target if the trade would exceed 20% turnover.

## Why pruning exists

Turnover caps can leave tiny stale positions. So after turnover control, V5.16 prunes tiny weights:

```text
Remove small positions below 2%
Keep max 15 non-cash holdings
Redistribute weight to the remaining names
```

This keeps the final allocation tradable.

---

# 12. Backtest return calculation

```mermaid
sequenceDiagram
    participant Loop as Monthly Loop
    participant Weights as Final Monthly Weights
    participant Returns as Daily Returns
    participant Backtest as Portfolio Return Engine

    Loop->>Weights: Final allocation at rebalance date
    Loop->>Returns: Get daily returns until next rebalance
    Returns->>Backtest: forward_returns matrix
    Weights->>Backtest: final_weights vector
    Backtest->>Backtest: daily portfolio return = returns dot weights
    Backtest->>Loop: Append daily returns
```

## Core idea

At each monthly rebalance:

```python
period_portfolio_returns = forward_returns.dot(final_weights)
```

This means:

```text
The selected weights are held until the next monthly rebalance.
```

That is why V5.16 is a monthly production engine, not a weekly risk-off engine.

---

# 13. Output/reporting block

```mermaid
flowchart TD
    A[Daily strategy returns] --> B[Equity curve]
    A --> C[Benchmark comparison]
    A --> D[Monthly returns]
    A --> E[Worst months]
    A --> F[Rolling 12M underperformance]
    A --> G[Drawdown table]

    H[Weights by rebalance] --> I[Final target weights]
    H --> J[Tradeable final target weights]
    H --> K[Turnover report]

    L[Score and eligibility history] --> M[Final selection reasons]
    L --> N[Eligibility history]

    O[Final portfolio] --> P[Final correlation matrix]
    O --> Q[High correlation pairs]
    O --> R[Correlation heatmap]
```

## Important output files

```text
walk_forward_summary.csv
benchmark_comparison_by_window.csv
rolling_12m_summary_by_window.csv

walk_forward_windows/2023/final_target_weights_tradeable.csv
walk_forward_windows/2023/final_portfolio_selection_reasons.csv
walk_forward_windows/2023/weights_by_rebalance.csv
walk_forward_windows/2023/signal_cash_history.csv
walk_forward_windows/2023/turnover_by_rebalance.csv
walk_forward_windows/2023/benchmark_comparison.csv
walk_forward_windows/2023/monthly_returns.csv
walk_forward_windows/2023/worst_months.csv
walk_forward_windows/2023/drawdown_data.csv
```

---

# 14. End-to-end simplified sequence

```mermaid
sequenceDiagram
    participant CSV as Wealthfront CSV
    participant Main as main()
    participant YF as yfinance
    participant Engine as run_backtest_for_start_window()
    participant Score as compute_asset_score_table()
    participant Select as select_eligible_assets()
    participant Corr as correlation filter
    participant RF as Riskfolio CVaR
    participant Tilt as score tilt
    participant Cash as cash sleeve
    participant Trade as turnover/prune
    participant Report as reports

    CSV->>Main: ETF universe
    Main->>Main: Remove cash-like ETFs
    Main->>YF: Download ETF + SGOV + benchmark prices
    YF->>Main: Price panel
    Main->>Main: Convert prices to daily returns

    loop Each walk-forward start date
        Main->>Engine: Start backtest window

        loop Each month-start rebalance
            Engine->>Score: Last 189 trading days
            Score->>Select: Score table
            Select->>Corr: Eligible ranked ETFs
            Corr->>Engine: Diversified winner basket
            Engine->>RF: Selected ETF returns
            RF->>Tilt: CVaR optimized weights
            Tilt->>Cash: Score-tilted risk weights
            Cash->>Trade: Add SGOV cash sleeve
            Trade->>Engine: Final monthly weights
            Engine->>Engine: Apply weights until next rebalance
        end

        Engine->>Report: Save per-window CSVs
    end

    Main->>Report: Save consolidated walk-forward summaries
```

---

# 15. One-sentence explanation for someone else

V5.16 is a **monthly tactical ETF rotation system** that reads the Wealthfront ETF universe, downloads price data, ranks ETFs by trend/momentum/volatility, removes weak and highly correlated names, uses Riskfolio CVaR to size the selected basket, modestly tilts weights toward stronger scores, adds SGOV when breadth or volatility says risk is elevated, caps turnover, prunes small positions, and then holds the portfolio until the next month-start rebalance.
