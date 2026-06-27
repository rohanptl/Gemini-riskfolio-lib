from pathlib import Path
import warnings
import re

import numpy as np
import pandas as pd
import yfinance as yf
import riskfolio as rp
import matplotlib.pyplot as plt


# Suppress noisy CVXPY deprecation warning emitted through Riskfolio internals.
# This does not affect optimization results.
warnings.filterwarnings(
    "ignore",
    message=r".*This use of ``\*`` has resulted in matrix multiplication.*",
    category=UserWarning,
    module=r"cvxpy\.expressions\.expression",
)

# ============================================================
# CONFIG
# ============================================================

CSV_FILE = "Wealthfront_ETF_Categorization.csv"

START_DATE = "2023-01-01"
END_DATE = "2026-06-23"  # yfinance end date is effectively exclusive

# V5.10 reporting / validation.
# Runs the same V5.9b strategy across multiple start windows automatically.
RUN_WALK_FORWARD_SUMMARY = True
WALK_FORWARD_START_DATES = [
    "2020-01-01",
    "2021-01-01",
    "2022-01-01",
    "2023-01-01",
]

FREQ = "monthly"  # "monthly" or "biweekly"

LOOKBACK = 189 if FREQ == "monthly" else 126
REBALANCE_DAYS = 21 if FREQ == "monthly" else 10

# Rebalance schedule.
# "month_start" = first available trading day of each calendar month.
# "fixed_days" = every REBALANCE_DAYS trading days after LOOKBACK.
REBALANCE_MODE = "month_start"


TRADING_DAYS = 252
ANNUAL_RF = 0.02
DAILY_RF = ANNUAL_RF / TRADING_DAYS

# ------------------------------------------------------------
# OPTION 2: FILTER WINNERS FIRST, THEN OPTIMIZE
# ------------------------------------------------------------

# Wider winner basket + lower cap gives Riskfolio room to size positions.
# This reduces the previous "five assets at 20% each" forced equal-weight behavior.
MIN_ELIGIBLE_ASSETS = 10
MAX_ELIGIBLE_ASSETS = 15
MAX_RISK_ASSET_WEIGHT = 0.12

# Remove tiny optimizer dust.
MIN_WEIGHT_TO_KEEP = 0.01
MIN_PRINT_WEIGHT = 0.001  # raw output threshold
TRADEABLE_MIN_WEIGHT = 0.02  # cleaner display threshold

# Eligibility filters.
REQUIRE_PRICE_ABOVE_SMA_50 = True
REQUIRE_PRICE_ABOVE_SMA_126 = True
REQUIRE_POSITIVE_63D_MOMENTUM = True
REQUIRE_POSITIVE_126D_MOMENTUM = True

# Benchmark-relative alpha filter.
# Sectors/themes must outperform SPY on at least one medium-term window.
USE_RELATIVE_STRENGTH_FILTER = False
REQUIRE_OUTPERFORM_SPY_63D = False
REQUIRE_OUTPERFORM_SPY_126D = False

# Risk controls for the candidate basket.
USE_VOL_FILTER = True
MAX_ELIGIBLE_VOL_63 = 0.45  # annualized 63-day realized vol

# Correlation cluster control.
# Prevents the selected basket from becoming one crowded trade
# such as SMH + QTEC + IXN + XLK + QQQJ, or EWY + EWT + EMXC.
USE_CORRELATION_FILTER = True
MAX_PAIRWISE_CORR = 0.85
CORR_LOOKBACK_DAYS = 126

# If strict rules produce fewer than MIN_ELIGIBLE_ASSETS,
# the script falls back to the top-ranked assets by score.
ALLOW_FALLBACK_TO_TOP_RANKED = True

# Portfolio-level risk targeting.
USE_VOL_TARGET_CASH_SCALING = True
TARGET_ACTIVE_SLEEVE_VOL = 0.18
MAX_VOL_BASED_CASH_WEIGHT = 0.50

# Turnover control. One-way turnover per rebalance is capped by blending
# from old weights toward target weights.
USE_TURNOVER_CAP = True
MAX_TURNOVER_PER_REBALANCE = 0.20

# V5.6: keep turnover control, but do not let tiny residual positions linger forever.
# Cleanup is applied after the turnover cap. It may push actual turnover slightly
# above 20%, but only by pruning very small weights.
PRUNE_TINY_POSITIONS_AFTER_TURNOVER = True
MIN_POSITION_WEIGHT_AFTER_REBALANCE = 0.02
MAX_FINAL_HOLDINGS_AFTER_PRUNE = 15

# Keep explicit cash-like ETFs out of the active risk sleeve.
# They are controlled by the SGOV/cash sleeve instead.
CASH_EQUIVALENT_TICKERS = {
    "SGOV", "BIL", "SHV", "USFR", "JPST", "PULS", "FLRN",
    "SCHO", "BSV", "VCSH", "SUB", "VTEB", "NYF", "CMF"
}

# Optional SGOV/cash sleeve.
USE_CASH_SLEEVE = True
CASH_TICKER = "SGOV"

MAX_CASH_WEIGHT = 0.50
MIN_CASH_WEIGHT = 0.00

# SGOV activates only when breadth weakens.
STRONG_SIGNAL_THRESHOLD = 0.65
WEAK_SIGNAL_THRESHOLD = 0.35

# Benchmarks.
BENCHMARK_TICKERS = ["SPY", "QQQ", "VTI"]
MARKET_PROXY = "SPY"

# V5.7:
# Benchmarks are kept only for reporting/performance comparison.
# They are not used as hard eligibility filters or score boosts.
# If SPY/QQQ/VTI/IWM/DIA are in your ETF universe CSV, they remain investable
# like any other ETF loaded from the file.
BENCHMARKS_ARE_REPORTING_ONLY = True

MIN_VALID_RATIO = 0.80

OUTPUT_DIR = Path("outputs_option2_v5_10_month_start_rebalance")
OUTPUT_DIR.mkdir(exist_ok=True)
WALK_FORWARD_OUTPUT_DIR = OUTPUT_DIR / "walk_forward_windows"

# Heatmap safety. Full 197x197 CSV is saved, but PNG is limited to avoid OOM kills.
HEATMAP_MAX_ASSETS = 40
HEATMAP_MAX_FIG_SIZE = 18
FINAL_PORTFOLIO_HEATMAP_MAX_FIG_SIZE = 24



# ============================================================
# DATA HELPERS
# ============================================================

def is_probable_ticker(value: object) -> bool:
    """
    Accepts normal ETF ticker shapes such as SPY, QQQM, BRK.B, BRK-B.
    Rejects labels, numbers, percentages, phrases, and empty values.
    """
    if pd.isna(value):
        return False

    token = str(value).strip().upper()

    if not token:
        return False

    # Reject obvious non-tickers / metadata labels.
    if token in {
        "TICKER", "ETF_NAME", "ETF NAME", "CATEGORY", "ELIGIBLE",
        "NOTES", "MAX_WEIGHT", "IS_CASH", "IS_GOLD", "IS_CRYPTO",
        "TRUE", "FALSE"
    }:
        return False

    # Reject numbers like 0.2, 20, 12, 30.
    try:
        float(token)
        return False
    except ValueError:
        pass

    # Reject phrases like "NASDAQ 100", "CORE BONDS", "US EQUITY".
    if " " in token:
        return False

    # Most ETF tickers are 1-5 letters; allow one dot/dash suffix.
    return bool(re.fullmatch(r"[A-Z]{1,5}([.-][A-Z])?", token))


def clean_ticker_list(values: list[object]) -> list[str]:
    """
    Cleans and de-duplicates candidate ticker values while preserving order.
    """
    cleaned = []

    for value in values:
        if is_probable_ticker(value):
            cleaned.append(str(value).strip().upper())

    return list(dict.fromkeys(cleaned))


def load_tickers(csv_file: str) -> list[str]:
    """
    Loads all ETF tickers from the Wealthfront ETF CSV without using Category.

    Handles both common layouts:

    1. Normal row-wise CSV:
       Ticker,ETF_Name,Category,...
       SPY,...
       QQQ,...

    2. Transposed CSV:
       Ticker,SPY,QQQ,VTI,...
       ETF_NAME,...
       CATEGORY,...

    This avoids accidentally loading labels like CATEGORY, ETF_NAME, TRUE,
    MAX_WEIGHT, 0.2, or NASDAQ 100 as tickers.
    """
    raw = pd.read_csv(csv_file, header=None, dtype=str).fillna("")

    ticker_cells = []

    for row_idx in range(raw.shape[0]):
        for col_idx in range(raw.shape[1]):
            if str(raw.iat[row_idx, col_idx]).strip().lower() == "ticker":
                ticker_cells.append((row_idx, col_idx))

    candidates: list[tuple[str, list[str]]] = []

    for row_idx, col_idx in ticker_cells:
        # Normal row-wise layout: tickers below the Ticker header.
        below_values = raw.iloc[row_idx + 1 :, col_idx].tolist()
        below_tickers = clean_ticker_list(below_values)
        candidates.append((f"column_below_row_{row_idx}_col_{col_idx}", below_tickers))

        # Transposed layout: tickers to the right of the Ticker label.
        right_values = raw.iloc[row_idx, col_idx + 1 :].tolist()
        right_tickers = clean_ticker_list(right_values)
        candidates.append((f"row_right_row_{row_idx}_col_{col_idx}", right_tickers))

    # Fallback: pandas-normal layout with a Ticker column.
    try:
        df = pd.read_csv(csv_file, dtype=str).fillna("")
        ticker_col = None

        for col in df.columns:
            if str(col).strip().lower() == "ticker":
                ticker_col = col
                break

        if ticker_col is not None:
            candidates.append(("pandas_ticker_column", clean_ticker_list(df[ticker_col].tolist())))

    except Exception:
        pass

    # Last fallback: first row after first cell, useful for transposed files.
    if raw.shape[0] > 0:
        first_row_tickers = clean_ticker_list(raw.iloc[0, 1:].tolist())
        candidates.append(("first_row_right_fallback", first_row_tickers))

    if not candidates:
        raise ValueError("Could not identify a Ticker row or column in CSV.")

    source_name, tickers = max(candidates, key=lambda item: len(item[1]))

    if not tickers:
        raise ValueError("No valid tickers found in CSV after cleaning.")

    print(f"Ticker source detected: {source_name}")
    print(f"Loaded {len(tickers)} valid ETF tickers from file.")

    return tickers


def extract_price_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Handles different yfinance formats:
    1. MultiIndex: level 0 = price field, level 1 = ticker
    2. MultiIndex: level 0 = ticker, level 1 = price field
    3. Flat columns for one ticker
    """
    if raw.empty:
        raise ValueError("yfinance returned empty data.")

    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        level1 = raw.columns.get_level_values(1)

        if "Adj Close" in level0:
            prices = raw.xs("Adj Close", axis=1, level=0)
        elif "Adj Close" in level1:
            prices = raw.xs("Adj Close", axis=1, level=1)
        elif "Close" in level0:
            prices = raw.xs("Close", axis=1, level=0)
        elif "Close" in level1:
            prices = raw.xs("Close", axis=1, level=1)
        else:
            raise KeyError(f"No Adj Close or Close found. Columns: {raw.columns}")
    else:
        if "Adj Close" in raw.columns:
            prices = raw[["Adj Close"]]
        elif "Close" in raw.columns:
            prices = raw[["Close"]]
        else:
            raise KeyError(f"No Adj Close or Close found. Columns: {raw.columns}")

    prices = prices.dropna(axis=1, how="all").sort_index()

    if prices.empty:
        raise ValueError("No usable price columns after cleaning.")

    return prices


def download_prices(
    tickers: list[str],
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> pd.DataFrame:
    raw = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=True,
        group_by="column",
        threads=True,
    )

    prices = extract_price_panel(raw)
    prices = prices.replace([np.inf, -np.inf], np.nan)
    prices = prices.dropna(axis=1, how="all")

    return prices


# ============================================================
# SCORING + ELIGIBILITY
# ============================================================

def safe_zscore(s: pd.Series) -> pd.Series:
    s = s.replace([np.inf, -np.inf], np.nan)

    std = s.std()

    if pd.isna(std) or std == 0:
        return pd.Series(0.0, index=s.index)

    return (s - s.mean()) / std


def compute_asset_score_table(
    train_returns: pd.DataFrame,
    benchmark_returns: pd.Series | None = None,
) -> pd.DataFrame:
    """
    Scores each ETF using absolute trend, absolute momentum, relative strength
    versus SPY, and realized volatility.

    Option 2 principle:
    - The signal model selects likely winners.
    - Riskfolio sizes only that winner basket.
    """
    r = train_returns.copy().dropna(axis=1, how="all").fillna(0.0)

    if r.empty:
        return pd.DataFrame()

    pseudo_prices = (1 + r).cumprod()

    last_price = pseudo_prices.iloc[-1]

    sma_50 = pseudo_prices.rolling(min(50, len(pseudo_prices))).mean().iloc[-1]
    sma_126 = pseudo_prices.rolling(min(126, len(pseudo_prices))).mean().iloc[-1]

    mom_21 = last_price / pseudo_prices.iloc[-min(21, len(pseudo_prices))] - 1
    mom_63 = last_price / pseudo_prices.iloc[-min(63, len(pseudo_prices))] - 1
    mom_126 = last_price / pseudo_prices.iloc[-min(126, len(pseudo_prices))] - 1

    vol_63 = r.tail(min(63, len(r))).std() * np.sqrt(TRADING_DAYS)

    above_sma_50 = last_price > sma_50
    above_sma_126 = last_price > sma_126
    positive_mom_63 = mom_63 > 0
    positive_mom_126 = mom_126 > 0

    rs_63 = pd.Series(0.0, index=r.columns)
    rs_126 = pd.Series(0.0, index=r.columns)
    outperform_spy_63 = pd.Series(False, index=r.columns)
    outperform_spy_126 = pd.Series(False, index=r.columns)

    if benchmark_returns is not None and len(benchmark_returns.dropna()) >= 126:
        b = benchmark_returns.reindex(r.index).fillna(0.0)
        b_price = (1 + b).cumprod()

        b_mom_63 = b_price.iloc[-1] / b_price.iloc[-min(63, len(b_price))] - 1
        b_mom_126 = b_price.iloc[-1] / b_price.iloc[-min(126, len(b_price))] - 1

        rs_63 = mom_63 - b_mom_63
        rs_126 = mom_126 - b_mom_126

        outperform_spy_63 = rs_63 > 0
        outperform_spy_126 = rs_126 > 0

    # V5.7:
    # Score uses only each ETF's own trend, momentum, and volatility.
    # Benchmark-relative metrics are kept as diagnostics only and are not used
    # for eligibility or scoring.
    score = (
        2.00 * above_sma_50.astype(float)
        + 3.00 * above_sma_126.astype(float)
        + 2.50 * positive_mom_63.astype(float)
        + 3.50 * positive_mom_126.astype(float)
        + 1.50 * safe_zscore(mom_21)
        + 2.50 * safe_zscore(mom_63)
        + 3.50 * safe_zscore(mom_126)
        - 2.00 * safe_zscore(vol_63)
    )

    score_table = pd.DataFrame(
        {
            "Score": score,
            "Mom21": mom_21,
            "Mom63": mom_63,
            "Mom126": mom_126,
            "RS63VsSPY": rs_63,
            "RS126VsSPY": rs_126,
            "Vol63Ann": vol_63,
            "AboveSMA50": above_sma_50,
            "AboveSMA126": above_sma_126,
            "PositiveMom63": positive_mom_63,
            "PositiveMom126": positive_mom_126,
            "OutperformSPY63": outperform_spy_63,
            "OutperformSPY126": outperform_spy_126,
        }
    )

    score_table = score_table.sort_values("Score", ascending=False)

    return score_table



def apply_correlation_filter_to_ranked_assets(
    train_returns: pd.DataFrame,
    ranked_assets: list[str],
    min_assets: int = MIN_ELIGIBLE_ASSETS,
    max_assets: int = MAX_ELIGIBLE_ASSETS,
) -> list[str]:
    """
    Selects a ranked basket while avoiding excessive correlation clusters.

    Rule:
    - Walk down the ranked list.
    - Add an ETF only if its max absolute correlation to already-selected ETFs
      is <= MAX_PAIRWISE_CORR.
    - If this leaves fewer than min_assets, relax the rule and fill from the
      remaining highest-ranked ETFs so the portfolio remains feasible.

    This prevents the active basket from becoming one crowded trade.
    """
    if not USE_CORRELATION_FILTER:
        return ranked_assets[:max_assets]

    ranked_assets = [a for a in ranked_assets if a in train_returns.columns]

    if not ranked_assets:
        return []

    r = train_returns[ranked_assets].tail(min(CORR_LOOKBACK_DAYS, len(train_returns))).fillna(0.0)

    if r.shape[0] < 30 or r.shape[1] < 2:
        return ranked_assets[:max_assets]

    corr = r.corr().abs().replace([np.inf, -np.inf], np.nan).fillna(0.0)

    selected: list[str] = []

    for asset in ranked_assets:
        if len(selected) >= max_assets:
            break

        if not selected:
            selected.append(asset)
            continue

        max_corr_to_selected = corr.loc[asset, selected].max()

        if max_corr_to_selected <= MAX_PAIRWISE_CORR:
            selected.append(asset)

    # If correlation filter is too restrictive, fill from ranked names.
    if len(selected) < min_assets:
        for asset in ranked_assets:
            if len(selected) >= min_assets:
                break
            if asset not in selected:
                selected.append(asset)

    return selected[:max_assets]


def select_eligible_assets(train_returns: pd.DataFrame, risk_assets: list[str]) -> tuple[list[str], pd.DataFrame]:
    """
    Option 2 with risk controls:
    1. Score all ETFs.
    2. Keep trend-positive and momentum-positive ETFs.
    3. Prefer ETFs outperforming SPY.
    4. Exclude very high-volatility ETFs.
    5. Use top-ranked fallback only if strict filters are too narrow.
    """
    available_assets = [a for a in risk_assets if a in train_returns.columns]
    r = train_returns[available_assets].copy()

    benchmark_returns = None
    if MARKET_PROXY in train_returns.columns:
        benchmark_returns = train_returns[MARKET_PROXY]

    score_table = compute_asset_score_table(r, benchmark_returns=benchmark_returns)

    if score_table.empty:
        return available_assets[:MIN_ELIGIBLE_ASSETS], score_table

    mask = pd.Series(True, index=score_table.index)

    if REQUIRE_PRICE_ABOVE_SMA_50:
        mask &= score_table["AboveSMA50"]

    if REQUIRE_PRICE_ABOVE_SMA_126:
        mask &= score_table["AboveSMA126"]

    if REQUIRE_POSITIVE_63D_MOMENTUM:
        mask &= score_table["PositiveMom63"]

    if REQUIRE_POSITIVE_126D_MOMENTUM:
        mask &= score_table["PositiveMom126"]

    # V5.7: benchmark-relative filters are disabled by config.
    # These columns remain available as diagnostics only.
    if USE_RELATIVE_STRENGTH_FILTER:
        if REQUIRE_OUTPERFORM_SPY_63D:
            mask &= score_table["OutperformSPY63"]
        if REQUIRE_OUTPERFORM_SPY_126D:
            mask &= score_table["OutperformSPY126"]

    if USE_VOL_FILTER:
        mask &= score_table["Vol63Ann"] <= MAX_ELIGIBLE_VOL_63

    eligible = score_table.loc[mask].index.tolist()

    if len(eligible) < MIN_ELIGIBLE_ASSETS and ALLOW_FALLBACK_TO_TOP_RANKED:
        # Relax relative strength first, but keep trend and volatility rules.
        fallback_mask = pd.Series(True, index=score_table.index)

        if REQUIRE_PRICE_ABOVE_SMA_50:
            fallback_mask &= score_table["AboveSMA50"]
        if REQUIRE_PRICE_ABOVE_SMA_126:
            fallback_mask &= score_table["AboveSMA126"]
        if REQUIRE_POSITIVE_63D_MOMENTUM:
            fallback_mask &= score_table["PositiveMom63"]
        if REQUIRE_POSITIVE_126D_MOMENTUM:
            fallback_mask &= score_table["PositiveMom126"]
        if USE_VOL_FILTER:
            fallback_mask &= score_table["Vol63Ann"] <= MAX_ELIGIBLE_VOL_63

        eligible = score_table.loc[fallback_mask].head(MIN_ELIGIBLE_ASSETS).index.tolist()

    if len(eligible) < MIN_ELIGIBLE_ASSETS and ALLOW_FALLBACK_TO_TOP_RANKED:
        # Last fallback: use top-ranked names.
        eligible = score_table.head(MIN_ELIGIBLE_ASSETS).index.tolist()

    # Apply correlation-cluster filter after ranking and eligibility screening.
    eligible = apply_correlation_filter_to_ranked_assets(
        train_returns=r,
        ranked_assets=eligible,
        min_assets=MIN_ELIGIBLE_ASSETS,
        max_assets=MAX_ELIGIBLE_ASSETS,
    )

    # Safety: ensure cap feasibility.
    min_names_needed = int(np.ceil(1.0 / MAX_RISK_ASSET_WEIGHT))

    if len(eligible) < min_names_needed:
        eligible = apply_correlation_filter_to_ranked_assets(
            train_returns=r,
            ranked_assets=score_table.index.tolist(),
            min_assets=min_names_needed,
            max_assets=max(MAX_ELIGIBLE_ASSETS, min_names_needed),
        )

    return eligible, score_table


def compute_signal_breadth(
    full_train_returns: pd.DataFrame,
    risk_assets: list[str],
) -> float:
    """
    Returns 0-to-1 market/sector breadth score.

    Higher score = risk-on.
    Lower score = more SGOV/cash.
    """
    available_assets = [a for a in risk_assets if a in full_train_returns.columns]

    if not available_assets:
        return 0.0

    r = full_train_returns[available_assets].dropna(how="all").fillna(0.0)

    if len(r) < 60:
        return 0.50

    score_table = compute_asset_score_table(r, benchmark_returns=full_train_returns[MARKET_PROXY] if MARKET_PROXY in full_train_returns.columns else None)

    if score_table.empty:
        return 0.50

    trend_breadth = (
        0.25 * score_table["AboveSMA50"].mean()
        + 0.25 * score_table["AboveSMA126"].mean()
        + 0.25 * score_table["PositiveMom63"].mean()
        + 0.25 * score_table["PositiveMom126"].mean()
    )

    market_confirm = 1.0

    if MARKET_PROXY in full_train_returns.columns:
        proxy_returns = full_train_returns[MARKET_PROXY].dropna().fillna(0.0)

        if len(proxy_returns) >= 126:
            proxy_price = (1 + proxy_returns).cumprod()

            sma_len = min(200, len(proxy_price))
            proxy_sma = proxy_price.rolling(sma_len).mean().iloc[-1]

            proxy_mom_126 = proxy_price.iloc[-1] / proxy_price.iloc[-min(126, len(proxy_price))] - 1

            proxy_above_sma = proxy_price.iloc[-1] > proxy_sma
            proxy_positive_mom = proxy_mom_126 > 0

            market_confirm = 0.50 * float(proxy_above_sma) + 0.50 * float(proxy_positive_mom)

    breadth = 0.75 * trend_breadth + 0.25 * market_confirm

    return float(np.clip(breadth, 0.0, 1.0))


def cash_weight_from_breadth(breadth: float) -> float:
    """
    breadth >= STRONG_SIGNAL_THRESHOLD -> min cash
    breadth <= WEAK_SIGNAL_THRESHOLD -> max cash
    between them -> linear interpolation
    """
    if not USE_CASH_SLEEVE:
        return 0.0

    if breadth >= STRONG_SIGNAL_THRESHOLD:
        return MIN_CASH_WEIGHT

    if breadth <= WEAK_SIGNAL_THRESHOLD:
        return MAX_CASH_WEIGHT

    weakness_ratio = (
        (STRONG_SIGNAL_THRESHOLD - breadth)
        / (STRONG_SIGNAL_THRESHOLD - WEAK_SIGNAL_THRESHOLD)
    )

    cash_weight = MIN_CASH_WEIGHT + weakness_ratio * (MAX_CASH_WEIGHT - MIN_CASH_WEIGHT)

    return float(np.clip(cash_weight, MIN_CASH_WEIGHT, MAX_CASH_WEIGHT))


# ============================================================
# BLACK-LITTERMAN VIEWS
# ============================================================

def build_momentum_views(train_returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Builds absolute Black-Litterman views from momentum scores
    for only the eligible winner basket.
    """
    assets = train_returns.columns.tolist()
    score_table = compute_asset_score_table(train_returns)

    if score_table.empty:
        daily_views = pd.Series(0.08 / TRADING_DAYS, index=assets)
    else:
        scores = score_table.reindex(assets)["Score"].fillna(0.0)
        z = safe_zscore(scores)

        annual_views = 0.10 + 0.06 * z
        annual_views = annual_views.clip(lower=-0.05, upper=0.30)

        daily_views = annual_views / TRADING_DAYS

    P = pd.DataFrame(
        np.eye(len(assets)),
        index=[f"view_{asset}" for asset in assets],
        columns=assets,
    )

    Q = pd.DataFrame(
        daily_views.values.reshape(-1, 1),
        index=P.index,
        columns=["views"],
    )

    return P, Q


# ============================================================
# WEIGHT HELPERS
# ============================================================

def normalize_to_one(weights: pd.Series) -> pd.Series:
    w = weights.copy().astype(float)
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    w = w.clip(lower=0.0)

    if w.sum() <= 0:
        w[:] = 1.0 / len(w)
    else:
        w = w / w.sum()

    return w


def cap_individual_weights(
    weights: pd.Series,
    max_weight: float,
    min_weight_to_keep: float = 0.0,
) -> pd.Series:
    """
    Enforces per-asset max weight while preserving 100% total allocation.
    """
    w = normalize_to_one(weights)

    if len(w) * max_weight < 1.0 - 1e-9:
        raise ValueError(
            f"Max weight cap {max_weight:.2%} is too restrictive for {len(w)} assets."
        )

    for _ in range(100):
        w = normalize_to_one(w)

        over = w > max_weight + 1e-12
        if not over.any():
            break

        excess = (w[over] - max_weight).sum()
        w[over] = max_weight

        under = w < max_weight - 1e-12
        if not under.any():
            break

        under_sum = w[under].sum()

        if under_sum > 0:
            w[under] += excess * (w[under] / under_sum)
        else:
            w[under] += excess / under.sum()

    if min_weight_to_keep > 0:
        keep = w >= min_weight_to_keep
        min_names_needed = int(np.ceil(1.0 / max_weight))

        if keep.sum() >= min_names_needed:
            w[~keep] = 0.0
            w = normalize_to_one(w)

            for _ in range(100):
                over = w > max_weight + 1e-12
                if not over.any():
                    break

                excess = (w[over] - max_weight).sum()
                w[over] = max_weight

                under = (w > 0) & (w < max_weight - 1e-12)
                if not under.any():
                    break

                under_sum = w[under].sum()
                if under_sum > 0:
                    w[under] += excess * (w[under] / under_sum)
                else:
                    break

                w = normalize_to_one(w)

    return w


def extract_weight_series(w: pd.DataFrame | pd.Series, assets: list[str]) -> pd.Series:
    if isinstance(w, pd.DataFrame):
        if w.shape[1] == 1:
            s = w.iloc[:, 0]
        elif "weights" in w.columns:
            s = w["weights"]
        else:
            s = w.iloc[:, 0]
    else:
        s = w.copy()

    s = s.reindex(assets).fillna(0.0)
    return normalize_to_one(s)


def equal_weight(assets: list[str]) -> pd.Series:
    w = pd.Series(1.0 / len(assets), index=assets)
    return cap_individual_weights(w, MAX_RISK_ASSET_WEIGHT)


def apply_cash_sleeve(
    risk_weights: pd.Series,
    cash_weight: float,
    final_assets: list[str],
) -> pd.Series:
    final_weights = pd.Series(0.0, index=final_assets)

    scaled_risk_weights = risk_weights * (1.0 - cash_weight)

    for asset, weight in scaled_risk_weights.items():
        if asset in final_weights.index:
            final_weights.loc[asset] = weight

    if USE_CASH_SLEEVE and CASH_TICKER in final_weights.index:
        final_weights.loc[CASH_TICKER] = cash_weight

    final_weights[final_weights < MIN_WEIGHT_TO_KEEP] = 0.0

    if final_weights.sum() > 0:
        final_weights = final_weights / final_weights.sum()

    return final_weights


def prune_tiny_positions_after_turnover(
    weights: pd.Series,
    min_position_weight: float = MIN_POSITION_WEIGHT_AFTER_REBALANCE,
    max_final_holdings: int = MAX_FINAL_HOLDINGS_AFTER_PRUNE,
) -> pd.Series:
    """
    V5.6 cleanup layer.

    Purpose:
    - Keep the 20% turnover cap to avoid whipsaw.
    - But remove tiny stale residual positions after the turnover cap is applied.

    Behavior:
    - Keeps SGOV/cash if present.
    - Keeps non-cash positions >= min_position_weight.
    - Also limits non-cash positions to the top max_final_holdings by weight.
    - Redistributes removed dust pro-rata to the kept positions.
    """
    if not PRUNE_TINY_POSITIONS_AFTER_TURNOVER:
        return weights

    w = weights.copy().astype(float)
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    w = w.clip(lower=0.0)

    if w.sum() <= 0:
        return w

    w = w / w.sum()

    cash_weight = 0.0
    if CASH_TICKER in w.index:
        cash_weight = float(w.loc[CASH_TICKER])

    non_cash = w.drop(labels=[CASH_TICKER], errors="ignore")
    non_cash = non_cash[non_cash > 0].sort_values(ascending=False)

    keep_non_cash = non_cash[non_cash >= min_position_weight]
    keep_non_cash = keep_non_cash.head(max_final_holdings)

    cleaned = pd.Series(0.0, index=w.index)

    if CASH_TICKER in cleaned.index and cash_weight > 0:
        cleaned.loc[CASH_TICKER] = cash_weight

    cleaned.loc[keep_non_cash.index] = keep_non_cash

    # If pruning removed everything except no cash, keep the largest original names.
    if cleaned.sum() <= 0:
        fallback = non_cash.head(max_final_holdings)
        cleaned.loc[fallback.index] = fallback

    if cleaned.sum() > 0:
        cleaned = cleaned / cleaned.sum()

    return cleaned


def calculate_turnover(
    previous_weights: pd.Series | None,
    current_weights: pd.Series,
    all_assets: list[str],
) -> float:
    """
    One-way turnover:
    0.5 * sum(abs(current - previous))
    """
    if previous_weights is None:
        return np.nan

    prev = previous_weights.reindex(all_assets).fillna(0.0)
    curr = current_weights.reindex(all_assets).fillna(0.0)

    return float(0.5 * np.abs(curr - prev).sum())


def estimate_active_sleeve_vol(
    train_returns: pd.DataFrame,
    risk_weights: pd.Series,
    lookback_days: int = 63,
) -> float:
    """
    Estimates annualized trailing volatility of the active risk sleeve.
    """
    assets = [a for a in risk_weights.index if a in train_returns.columns and risk_weights[a] > 0]

    if not assets:
        return 0.0

    r = train_returns[assets].tail(min(lookback_days, len(train_returns))).fillna(0.0)
    w = risk_weights.reindex(assets).fillna(0.0)

    if w.sum() <= 0:
        return 0.0

    w = w / w.sum()

    sleeve_returns = r.dot(w)
    return float(sleeve_returns.std() * np.sqrt(TRADING_DAYS))


def cash_weight_from_vol(active_sleeve_vol: float) -> float:
    """
    Adds SGOV/cash when the selected winner basket is too volatile.
    """
    if not USE_VOL_TARGET_CASH_SCALING:
        return 0.0

    if active_sleeve_vol <= 0 or active_sleeve_vol <= TARGET_ACTIVE_SLEEVE_VOL:
        return 0.0

    cash_weight = 1.0 - (TARGET_ACTIVE_SLEEVE_VOL / active_sleeve_vol)

    return float(np.clip(cash_weight, 0.0, MAX_VOL_BASED_CASH_WEIGHT))


def apply_turnover_cap(
    previous_weights: pd.Series | None,
    target_weights: pd.Series,
    all_assets: list[str],
    max_turnover: float,
) -> pd.Series:
    """
    Caps one-way turnover by moving only partway from previous weights to target weights.
    """
    if previous_weights is None or not USE_TURNOVER_CAP:
        return target_weights

    prev = previous_weights.reindex(all_assets).fillna(0.0)
    target = target_weights.reindex(all_assets).fillna(0.0)

    raw_turnover = 0.5 * np.abs(target - prev).sum()

    if raw_turnover <= max_turnover or raw_turnover <= 1e-12:
        return target_weights

    blend = max_turnover / raw_turnover
    capped = prev + blend * (target - prev)
    capped = capped.clip(lower=0.0)

    if capped.sum() > 0:
        capped = capped / capped.sum()

    return capped


# ============================================================
# RISKFOLIO OPTIMIZER
# ============================================================

def optimize_winner_basket(train_returns: pd.DataFrame, eligible_assets: list[str]) -> pd.Series:
    """
    Uses Riskfolio only after the winner basket has been selected.

    V5.9b default:
    - V5.7 signal/selection logic.
    - Classic CVaR Sharpe portfolio construction.
    - 15-position / 2% final pruning for a cleaner tradeable portfolio.
    """
    r = train_returns[eligible_assets]
    r = r.dropna(axis=1, how="all")
    r = r.dropna(axis=0, how="any")

    available_assets = r.columns.tolist()

    if len(available_assets) < MIN_ELIGIBLE_ASSETS or r.shape[0] < 60:
        return equal_weight(eligible_assets)

    try:
        port = rp.Portfolio(
            returns=r,
            upperlng=MAX_RISK_ASSET_WEIGHT,
            sht=False,
        )

        port.assets_stats(
            method_mu="hist",
            method_cov="ledoit",
        )

        w = port.optimization(
            model="Classic",
            rm="CVaR",
            obj="Sharpe",
            rf=DAILY_RF,
            hist=True,
        )

        if w is None or len(w) == 0:
            raise RuntimeError("Classic CVaR Sharpe optimizer returned empty weights.")

        s = extract_weight_series(w, available_assets)

        s = cap_individual_weights(
            s,
            max_weight=MAX_RISK_ASSET_WEIGHT,
            min_weight_to_keep=MIN_WEIGHT_TO_KEEP,
        )

        return s.reindex(eligible_assets).fillna(0.0)

    except Exception as cvar_error:
        print(f"Classic CVaR Sharpe optimization failed. Falling back to Classic MAD Sharpe. Error: {cvar_error}")

        try:
            port = rp.Portfolio(
                returns=r,
                upperlng=MAX_RISK_ASSET_WEIGHT,
                sht=False,
            )

            port.assets_stats(
                method_mu="hist",
                method_cov="ledoit",
            )

            w = port.optimization(
                model="Classic",
                rm="MAD",
                obj="Sharpe",
                rf=DAILY_RF,
                hist=True,
            )

            if w is None or len(w) == 0:
                raise RuntimeError("Classic MAD Sharpe optimizer returned empty weights.")

            s = extract_weight_series(w, available_assets)

            s = cap_individual_weights(
                s,
                max_weight=MAX_RISK_ASSET_WEIGHT,
                min_weight_to_keep=MIN_WEIGHT_TO_KEEP,
            )

            return s.reindex(eligible_assets).fillna(0.0)

        except Exception as mad_error:
            print(f"Classic MAD Sharpe optimization failed. Falling back to equal weight. Error: {mad_error}")
            return equal_weight(eligible_assets)


# ============================================================
# ANALYSIS HELPERS
# ============================================================

def performance_stats(return_series: pd.Series, label: str) -> dict:
    r = return_series.dropna()

    if r.empty:
        return {
            "Name": label,
            "Total Return": np.nan,
            "CAGR": np.nan,
            "Annual Volatility": np.nan,
            "Sharpe": np.nan,
            "Max Drawdown": np.nan,
            "Daily Observations": 0,
        }

    equity = (1 + r).cumprod()

    total_return = equity.iloc[-1] - 1
    years = len(r) / TRADING_DAYS
    cagr = equity.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan

    vol = r.std() * np.sqrt(TRADING_DAYS)

    sharpe = (
        ((r.mean() - DAILY_RF) / r.std()) * np.sqrt(TRADING_DAYS)
        if r.std() > 0
        else np.nan
    )

    drawdown = equity / equity.cummax() - 1
    max_drawdown = drawdown.min()

    return {
        "Name": label,
        "Total Return": total_return,
        "CAGR": cagr,
        "Annual Volatility": vol,
        "Sharpe": sharpe,
        "Max Drawdown": max_drawdown,
        "Daily Observations": len(r),
    }


def make_benchmark_comparison(
    strategy_returns: pd.Series,
    all_returns: pd.DataFrame,
    benchmark_tickers: list[str],
) -> pd.DataFrame:
    rows = [performance_stats(strategy_returns, "Strategy")]

    aligned_index = strategy_returns.index

    for ticker in benchmark_tickers:
        if ticker in all_returns.columns:
            benchmark_returns = all_returns.loc[aligned_index, ticker].dropna()
            rows.append(performance_stats(benchmark_returns, ticker))

    return pd.DataFrame(rows).set_index("Name")


def make_monthly_return_table(
    strategy_returns: pd.Series,
    all_returns: pd.DataFrame,
    benchmark_tickers: list[str],
) -> pd.DataFrame:
    monthly = pd.DataFrame()

    monthly["Strategy"] = strategy_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)

    for ticker in benchmark_tickers:
        if ticker in all_returns.columns:
            monthly[ticker] = all_returns.loc[strategy_returns.index, ticker].resample("ME").apply(
                lambda x: (1 + x).prod() - 1
            )

    monthly.index.name = "Month"

    return monthly


def make_drawdown_table(
    strategy_returns: pd.Series,
    all_returns: pd.DataFrame,
    benchmark_tickers: list[str],
) -> pd.DataFrame:
    drawdowns = pd.DataFrame(index=strategy_returns.index)

    strategy_equity = (1 + strategy_returns).cumprod()
    drawdowns["Strategy"] = strategy_equity / strategy_equity.cummax() - 1

    for ticker in benchmark_tickers:
        if ticker in all_returns.columns:
            r = all_returns.loc[strategy_returns.index, ticker].fillna(0.0)
            equity = (1 + r).cumprod()
            drawdowns[ticker] = equity / equity.cummax() - 1

    drawdowns.index.name = "Date"

    return drawdowns


def save_correlation_heatmap(corr: pd.DataFrame, output_file: Path) -> None:
    """
    Saves a memory-safe correlation heatmap.

    The full correlation matrix is still saved as CSV. The PNG heatmap is capped
    to HEATMAP_MAX_ASSETS so large ETF universes do not create a massive image
    and get the process killed by the OS.
    """
    if corr.empty:
        return

    plot_corr = corr.copy()

    if len(plot_corr.columns) > HEATMAP_MAX_ASSETS:
        plot_corr = plot_corr.iloc[:HEATMAP_MAX_ASSETS, :HEATMAP_MAX_ASSETS]
        print(
            f"Correlation heatmap limited to first {HEATMAP_MAX_ASSETS} assets "
            f"to avoid memory issues. Full matrix is still saved as CSV."
        )

    n = len(plot_corr.columns)
    fig_size = min(max(8, n * 0.35), HEATMAP_MAX_FIG_SIZE)

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))

    im = ax.imshow(plot_corr.values, aspect="auto")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))

    ax.set_xticklabels(plot_corr.columns, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(plot_corr.index, fontsize=7)

    ax.set_title("Correlation Heatmap")

    # Annotate only small heatmaps.
    if n <= 20:
        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    f"{plot_corr.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                )

    fig.tight_layout()
    fig.savefig(output_file, dpi=120)
    plt.close(fig)



def make_tradeable_display_weights(
    weights: pd.Series,
    min_display_weight: float = TRADEABLE_MIN_WEIGHT,
) -> pd.Series:
    """
    Creates a clean human-readable allocation by removing tiny weights.
    Backtest math uses the actual pruned portfolio weights.
    """
    w = weights.copy().astype(float)
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    w = w.clip(lower=0.0)

    display = w[w >= min_display_weight].sort_values(ascending=False)

    if display.sum() > 0:
        display = display / display.sum()

    return display


def save_final_portfolio_correlation_outputs(
    all_returns: pd.DataFrame,
    final_weights: pd.Series,
    output_dir: Path,
    min_weight: float = MIN_PRINT_WEIGHT,
) -> None:
    """
    Saves correlation outputs only for the final target portfolio holdings.

    Outputs:
    - final_portfolio_correlation_matrix.csv
    - final_portfolio_correlation_heatmap.png
    - final_portfolio_high_correlation_pairs.csv
    """
    holdings = (
        final_weights[final_weights >= min_weight]
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    holdings = [ticker for ticker in holdings if ticker in all_returns.columns]

    if len(holdings) < 2:
        print("Not enough final holdings to create final portfolio correlation heatmap.")
        return

    final_corr = all_returns[holdings].corr()
    final_corr.to_csv(output_dir / "final_portfolio_correlation_matrix.csv")

    # Save high-correlation pair list for easier review.
    pair_rows = []

    for i, ticker_a in enumerate(holdings):
        for ticker_b in holdings[i + 1:]:
            pair_rows.append(
                {
                    "TickerA": ticker_a,
                    "TickerB": ticker_b,
                    "Correlation": final_corr.loc[ticker_a, ticker_b],
                    "AbsCorrelation": abs(final_corr.loc[ticker_a, ticker_b]),
                    "WeightA": final_weights.get(ticker_a, 0.0),
                    "WeightB": final_weights.get(ticker_b, 0.0),
                }
            )

    if pair_rows:
        pair_df = pd.DataFrame(pair_rows).sort_values("AbsCorrelation", ascending=False)
        pair_df.to_csv(output_dir / "final_portfolio_high_correlation_pairs.csv", index=False)

    n = len(final_corr.columns)
    fig_size = min(max(9, n * 0.45), FINAL_PORTFOLIO_HEATMAP_MAX_FIG_SIZE)

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))

    im = ax.imshow(final_corr.values, aspect="auto", vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    font_size = 8 if n <= 25 else 6

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))

    ax.set_xticklabels(final_corr.columns, rotation=45, ha="right", fontsize=font_size)
    ax.set_yticklabels(final_corr.index, fontsize=font_size)

    ax.set_title("Final Portfolio Correlation Heatmap")

    # Annotate only if readable.
    if n <= 25:
        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    f"{final_corr.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                )

    fig.tight_layout()
    fig.savefig(output_dir / "final_portfolio_correlation_heatmap.png", dpi=140)
    plt.close(fig)

    print(f"Final portfolio correlation outputs saved for {n} holdings.")




def get_rebalance_dates(returns_index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """
    Returns rebalance dates based on REBALANCE_MODE.

    month_start:
        first available trading day of each calendar month after enough LOOKBACK history.
        If the 1st is a weekend/holiday, this uses the next trading day in the data.

    fixed_days:
        old behavior: every REBALANCE_DAYS trading days after LOOKBACK.
    """
    idx = pd.DatetimeIndex(returns_index).sort_values()

    if len(idx) <= LOOKBACK:
        return idx[0:0]

    eligible_idx = idx[LOOKBACK:]

    rebalance_mode = globals().get("REBALANCE_MODE", "month_start")

    if rebalance_mode == "fixed_days":
        return idx[LOOKBACK::REBALANCE_DAYS]

    if rebalance_mode != "month_start":
        raise ValueError(
            f"Unsupported REBALANCE_MODE={rebalance_mode!r}. "
            "Use 'month_start' or 'fixed_days'."
        )

    eligible_dates = pd.Series(eligible_idx, index=eligible_idx)
    month_keys = eligible_dates.index.to_period("M")

    # groupby(...).first() selects the first available trading day in each month.
    rebalance_dates = eligible_dates.groupby(month_keys).first()

    return pd.DatetimeIndex(rebalance_dates.values)

def build_final_portfolio_selection_reasons(
    final_weights: pd.Series,
    latest_score_table: pd.DataFrame,
    latest_eligible_assets: list[str],
    min_weight: float = MIN_PRINT_WEIGHT,
) -> pd.DataFrame:
    """
    Explains why each final holding appears in the portfolio.

    This distinguishes:
    - current eligible holdings,
    - residual/carryover holdings created by turnover control,
    - SGOV/cash sleeve holdings.
    """
    rows = []
    latest_eligible_set = set(latest_eligible_assets or [])

    for ticker, weight in final_weights.items():
        if weight < min_weight:
            continue

        row = {
            "Ticker": ticker,
            "Weight": float(weight),
            "WeightPct": float(weight) * 100.0,
            "InLatestEligibleBasket": ticker in latest_eligible_set,
            "Reason": "",
        }

        if ticker == CASH_TICKER:
            row["Reason"] = "Cash/volatility-control sleeve or cash residual after pruning."
            rows.append(row)
            continue

        if latest_score_table is not None and not latest_score_table.empty and ticker in latest_score_table.index:
            s = latest_score_table.loc[ticker]

            row.update(
                {
                    "Score": s.get("Score", np.nan),
                    "EligibleNow": ticker in latest_eligible_set,
                    "Mom21": s.get("Mom21", np.nan),
                    "Mom63": s.get("Mom63", np.nan),
                    "Mom126": s.get("Mom126", np.nan),
                    "RS63VsSPY": s.get("RS63VsSPY", np.nan),
                    "RS126VsSPY": s.get("RS126VsSPY", np.nan),
                    "Vol63Ann": s.get("Vol63Ann", np.nan),
                    "AboveSMA50": bool(s.get("AboveSMA50", False)),
                    "AboveSMA126": bool(s.get("AboveSMA126", False)),
                    "PositiveMom63": bool(s.get("PositiveMom63", False)),
                    "PositiveMom126": bool(s.get("PositiveMom126", False)),
                    "OutperformSPY63DiagnosticOnly": bool(s.get("OutperformSPY63", False)),
                    "OutperformSPY126DiagnosticOnly": bool(s.get("OutperformSPY126", False)),
                }
            )

            if ticker in latest_eligible_set:
                row["Reason"] = "Current eligible ETF selected by the V5.7/V5.9b signal layer."
            elif weight >= TRADEABLE_MIN_WEIGHT:
                row["Reason"] = "Carryover/kept holding from prior rebalance; still above pruning threshold."
            else:
                row["Reason"] = "Small residual holding; kept only because it passed minimum output threshold."
        else:
            row["Reason"] = "No latest score row available; likely cash-like, benchmark-only, or residual."

        rows.append(row)

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values("Weight", ascending=False)

    return result


def make_worst_month_report(
    monthly_returns: pd.DataFrame,
    benchmark_tickers: list[str],
    top_n: int = 24,
) -> pd.DataFrame:
    """
    Returns worst strategy months with benchmark-relative monthly excess returns.
    """
    report = monthly_returns.copy()

    for ticker in benchmark_tickers:
        if ticker in report.columns:
            report[f"StrategyMinus{ticker}"] = report["Strategy"] - report[ticker]

    report = report.sort_values("Strategy", ascending=True).head(top_n)
    report.index.name = "Month"

    return report


def make_rolling_12m_underperformance_report(
    monthly_returns: pd.DataFrame,
    benchmark_tickers: list[str],
) -> pd.DataFrame:
    """
    Creates rolling 12-month compounded returns and excess returns versus benchmarks.
    """
    rolling = pd.DataFrame(index=monthly_returns.index)

    for col in monthly_returns.columns:
        rolling[f"{col}_Rolling12M"] = (
            (1.0 + monthly_returns[col])
            .rolling(12)
            .apply(np.prod, raw=True)
            - 1.0
        )

    for ticker in benchmark_tickers:
        strategy_col = "Strategy_Rolling12M"
        benchmark_col = f"{ticker}_Rolling12M"

        if strategy_col in rolling.columns and benchmark_col in rolling.columns:
            rolling[f"StrategyMinus{ticker}_Rolling12M"] = (
                rolling[strategy_col] - rolling[benchmark_col]
            )

    rolling = rolling.dropna(how="all")
    rolling.index.name = "Month"

    return rolling


def make_rolling_12m_summary(
    rolling_12m: pd.DataFrame,
    benchmark_tickers: list[str],
) -> pd.DataFrame:
    """
    Summarizes rolling 12-month excess-return behavior versus benchmarks.
    """
    rows = []

    for ticker in benchmark_tickers:
        excess_col = f"StrategyMinus{ticker}_Rolling12M"

        if excess_col not in rolling_12m.columns:
            continue

        excess = rolling_12m[excess_col].dropna()

        if excess.empty:
            continue

        worst_month = excess.idxmin()
        best_month = excess.idxmax()

        rows.append(
            {
                "Benchmark": ticker,
                "RollingPeriods": int(excess.count()),
                "Average12MExcess": float(excess.mean()),
                "Median12MExcess": float(excess.median()),
                "Worst12MExcess": float(excess.min()),
                "Worst12MExcessMonth": worst_month,
                "Best12MExcess": float(excess.max()),
                "Best12MExcessMonth": best_month,
                "Latest12MExcess": float(excess.iloc[-1]),
                "HitRate12M": float((excess >= 0).mean()),
            }
        )

    return pd.DataFrame(rows)


def make_worst_rolling_12m_underperformance(
    rolling_12m: pd.DataFrame,
    benchmark_tickers: list[str],
    top_n: int = 24,
) -> pd.DataFrame:
    """
    Finds the worst rolling 12-month underperformance rows versus any benchmark.
    """
    rows = []

    for ticker in benchmark_tickers:
        excess_col = f"StrategyMinus{ticker}_Rolling12M"

        if excess_col not in rolling_12m.columns:
            continue

        temp = rolling_12m[[excess_col]].dropna().copy()
        temp["Benchmark"] = ticker
        temp["ExcessReturn"] = temp[excess_col]
        temp = temp.drop(columns=[excess_col])
        rows.append(temp)

    if not rows:
        return pd.DataFrame()

    combined = pd.concat(rows).sort_values("ExcessReturn", ascending=True).head(top_n)
    combined.index.name = "Month"

    return combined


def run_backtest_for_start_window(
    base_returns: pd.DataFrame,
    risk_tickers: list[str],
    start_date: str,
    output_dir: Path,
) -> dict:
    """
    Runs the V5.9b strategy for one start window and writes full outputs.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    returns_window_raw = base_returns.loc[pd.Timestamp(start_date):].copy()

    min_valid_rows = int(len(returns_window_raw) * MIN_VALID_RATIO)

    available_risk_tickers = [
        t for t in risk_tickers
        if t in returns_window_raw.columns and returns_window_raw[t].notna().sum() >= min_valid_rows
    ]

    if len(available_risk_tickers) < MIN_ELIGIBLE_ASSETS:
        raise ValueError(
            f"{start_date}: Need at least {MIN_ELIGIBLE_ASSETS} valid risk assets after cleaning."
        )

    required_non_risk = [
        t for t in [CASH_TICKER, MARKET_PROXY, *BENCHMARK_TICKERS]
        if t in returns_window_raw.columns
    ]

    keep_columns = list(dict.fromkeys(available_risk_tickers + required_non_risk))
    returns = returns_window_raw[keep_columns].fillna(0.0)

    if USE_CASH_SLEEVE and CASH_TICKER not in returns.columns:
        print(f"{start_date}: {CASH_TICKER} not available. Using synthetic daily cash return.")
        returns[CASH_TICKER] = DAILY_RF

    final_assets = available_risk_tickers.copy()

    if USE_CASH_SLEEVE and CASH_TICKER not in final_assets:
        final_assets.append(CASH_TICKER)

    corr = returns[available_risk_tickers].corr()
    corr.to_csv(output_dir / "correlation_matrix.csv")
    save_correlation_heatmap(corr, output_dir / "correlation_heatmap.png")

    rebalance_dates = get_rebalance_dates(returns.index)

    if len(rebalance_dates) == 0:
        raise ValueError(f"{start_date}: Not enough return history for selected LOOKBACK.")

    weights_by_date = {}
    signal_by_date = []
    turnover_rows = []
    eligibility_rows = []
    daily_portfolio_returns = []

    previous_weights = None
    latest_score_table = pd.DataFrame()
    latest_eligible_assets = []

    print(f"\nRunning V5.10 month-start/V5.9b start window {start_date} with {len(rebalance_dates)} rebalance dates...")

    for i, date in enumerate(rebalance_dates):
        full_train_returns = returns.loc[:date]
        train_returns = returns.loc[:date].iloc[-LOOKBACK:]

        signal_breadth = compute_signal_breadth(
            full_train_returns=full_train_returns,
            risk_assets=available_risk_tickers,
        )

        eligible_assets, score_table = select_eligible_assets(
            train_returns=train_returns,
            risk_assets=available_risk_tickers,
        )

        latest_score_table = score_table.copy()
        latest_eligible_assets = eligible_assets.copy()

        risk_weights = optimize_winner_basket(
            train_returns=train_returns,
            eligible_assets=eligible_assets,
        )

        active_sleeve_vol = estimate_active_sleeve_vol(
            train_returns=train_returns,
            risk_weights=risk_weights,
        )

        breadth_cash_weight = cash_weight_from_breadth(signal_breadth)
        vol_cash_weight = cash_weight_from_vol(active_sleeve_vol)
        cash_weight = max(breadth_cash_weight, vol_cash_weight)

        target_final_weights = apply_cash_sleeve(
            risk_weights=risk_weights,
            cash_weight=cash_weight,
            final_assets=final_assets,
        )

        final_weights = apply_turnover_cap(
            previous_weights=previous_weights,
            target_weights=target_final_weights,
            all_assets=final_assets,
            max_turnover=MAX_TURNOVER_PER_REBALANCE,
        )

        turnover_before_prune = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=final_weights,
            all_assets=final_assets,
        )

        final_weights = prune_tiny_positions_after_turnover(final_weights)

        turnover = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=final_weights,
            all_assets=final_assets,
        )

        previous_weights = final_weights.copy()
        weights_by_date[date] = final_weights

        score_table_out = score_table.copy()
        score_table_out["Date"] = date
        score_table_out["StartWindow"] = start_date
        score_table_out["Eligible"] = score_table_out.index.isin(eligible_assets)
        score_table_out["Rank"] = range(1, len(score_table_out) + 1)
        score_table_out = score_table_out.reset_index().rename(columns={"index": "Ticker"})
        eligibility_rows.append(score_table_out)

        signal_by_date.append(
            {
                "Date": date,
                "StartWindow": start_date,
                "SignalBreadth": signal_breadth,
                "CashWeight": cash_weight,
                "BreadthCashWeight": breadth_cash_weight,
                "VolCashWeight": vol_cash_weight,
                "ActiveSleeveVol": active_sleeve_vol,
                "RiskWeight": 1.0 - cash_weight,
                "EligibleAssets": ",".join(eligible_assets),
                "EligibleCount": len(eligible_assets),
            }
        )

        turnover_rows.append(
            {
                "Date": date,
                "StartWindow": start_date,
                "Turnover": turnover,
                "TurnoverBeforePrune": turnover_before_prune,
                "ExtraTurnoverFromPrune": max(0.0, turnover - turnover_before_prune),
                "SignalBreadth": signal_breadth,
                "CashWeight": cash_weight,
                "BreadthCashWeight": breadth_cash_weight,
                "VolCashWeight": vol_cash_weight,
                "ActiveSleeveVol": active_sleeve_vol,
                "EligibleAssets": ",".join(eligible_assets),
                "EligibleCount": len(eligible_assets),
            }
        )

        if i + 1 < len(rebalance_dates):
            next_date = rebalance_dates[i + 1]
            forward_returns = returns.loc[
                (returns.index > date) & (returns.index <= next_date),
                final_assets,
            ]
        else:
            forward_returns = returns.loc[
                returns.index > date,
                final_assets,
            ]

        if not forward_returns.empty:
            period_portfolio_returns = forward_returns.dot(final_weights)
            daily_portfolio_returns.append(period_portfolio_returns)

        if i == 0 or (i + 1) % 10 == 0 or i + 1 == len(rebalance_dates):
            top_weights = final_weights.sort_values(ascending=False).head(5).round(4).to_dict()
            print(
                f"{start_date} | {date.date()} | "
                f"turnover={turnover if not np.isnan(turnover) else 0:.2%} | "
                f"cash={cash_weight:.2%} | "
                f"eligible={len(eligible_assets)} | "
                f"top={top_weights}"
            )

    weights_df = pd.DataFrame(weights_by_date).T
    weights_df.index.name = "RebalanceDate"
    weights_df.to_csv(output_dir / "weights_by_rebalance.csv")

    signal_df = pd.DataFrame(signal_by_date)
    signal_df.to_csv(output_dir / "signal_cash_history.csv", index=False)

    turnover_df = pd.DataFrame(turnover_rows)
    turnover_df.to_csv(output_dir / "turnover_by_rebalance.csv", index=False)

    eligibility_df = pd.concat(eligibility_rows, ignore_index=True)
    eligibility_df.to_csv(output_dir / "eligibility_history.csv", index=False)

    final_weights = weights_df.iloc[-1].sort_values(ascending=False)
    final_weights = final_weights[final_weights >= MIN_PRINT_WEIGHT]
    final_weights.to_csv(output_dir / "final_target_weights.csv", header=["Weight"])

    tradeable_final_weights = make_tradeable_display_weights(
        final_weights,
        min_display_weight=TRADEABLE_MIN_WEIGHT,
    )
    tradeable_final_weights.to_csv(
        output_dir / "final_target_weights_tradeable.csv",
        header=["Weight"],
    )

    final_reasons = build_final_portfolio_selection_reasons(
        final_weights=final_weights,
        latest_score_table=latest_score_table,
        latest_eligible_assets=latest_eligible_assets,
        min_weight=MIN_PRINT_WEIGHT,
    )
    final_reasons.to_csv(output_dir / "final_portfolio_selection_reasons.csv", index=False)

    save_final_portfolio_correlation_outputs(
        all_returns=returns,
        final_weights=final_weights,
        output_dir=output_dir,
        min_weight=MIN_PRINT_WEIGHT,
    )

    if daily_portfolio_returns:
        strategy_returns = pd.concat(daily_portfolio_returns).sort_index()
    else:
        strategy_returns = pd.Series(dtype=float, name="Strategy")

    strategy_returns.name = "Strategy"

    strategy_equity = (1 + strategy_returns).cumprod()

    portfolio_backtest = pd.DataFrame(
        {
            "DailyReturn": strategy_returns,
            "EquityCurve": strategy_equity,
        }
    )
    portfolio_backtest.index.name = "Date"
    portfolio_backtest.to_csv(output_dir / "portfolio_backtest.csv")

    benchmark_summary = make_benchmark_comparison(
        strategy_returns=strategy_returns,
        all_returns=returns,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    benchmark_summary.to_csv(output_dir / "benchmark_comparison.csv")

    monthly_returns = make_monthly_return_table(
        strategy_returns=strategy_returns,
        all_returns=returns,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    monthly_returns.to_csv(output_dir / "monthly_returns.csv")

    worst_months = make_worst_month_report(
        monthly_returns=monthly_returns,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    worst_months.to_csv(output_dir / "worst_months.csv")

    rolling_12m = make_rolling_12m_underperformance_report(
        monthly_returns=monthly_returns,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    rolling_12m.to_csv(output_dir / "rolling_12m_underperformance.csv")

    rolling_12m_summary = make_rolling_12m_summary(
        rolling_12m=rolling_12m,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    rolling_12m_summary.to_csv(output_dir / "rolling_12m_summary.csv", index=False)

    worst_rolling_12m = make_worst_rolling_12m_underperformance(
        rolling_12m=rolling_12m,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    worst_rolling_12m.to_csv(output_dir / "worst_rolling_12m_underperformance.csv")

    drawdown_data = make_drawdown_table(
        strategy_returns=strategy_returns,
        all_returns=returns,
        benchmark_tickers=BENCHMARK_TICKERS,
    )
    drawdown_data.to_csv(output_dir / "drawdown_data.csv")

    strategy_row = benchmark_summary.loc["Strategy"].to_dict()
    strategy_row["StartWindow"] = start_date
    strategy_row["AverageTurnover"] = turnover_df["Turnover"].dropna().mean()
    strategy_row["MedianTurnover"] = turnover_df["Turnover"].dropna().median()
    strategy_row["AverageExtraTurnoverFromPrune"] = turnover_df["ExtraTurnoverFromPrune"].dropna().mean()
    strategy_row["FinalHoldings"] = int((final_weights > 0).sum())
    strategy_row["FinalCashWeight"] = float(final_weights.get(CASH_TICKER, 0.0))

    # Add benchmark deltas to the walk-forward row.
    for bench in BENCHMARK_TICKERS:
        if bench in benchmark_summary.index:
            strategy_row[f"CAGREdgeVs{bench}"] = (
                strategy_row["CAGR"] - benchmark_summary.loc[bench, "CAGR"]
            )
            strategy_row[f"SharpeEdgeVs{bench}"] = (
                strategy_row["Sharpe"] - benchmark_summary.loc[bench, "Sharpe"]
            )
            strategy_row[f"MaxDDEdgeVs{bench}"] = (
                strategy_row["Max Drawdown"] - benchmark_summary.loc[bench, "Max Drawdown"]
            )
            strategy_row[f"VolEdgeVs{bench}"] = (
                strategy_row["Annual Volatility"] - benchmark_summary.loc[bench, "Annual Volatility"]
            )

    print(f"\n{start_date} final target weights:")
    print((final_weights * 100).round(2).astype(str) + "%")

    print(f"\n{start_date} benchmark comparison:")
    print(benchmark_summary)

    return {
        "StartWindow": start_date,
        "OutputDir": str(output_dir),
        "strategy_summary": strategy_row,
        "benchmark_summary": benchmark_summary.reset_index().assign(StartWindow=start_date),
        "rolling_12m_summary": rolling_12m_summary.assign(StartWindow=start_date),
    }

# ============================================================
# MAIN BACKTEST
# ============================================================

def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    WALK_FORWARD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    risk_tickers = load_tickers(CSV_FILE)

    # Keep cash-like ETFs controlled by the explicit cash sleeve, not by the active risk optimizer.
    if USE_CASH_SLEEVE:
        risk_tickers = [t for t in risk_tickers if t not in CASH_EQUIVALENT_TICKERS]

    download_tickers = risk_tickers.copy()

    extra_tickers = []

    if USE_CASH_SLEEVE:
        extra_tickers.append(CASH_TICKER)

    extra_tickers.extend(BENCHMARK_TICKERS)

    if MARKET_PROXY not in extra_tickers:
        extra_tickers.append(MARKET_PROXY)

    for ticker in extra_tickers:
        if ticker not in download_tickers:
            download_tickers.append(ticker)

    start_dates = WALK_FORWARD_START_DATES if RUN_WALK_FORWARD_SUMMARY else [START_DATE]
    download_start_date = min(start_dates)

    print(f"Loaded {len(risk_tickers)} ETF tickers from file.")
    print(risk_tickers)
    print(f"Downloading prices from {download_start_date} to {END_DATE}...")
    print(f"Rebalance mode: {globals().get('REBALANCE_MODE', 'month_start')}")

    prices = download_prices(
        download_tickers,
        start_date=download_start_date,
        end_date=END_DATE,
    )

    print("\nDownloaded price panel:")
    print(f"Rows: {len(prices)}")
    print(f"Columns: {len(prices.columns)}")
    print(f"Date range: {prices.index.min()} to {prices.index.max()}")
    print(f"Tickers downloaded: {list(prices.columns)}")

    base_returns = prices.pct_change(fill_method=None)
    base_returns = base_returns.replace([np.inf, -np.inf], np.nan)

    run_results = []

    for start_date in start_dates:
        year_label = str(pd.Timestamp(start_date).year)
        run_output_dir = WALK_FORWARD_OUTPUT_DIR / year_label

        result = run_backtest_for_start_window(
            base_returns=base_returns,
            risk_tickers=risk_tickers,
            start_date=start_date,
            output_dir=run_output_dir,
        )

        run_results.append(result)

    # ------------------------------------------------------------
    # Consolidated walk-forward outputs
    # ------------------------------------------------------------
    walk_forward_summary = pd.DataFrame(
        [r["strategy_summary"] for r in run_results]
    )
    walk_forward_summary = walk_forward_summary.set_index("StartWindow")
    walk_forward_summary.to_csv(OUTPUT_DIR / "walk_forward_summary.csv")

    benchmark_by_window = pd.concat(
        [r["benchmark_summary"] for r in run_results],
        ignore_index=True,
    )
    benchmark_by_window.to_csv(OUTPUT_DIR / "benchmark_comparison_by_window.csv", index=False)

    rolling_12m_summary_by_window = pd.concat(
        [r["rolling_12m_summary"] for r in run_results],
        ignore_index=True,
    )
    rolling_12m_summary_by_window.to_csv(
        OUTPUT_DIR / "rolling_12m_summary_by_window.csv",
        index=False,
    )

    print("\nWalk-forward summary:")
    print(walk_forward_summary)

    print("\nFiles written:")
    print(f"- {OUTPUT_DIR / 'walk_forward_summary.csv'}")
    print(f"- {OUTPUT_DIR / 'benchmark_comparison_by_window.csv'}")
    print(f"- {OUTPUT_DIR / 'rolling_12m_summary_by_window.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'final_portfolio_selection_reasons.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'worst_months.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'rolling_12m_underperformance.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'worst_rolling_12m_underperformance.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'benchmark_comparison.csv'}")
    print(f"- {WALK_FORWARD_OUTPUT_DIR / '<year>' / 'final_target_weights.csv'}")


if __name__ == "__main__":
    main()
