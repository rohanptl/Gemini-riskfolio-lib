from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import yfinance as yf

import main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate as production


TRADING_DAYS = 252
DEFAULT_OUTPUT_DIR = Path("outputs_experiment_oversold_reversal_sleeve_v4_candidate")
DEFAULT_MARKET_DATA_CACHE = Path(
    "outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"
)
DEFAULT_INDICATOR_CACHE = Path(
    "outputs_experiment_market_data_cache/indicators_v1.pkl"
)
INDICATOR_CACHE_VERSION = 1


def indicator_cache_signature() -> str:
    functions = [
        rsi_wilder,
        money_flow_index,
        chaikin_money_flow,
        add_weekly_indicators,
        calculate_indicators,
    ]
    source = "\n".join(inspect.getsource(function) for function in functions)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()
DEFAULT_BASELINE_CSV = Path(
    "outputs_milestone_prod_mom126_skip21"
    "/walk_forward_windows/2020/portfolio_backtest.csv"
)


def rsi_wilder(close: pd.Series, length: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi.where(avg_loss > 0.0, 100.0)


def extract_field(raw: pd.DataFrame, field: str) -> pd.DataFrame:
    if not isinstance(raw.columns, pd.MultiIndex):
        if field not in raw.columns:
            return pd.DataFrame(index=raw.index)
        return raw[[field]].rename(columns={field: "SINGLE"})

    level_0 = raw.columns.get_level_values(0)
    level_1 = raw.columns.get_level_values(1)

    if field in level_0:
        panel = raw[field].copy()
    elif field in level_1:
        panel = raw.xs(field, axis=1, level=1).copy()
    else:
        return pd.DataFrame(index=raw.index)

    if isinstance(panel, pd.Series):
        panel = panel.to_frame()
    return panel


def download_ohlcv(
    tickers: list[str],
    start_date: str,
    end_date: str,
) -> dict[str, pd.DataFrame]:
    raw = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        # Keep OHLC on the same split/distribution-adjusted scale. Mixing an
        # adjusted close with raw highs/lows corrupts CMF/MFI around corporate
        # actions and can distort cross-sectional ranks.
        auto_adjust=True,
        progress=True,
        group_by="column",
        threads=True,
    )

    panels = {
        field: extract_field(raw, field)
        for field in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    }

    close = panels["Close"]
    close = close.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all")

    output: dict[str, pd.DataFrame] = {}
    for ticker in close.columns:
        frame = pd.DataFrame(index=close.index)
        frame["Close"] = close[ticker]
        for field in ["Open", "High", "Low", "Volume"]:
            panel = panels[field]
            frame[field] = panel[ticker] if ticker in panel.columns else np.nan
        frame = frame.replace([np.inf, -np.inf], np.nan)
        frame = frame.dropna(subset=["Close"])
        if not frame.empty:
            output[str(ticker)] = frame
    return output


def load_or_download_ohlcv(
    tickers: list[str],
    start_date: str,
    end_date: str,
    cache_file: Path,
    refresh: bool,
) -> tuple[dict[str, pd.DataFrame], str]:
    metadata_file = cache_file.with_suffix(".json")
    requested = set(tickers)
    if not refresh and cache_file.exists() and metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            cache_covers_request = (
                set(metadata.get("requested_tickers", [])) >= requested
                and metadata.get("start_date", "9999-12-31") <= start_date
                and metadata.get("end_date", "0000-01-01") >= end_date
            )
            if cache_covers_request:
                cached = pd.read_pickle(cache_file)
                cached["Date"] = pd.to_datetime(cached["Date"])
                cached = cached[
                    (cached["Date"] >= pd.Timestamp(start_date))
                    & (cached["Date"] < pd.Timestamp(end_date))
                    & cached["Ticker"].isin(requested)
                ]
                frames = {
                    str(ticker): group.drop(columns="Ticker").set_index("Date").sort_index()
                    for ticker, group in cached.groupby("Ticker", sort=False)
                }
                print(f"Loaded OHLCV cache for {len(frames)} tickers from {cache_file}.")
                return frames, "cache"
        except Exception as exc:
            print(f"Ignoring unusable OHLCV cache ({exc}).")

    frames = download_ohlcv(tickers, start_date, end_date)
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_rows = []
        for ticker, frame in frames.items():
            item = frame.reset_index().rename(columns={frame.index.name or "index": "Date"})
            item.insert(1, "Ticker", ticker)
            cache_rows.append(item)
        pd.concat(cache_rows, ignore_index=True).to_pickle(cache_file)
        metadata_file.write_text(
            json.dumps(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "requested_tickers": sorted(requested),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Saved OHLCV cache to {cache_file}.")
    except Exception as exc:
        print(f"Warning: could not save OHLCV cache ({exc}).")
    return frames, "download"


def load_or_calculate_indicators(
    ohlcv: dict[str, pd.DataFrame],
    start_date: str,
    end_date: str,
    cache_file: Path,
    refresh: bool,
) -> tuple[dict[str, pd.DataFrame], str]:
    metadata_file = cache_file.with_suffix(".json")
    requested = set(ohlcv)
    calculation_signature = indicator_cache_signature()
    if not refresh and cache_file.exists() and metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            cache_covers_request = (
                metadata.get("version") == INDICATOR_CACHE_VERSION
                and metadata.get("calculation_signature") == calculation_signature
                and set(metadata.get("tickers", [])) >= requested
                and metadata.get("start_date", "9999-12-31") <= start_date
                and metadata.get("end_date", "0000-01-01") >= end_date
            )
            if cache_covers_request:
                long_table = pd.read_pickle(cache_file)
                indicators = {
                    str(ticker): long_table.xs(ticker, level="Ticker").sort_index()
                    for ticker in requested
                    if ticker in long_table.index.get_level_values("Ticker")
                }
                print(
                    f"Loaded indicator cache for {len(indicators)} tickers "
                    f"from {cache_file}."
                )
                return indicators, "cache"
        except Exception as exc:
            print(f"Ignoring unusable indicator cache ({exc}).")

    indicators = {
        ticker: calculate_indicators(frame)
        for ticker, frame in ohlcv.items()
        if len(frame) >= 220
    }
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        build_long_indicator_table(indicators).to_pickle(cache_file)
        metadata_file.write_text(
            json.dumps(
                {
                    "version": INDICATOR_CACHE_VERSION,
                    "calculation_signature": calculation_signature,
                    "start_date": start_date,
                    "end_date": end_date,
                    "tickers": sorted(requested),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Saved indicator cache to {cache_file}.")
    except Exception as exc:
        print(f"Warning: could not save indicator cache ({exc}).")
    return indicators, "calculated"


def money_flow_index(frame: pd.DataFrame, length: int = 14) -> pd.Series:
    typical = (frame["High"] + frame["Low"] + frame["Close"]) / 3.0
    raw_flow = typical * frame["Volume"].fillna(0.0)
    direction = typical.diff()
    positive = raw_flow.where(direction > 0.0, 0.0)
    negative = raw_flow.where(direction < 0.0, 0.0)
    positive_sum = positive.rolling(length, min_periods=length).sum()
    negative_sum = negative.rolling(length, min_periods=length).sum()
    ratio = positive_sum / negative_sum.replace(0.0, np.nan)
    mfi = 100.0 - 100.0 / (1.0 + ratio)
    return mfi.where(negative_sum > 0.0, 100.0)


def chaikin_money_flow(frame: pd.DataFrame, length: int = 20) -> pd.Series:
    spread = (frame["High"] - frame["Low"]).replace(0.0, np.nan)
    multiplier = ((frame["Close"] - frame["Low"]) - (frame["High"] - frame["Close"])) / spread
    money_flow_volume = multiplier.fillna(0.0) * frame["Volume"].fillna(0.0)
    volume_sum = frame["Volume"].rolling(length, min_periods=length).sum()
    return money_flow_volume.rolling(length, min_periods=length).sum() / volume_sum.replace(0.0, np.nan)


def add_weekly_indicators(daily: pd.DataFrame) -> pd.DataFrame:
    """Attach causal week-to-date indicators to every daily row.

    A historical row must produce the same weekly features when calculated in
    the full data set or with data truncated on that row.  Building a weekly
    bar with ``groupby(...).last()`` and then joining only its final date breaks
    that property: a live mid-week run treats the partial week as complete,
    while a historical mid-week row receives the prior Friday's values.

    The calculations below carry the state of the previous completed week and
    update it with the current week-to-date OHLCV bar.  This is both causal and
    consistent with what the daily/weekly chart would show after each close.
    """
    periods = daily.index.to_period("W-FRI")
    grouped = daily.groupby(periods)
    weekly = grouped.agg(
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last"),
        Volume=("Volume", "sum"),
    )
    period_series = pd.Series(periods, index=daily.index)

    def map_previous(values: pd.Series) -> pd.Series:
        return period_series.map(values.shift(1)).astype(float)

    previous_close = map_previous(weekly["Close"])
    weekly_delta = weekly["Close"].diff()
    alpha_rsi = 1.0 / 14.0
    completed_avg_gain = weekly_delta.clip(lower=0.0).ewm(
        alpha=alpha_rsi, adjust=False, min_periods=14
    ).mean()
    completed_avg_loss = (-weekly_delta.clip(upper=0.0)).ewm(
        alpha=alpha_rsi, adjust=False, min_periods=14
    ).mean()
    current_delta = daily["Close"] - previous_close
    current_avg_gain = (
        (1.0 - alpha_rsi) * map_previous(completed_avg_gain)
        + alpha_rsi * current_delta.clip(lower=0.0)
    )
    current_avg_loss = (
        (1.0 - alpha_rsi) * map_previous(completed_avg_loss)
        + alpha_rsi * (-current_delta.clip(upper=0.0))
    )
    relative_strength = current_avg_gain / current_avg_loss.replace(0.0, np.nan)
    weekly_rsi = 100.0 - 100.0 / (1.0 + relative_strength)
    weekly_rsi = weekly_rsi.where(current_avg_loss > 0.0, 100.0)

    completed_ema12 = weekly["Close"].ewm(span=12, adjust=False).mean()
    completed_ema26 = weekly["Close"].ewm(span=26, adjust=False).mean()
    current_ema12 = (
        2.0 / 13.0 * daily["Close"]
        + 11.0 / 13.0 * map_previous(completed_ema12)
    )
    current_ema26 = (
        2.0 / 27.0 * daily["Close"]
        + 25.0 / 27.0 * map_previous(completed_ema26)
    )
    current_macd = current_ema12 - current_ema26
    completed_macd = completed_ema12 - completed_ema26
    completed_signal = completed_macd.ewm(span=9, adjust=False).mean()
    current_signal = (
        0.2 * current_macd + 0.8 * map_previous(completed_signal)
    )
    current_histogram = current_macd - current_signal
    completed_histogram = completed_macd - completed_signal

    week_high = grouped["High"].cummax()
    week_low = grouped["Low"].cummin()
    week_volume = grouped["Volume"].cumsum()
    spread = (week_high - week_low).replace(0.0, np.nan)
    multiplier = (
        (daily["Close"] - week_low) - (week_high - daily["Close"])
    ) / spread
    current_mfv = multiplier.fillna(0.0) * week_volume.fillna(0.0)
    weekly_spread = (weekly["High"] - weekly["Low"]).replace(0.0, np.nan)
    weekly_multiplier = (
        (weekly["Close"] - weekly["Low"])
        - (weekly["High"] - weekly["Close"])
    ) / weekly_spread
    completed_mfv = weekly_multiplier.fillna(0.0) * weekly["Volume"].fillna(0.0)
    previous_mfv_19 = map_previous(
        completed_mfv.rolling(19, min_periods=19).sum()
    )
    previous_volume_19 = map_previous(
        weekly["Volume"].rolling(19, min_periods=19).sum()
    )
    weekly_cmf = (previous_mfv_19 + current_mfv) / (
        previous_volume_19 + week_volume
    ).replace(0.0, np.nan)
    previous_close_39 = map_previous(
        weekly["Close"].rolling(39, min_periods=39).sum()
    )

    output = daily.copy()
    output["WeeklyRSI14"] = weekly_rsi
    output["WeeklyMACDHist"] = current_histogram
    output["WeeklyMACDHistDelta1"] = (
        current_histogram - map_previous(completed_histogram)
    )
    output["WeeklyCMF20"] = weekly_cmf
    output["WeeklySMA40"] = (previous_close_39 + daily["Close"]) / 40.0
    return output


def calculate_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.copy().sort_index()
    close = x["Close"]
    x["RSI14"] = rsi_wilder(close, 14)
    x["EMA5"] = close.ewm(span=5, adjust=False).mean()
    x["EMA10"] = close.ewm(span=10, adjust=False).mean()
    x["EMA20"] = close.ewm(span=20, adjust=False).mean()
    x["SMA50"] = close.rolling(50, min_periods=50).mean()
    x["SMA200"] = close.rolling(200, min_periods=200).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    x["MACD"] = ema12 - ema26
    x["MACDSignal"] = x["MACD"].ewm(span=9, adjust=False).mean()
    x["MACDHist"] = x["MACD"] - x["MACDSignal"]

    mid = close.rolling(20, min_periods=20).mean()
    std = close.rolling(20, min_periods=20).std()
    lower = mid - 2.0 * std
    upper = mid + 2.0 * std
    x["BBPct"] = (close - lower) / (upper - lower).replace(0.0, np.nan)
    x["Prior20High"] = close.rolling(20, min_periods=20).max().shift(1)
    x["Drawdown63"] = close / close.rolling(63, min_periods=63).max() - 1.0
    x["Return3"] = close.pct_change(3)
    x["Return5"] = close.pct_change(5)
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            x["High"] - x["Low"],
            (x["High"] - previous_close).abs(),
            (x["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    x["ATR14"] = true_range.ewm(
        alpha=1.0 / 14.0, adjust=False, min_periods=14
    ).mean()
    x["ATR14Pct"] = x["ATR14"] / close
    x["FiveDayMoveATR14"] = x["Return5"] / (
        x["ATR14Pct"] * np.sqrt(5.0)
    ).replace(0.0, np.nan)
    x["RSIRecovery3"] = x["RSI14"] - x["RSI14"].shift(3)
    x["RSIRecovery5"] = x["RSI14"] - x["RSI14"].shift(5)
    x["MACDHistDelta3"] = x["MACDHist"] - x["MACDHist"].shift(3)
    x["MACDHistDelta5"] = x["MACDHist"] - x["MACDHist"].shift(5)
    x["EMA5Slope3"] = x["EMA5"] / x["EMA5"].shift(3) - 1.0
    x["SMA200Slope20"] = x["SMA200"] / x["SMA200"].shift(20) - 1.0
    x["CMF20"] = chaikin_money_flow(x, 20)
    x["CMFDelta5"] = x["CMF20"] - x["CMF20"].shift(5)
    x["MFI14"] = money_flow_index(x, 14)
    x["DollarVolume20"] = (close * x["Volume"]).rolling(20, min_periods=20).mean()

    x["RecentRSIMin20"] = x["RSI14"].rolling(20, min_periods=20).min()
    x["RecentBBPctMin20"] = x["BBPct"].rolling(20, min_periods=20).min()
    x["SetupRSI"] = x["RecentRSIMin20"] <= 40.0
    x["SetupBand"] = x["RecentBBPctMin20"] <= 0.05
    x["SetupDrawdown"] = x["Drawdown63"] <= -0.08
    x["SetupCount"] = x[["SetupRSI", "SetupBand", "SetupDrawdown"]].sum(axis=1)

    rsi_cross_50 = (x["RSI14"] > 50.0) & (x["RSI14"].shift(1) <= 50.0)
    x["SignalStrict"] = (
        (x["RecentRSIMin20"] <= 35.0)
        & rsi_cross_50
        & (close > x["EMA20"])
        & (x["MACDHist"] > 0.0)
        & (close > x["Prior20High"])
    )

    x["SignalBalanced"] = (
        (x["SetupCount"] >= 2)
        & (x["RSI14"] >= 40.0)
        & (x["RSIRecovery5"] >= 5.0)
        & (close > x["EMA10"])
        & (x["MACDHistDelta3"] > 0.0)
        & (x["Return5"] > 0.0)
        & ((close / x["SMA200"] >= 0.85) | (x["SMA200Slope20"] > 0.0))
    )

    x["SignalEarly"] = (
        (x["SetupCount"] >= 2)
        & (x["RSI14"] >= 35.0)
        & (x["RSIRecovery3"] > 0.0)
        & (close > x["EMA5"])
        & (x["EMA5Slope3"] > 0.0)
        & (x["MACDHistDelta3"] > 0.0)
        & (x["Return3"] > 0.0)
        & ((close / x["SMA200"] >= 0.85) | (x["SMA200Slope20"] > 0.0))
    )

    # Selective washout-to-turn signal. Unlike the broader balanced setup, this
    # requires RSI to have reached a genuinely weak level before recovery.
    x["SignalWashoutTurn"] = (
        (x["RecentRSIMin20"] <= 35.0)
        & (x["SetupCount"] >= 2)
        & (x["RSI14"] >= 40.0)
        & (x["RSIRecovery5"] >= 5.0)
        & (close > x["EMA10"])
        & (x["MACDHistDelta3"] > 0.0)
        & (x["Return5"] > 0.0)
        & ((close / x["SMA200"] >= 0.85) | (x["SMA200Slope20"] > 0.0))
    )

    # The sleeve evaluates at week-end but remembers a valid daily turn from
    # any of the last five sessions. Current-state checks prevent entry after
    # the recovery has already failed by Friday.
    current_state_alive = (
        (close >= 0.98 * x["EMA10"])
        & (x["RSI14"] >= 40.0)
        & (x["MACDHist"] > 0.0)
    )
    x["SignalWashoutMemory5"] = (
        x["SignalWashoutTurn"].rolling(5, min_periods=1).max().astype(bool)
        & current_state_alive
    )
    x["SignalBalancedMemory5"] = (
        x["SignalBalanced"].rolling(5, min_periods=1).max().astype(bool)
        & current_state_alive
    )

    event_number = pd.Series(
        np.where(x["SignalWashoutTurn"], np.arange(len(x)), np.nan),
        index=x.index,
    ).ffill()
    x["WashoutWatchAge"] = np.arange(len(x)) - event_number
    x["WashoutWatchActive30"] = x["WashoutWatchAge"].between(
        1.0, 30.0, inclusive="both"
    )

    x = add_weekly_indicators(x)

    # A weekly turn is confirmation, not a demand that the reversal already be
    # complete. This deliberately allows a still-negative weekly MACD as long
    # as its histogram is improving, which is how GLD/GLDM looked on 2026-07-24.
    weekly_turn = (
        x["WeeklyRSI14"].between(35.0, 60.0, inclusive="both")
        & (x["WeeklyMACDHistDelta1"] > 0.0)
    )
    x["SignalWashoutWeeklyMemory5"] = x["SignalWashoutMemory5"] & weekly_turn

    # Small, earlier probe after a deep washout. This reuses the existing
    # daily turn signal but limits it to three-of-three washout setups, a
    # non-overbought recovery, a still-depressed weekly RSI, and an
    # ATR-normalized move that has not become extended.
    x["SignalEarlyProbeATR125"] = (
        x["SignalEarly"]
        & (x["SetupCount"] >= 3)
        & x["RSI14"].between(40.0, 60.0, inclusive="both")
        & x["WeeklyRSI14"].between(35.0, 52.0, inclusive="both")
        & (x["FiveDayMoveATR14"] <= 1.25)
    )

    # Stage two: confirm a watched washout only after price and momentum turn.
    # The 30-session state preserves GLD's July washout after its 20-day RSI
    # minimum aged out, allowing the 2026-08-05 breakout to qualify.
    x["SignalTwoStageConfirm"] = (
        x["WashoutWatchActive30"]
        & rsi_cross_50
        & x["RSI14"].between(50.0, 68.0, inclusive="both")
        & (close > x["EMA20"])
        & (x["MACDHist"] > 0.0)
        & (close > x["Prior20High"])
        & x["WeeklyRSI14"].between(35.0, 65.0, inclusive="both")
        & (x["WeeklyMACDHistDelta1"] > 0.0)
    )
    quality_state_common = (
        x["RSI14"].between(55.0, 64.0, inclusive="both")
        & (x["Return5"] >= 0.0)
        & x["WeeklyRSI14"].between(35.0, 52.0, inclusive="both")
    )
    quality_state = quality_state_common & (x["Return5"] <= 0.06)
    x["SignalTwoStageQuality10"] = (
        x["SignalTwoStageConfirm"]
        & x["WashoutWatchAge"].between(1.0, 10.0, inclusive="both")
        & quality_state
    )
    x["SignalTwoStageQuality5To10"] = (
        x["SignalTwoStageConfirm"]
        & x["WashoutWatchAge"].between(5.0, 10.0, inclusive="both")
        & quality_state
    )
    x["SignalTwoStageQuality10Cap8"] = (
        x["SignalTwoStageConfirm"]
        & x["WashoutWatchAge"].between(1.0, 10.0, inclusive="both")
        & quality_state_common
        & (x["Return5"] <= 0.08)
    )
    x["SignalTwoStageQuality10Cap10"] = (
        x["SignalTwoStageConfirm"]
        & x["WashoutWatchAge"].between(1.0, 10.0, inclusive="both")
        & quality_state_common
        & (x["Return5"] <= 0.10)
    )
    x["SignalTwoStageQuality10NoCap"] = (
        x["SignalTwoStageConfirm"]
        & x["WashoutWatchAge"].between(1.0, 10.0, inclusive="both")
        & quality_state_common
    )
    for atr_limit, suffix in [(1.0, "100"), (1.25, "125"), (1.5, "150"), (2.0, "200")]:
        x[f"SignalTwoStageQuality10ATR{suffix}"] = (
            x["SignalTwoStageConfirm"]
            & x["WashoutWatchAge"].between(1.0, 10.0, inclusive="both")
            & quality_state_common
            & (x["FiveDayMoveATR14"] <= atr_limit)
        )

    return x


def last_trading_day_each_week(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    s = pd.Series(index, index=index)
    return pd.DatetimeIndex(s.groupby(index.to_period("W-FRI")).max().values)


def cross_sectional_rank(snapshot: pd.DataFrame) -> pd.Series:
    components = pd.DataFrame(index=snapshot.index)
    components["RSIRecovery"] = snapshot["RSIRecovery5"].rank(pct=True)
    components["MACDAcceleration"] = (
        snapshot["MACDHistDelta3"] / snapshot["Close"]
    ).rank(pct=True)
    components["Return5"] = snapshot["Return5"].rank(pct=True)
    components["CMFImprovement"] = snapshot["CMFDelta5"].rank(pct=True)
    components["NotOverbought"] = (-snapshot["RSI14"].clip(lower=0.0)).rank(pct=True)
    return components.mean(axis=1)


def build_long_indicator_table(indicators: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ticker, frame in indicators.items():
        item = frame.copy()
        item["Ticker"] = ticker
        item.index.name = "Date"
        rows.append(item.reset_index())
    return pd.concat(rows, ignore_index=True).set_index(["Date", "Ticker"]).sort_index()


def backtest_variant(
    variant: str,
    signal_column: str,
    indicators: dict[str, pd.DataFrame],
    baseline_returns: pd.Series,
    candidate_tickers: list[str],
    max_holdings: int,
    weight_per_holding: float,
    max_holding_weeks: int,
    cost_bps: float,
    prebuilt_long_table: pd.DataFrame | None = None,
    precomputed_asset_returns: pd.DataFrame | None = None,
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    long_table = prebuilt_long_table
    if long_table is None:
        long_table = build_long_indicator_table(
            {t: indicators[t] for t in candidate_tickers if t in indicators}
        )
    common_dates = pd.DatetimeIndex(
        sorted(set(baseline_returns.index) & set(long_table.index.get_level_values("Date")))
    )
    weekly_dates = last_trading_day_each_week(common_dates)

    positions: dict[str, int] = {}
    target_rows: list[pd.Series] = []
    log_rows: list[dict] = []
    eligibility_rows: list[dict] = []

    for date in weekly_dates:
        try:
            snapshot = long_table.xs(date, level="Date").copy()
        except KeyError:
            continue

        exits: list[str] = []
        for ticker in list(positions):
            if ticker not in snapshot.index:
                exits.append(ticker)
                continue
            row = snapshot.loc[ticker]
            confirmation_failed = (
                row["Close"] < row["EMA20"]
                and row["RSI14"] < 40.0
                and row["MACDHist"] < 0.0
            )
            # A renewed valid setup extends the opportunity window. Without
            # this refresh, GLDM's 2026-07-24 confirmation was ignored because
            # an earlier July entry hit its time limit one week later.
            if bool(row.get(signal_column, False)):
                positions[ticker] = 0
            else:
                positions[ticker] += 1
            exit_signal = confirmation_failed or positions[ticker] >= max_holding_weeks
            if exit_signal:
                exits.append(ticker)

        for ticker in exits:
            positions.pop(ticker, None)

        eligible = snapshot[
            snapshot[signal_column].fillna(False)
            & (snapshot["DollarVolume20"] >= 10_000_000)
            & (snapshot["RSI14"] <= 70.0)
        ].copy()
        eligible = eligible.loc[~eligible.index.isin(positions)]
        eligible["ReversalRank"] = cross_sectional_rank(eligible) if not eligible.empty else np.nan
        entrants = (
            eligible.sort_values("ReversalRank", ascending=False)
            .head(max(0, max_holdings - len(positions)))
            .index.tolist()
        )
        for ticker, row in eligible.iterrows():
            eligibility_rows.append(
                {
                    "Date": date,
                    "Variant": variant,
                    "Ticker": ticker,
                    "Selected": ticker in entrants,
                    "ReversalRank": row["ReversalRank"],
                    "RSI14": row["RSI14"],
                    "RecentRSIMin20": row["RecentRSIMin20"],
                    "WeeklyRSI14": row["WeeklyRSI14"],
                    "WeeklyMACDHistDelta1": row["WeeklyMACDHistDelta1"],
                }
            )
        for ticker in entrants:
            positions[ticker] = 0

        target = pd.Series(0.0, index=candidate_tickers, name=date)
        for ticker in positions:
            if ticker in target.index:
                target[ticker] = weight_per_holding
        target_rows.append(target)

        for ticker in sorted(set(positions) | set(exits)):
            row = snapshot.loc[ticker] if ticker in snapshot.index else pd.Series(dtype=float)
            log_rows.append(
                {
                    "Date": date,
                    "Variant": variant,
                    "Ticker": ticker,
                    "Action": "Exit" if ticker in exits else ("Enter" if ticker in entrants else "Hold"),
                    "TargetWeight": target.get(ticker, 0.0),
                    "RSI14": row.get("RSI14", np.nan),
                    "RecentRSIMin20": row.get("RecentRSIMin20", np.nan),
                    "SetupCount": row.get("SetupCount", np.nan),
                    "Return5": row.get("Return5", np.nan),
                    "MACDHist": row.get("MACDHist", np.nan),
                    "MACDHistDelta3": row.get("MACDHistDelta3", np.nan),
                    "CMF20": row.get("CMF20", np.nan),
                    "WeeklyRSI14": row.get("WeeklyRSI14", np.nan),
                    "WeeklyMACDHistDelta1": row.get("WeeklyMACDHistDelta1", np.nan),
                }
            )

    if not target_rows:
        return (
            baseline_returns.copy(),
            pd.DataFrame(),
            pd.DataFrame(log_rows),
            pd.DataFrame(eligibility_rows),
        )

    weekly_targets = pd.DataFrame(target_rows).sort_index()
    daily_targets = weekly_targets.reindex(baseline_returns.index).ffill().shift(1).fillna(0.0)
    sleeve_total = daily_targets.sum(axis=1).clip(upper=max_holdings * weight_per_holding)

    asset_returns = precomputed_asset_returns
    if asset_returns is None:
        asset_returns = pd.DataFrame(
            {
                ticker: indicators[ticker]["Close"].pct_change()
                for ticker in daily_targets.columns
                if ticker in indicators
            }
        )
    asset_returns = asset_returns.reindex(baseline_returns.index).fillna(0.0)
    sleeve_return = (daily_targets * asset_returns.reindex(columns=daily_targets.columns).fillna(0.0)).sum(axis=1)
    combined = (1.0 - sleeve_total) * baseline_returns + sleeve_return

    base_weight = 1.0 - sleeve_total
    sleeve_delta = daily_targets.diff().abs().sum(axis=1).fillna(0.0)
    base_delta = base_weight.diff().abs().fillna(0.0)
    turnover = 0.5 * (sleeve_delta + base_delta)
    combined_net = combined - turnover * cost_bps / 10_000.0

    daily_output = pd.DataFrame(
        {
            "BaselineReturn": baseline_returns,
            "SleeveWeight": sleeve_total,
            "GrossCombinedReturn": combined,
            "Turnover": turnover,
            "NetCombinedReturn": combined_net,
        }
    )
    return (
        combined_net,
        daily_output,
        pd.DataFrame(log_rows),
        pd.DataFrame(eligibility_rows),
    )


def trailing_correlation(
    left: str,
    right: str,
    date: pd.Timestamp,
    indicators: dict[str, pd.DataFrame],
    lookback: int = 63,
    return_history: pd.DataFrame | None = None,
) -> float:
    if return_history is not None:
        pair = return_history.loc[:date, [left, right]].dropna().tail(lookback)
        pair = pair.rename(columns={left: "Left", right: "Right"})
    else:
        pair = pd.concat(
            [
                indicators[left]["Close"].pct_change().loc[:date].rename("Left"),
                indicators[right]["Close"].pct_change().loc[:date].rename("Right"),
            ],
            axis=1,
            sort=False,
        ).dropna().tail(lookback)
    if len(pair) < 30:
        return np.nan
    return float(pair["Left"].corr(pair["Right"]))


def backtest_daily_confirmation_variant(
    variant: str,
    indicators: dict[str, pd.DataFrame],
    baseline_returns: pd.Series,
    candidate_tickers: list[str],
    max_holdings: int,
    weight_per_holding: float,
    max_holding_days: int,
    cost_bps: float,
    rank_ascending: bool,
    max_pair_correlation: float,
    replacement_policy: str = "none",
    min_replacement_days: int = 10,
    signal_column: str = "SignalTwoStageConfirm",
    probe_signal_column: str | None = None,
    probe_weight_per_holding: float | None = None,
    profit_stop_activation: float | None = None,
    atr_trailing_multiple: float | None = None,
    atr_stop_floor_at_entry: bool = True,
    entry_event_whitelist: dict[pd.Timestamp, set[str]] | None = None,
    prebuilt_long_table: pd.DataFrame | None = None,
    precomputed_asset_returns: pd.DataFrame | None = None,
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    long_table = prebuilt_long_table
    if long_table is None:
        long_table = build_long_indicator_table(
            {t: indicators[t] for t in candidate_tickers if t in indicators}
        )
    common_dates = pd.DatetimeIndex(
        sorted(set(baseline_returns.index) & set(long_table.index.get_level_values("Date")))
    )
    positions: dict[str, int] = {}
    position_weights: dict[str, float] = {}
    position_entry_closes: dict[str, float] = {}
    position_peak_prices: dict[str, float] = {}
    target_rows: list[pd.Series] = []
    log_rows: list[dict] = []
    eligibility_rows: list[dict] = []

    for date in common_dates:
        snapshot = long_table.xs(date, level="Date").copy()
        exits: list[str] = []
        exit_reasons: dict[str, str] = {}
        stop_levels: dict[str, float] = {}
        peak_gains: dict[str, float] = {}
        stop_active: dict[str, bool] = {}
        for ticker in list(positions):
            if ticker not in snapshot.index:
                exits.append(ticker)
                exit_reasons[ticker] = "MissingData"
                continue
            row = snapshot.loc[ticker]
            positions[ticker] += 1
            position_peak_prices[ticker] = max(
                position_peak_prices[ticker], float(row["High"])
            )
            entry_close = position_entry_closes[ticker]
            peak_price = position_peak_prices[ticker]
            peak_gain = peak_price / entry_close - 1.0
            peak_gains[ticker] = peak_gain
            stop_is_active = (
                profit_stop_activation is not None
                and atr_trailing_multiple is not None
                and peak_gain >= profit_stop_activation
            )
            stop_active[ticker] = stop_is_active
            stop_level = np.nan
            atr_stop_failed = False
            if stop_is_active:
                stop_level = peak_price - atr_trailing_multiple * float(row["ATR14"])
                if atr_stop_floor_at_entry:
                    stop_level = max(entry_close, stop_level)
                atr_stop_failed = float(row["Close"]) < stop_level
            stop_levels[ticker] = stop_level
            confirmation_failed = (
                row["Close"] < row["EMA20"]
                and row["RSI14"] < 40.0
                and row["MACDHist"] < 0.0
            )
            max_holding_reached = positions[ticker] >= max_holding_days
            if confirmation_failed or atr_stop_failed or max_holding_reached:
                exits.append(ticker)
                exit_reasons[ticker] = (
                    "ConfirmationFailure" if confirmation_failed else (
                        "ATRProfitStop" if atr_stop_failed else "MaxHoldingDays"
                    )
                )
        for ticker in exits:
            positions.pop(ticker, None)
            position_weights.pop(ticker, None)
            position_entry_closes.pop(ticker, None)
            position_peak_prices.pop(ticker, None)

        additions: list[str] = []
        if probe_signal_column is not None:
            for ticker in positions:
                if (
                    bool(snapshot.loc[ticker, signal_column])
                    and position_weights[ticker] < weight_per_holding
                ):
                    position_weights[ticker] = weight_per_holding
                    additions.append(ticker)

        entry_signal = snapshot[signal_column].fillna(False)
        if probe_signal_column is not None:
            entry_signal = (
                entry_signal | snapshot[probe_signal_column].fillna(False)
            )
        eligible = snapshot[
            entry_signal & (snapshot["DollarVolume20"] >= 10_000_000)
        ].copy()
        if entry_event_whitelist is not None:
            eligible = eligible.loc[
                eligible.index.isin(entry_event_whitelist.get(date, set()))
            ]
        eligible = eligible.loc[~eligible.index.isin(positions)]
        eligible["ReversalRank"] = (
            cross_sectional_rank(eligible) if not eligible.empty else np.nan
        )
        ordered = eligible.sort_values(
            "ReversalRank", ascending=rank_ascending
        ).index.tolist()

        entrants: list[str] = []
        for ticker in ordered:
            replace_ticker: str | None = None
            if len(positions) + len(entrants) >= max_holdings:
                replaceable = [
                    held for held, age in positions.items()
                    if age >= min_replacement_days
                ]
                if replacement_policy == "oldest" and replaceable:
                    replace_ticker = max(replaceable, key=lambda held: positions[held])
                elif replacement_policy == "weakest" and replaceable:
                    def holding_strength(held: str) -> float:
                        held_row = snapshot.loc[held]
                        return float(
                            held_row["Return5"]
                            + (held_row["Close"] / held_row["EMA20"] - 1.0)
                            + 5.0 * held_row["MACDHist"] / held_row["Close"]
                        )

                    replace_ticker = min(replaceable, key=holding_strength)
                else:
                    continue

            references = [
                held for held in positions if held != replace_ticker
            ] + entrants
            correlations = [
                trailing_correlation(
                    ticker, other, date, indicators,
                    return_history=precomputed_asset_returns,
                )
                for other in references
            ]
            if all(
                not np.isfinite(value) or value <= max_pair_correlation
                for value in correlations
            ):
                if replace_ticker is not None:
                    positions.pop(replace_ticker, None)
                    position_weights.pop(replace_ticker, None)
                    position_entry_closes.pop(replace_ticker, None)
                    position_peak_prices.pop(replace_ticker, None)
                    exits.append(replace_ticker)
                    exit_reasons[replace_ticker] = "Replacement"
                entrants.append(ticker)

        for ticker, row in eligible.iterrows():
            correlations = [
                trailing_correlation(
                    ticker, other, date, indicators,
                    return_history=precomputed_asset_returns,
                )
                for other in list(positions) + entrants
                if other != ticker
            ]
            finite_correlations = [
                value for value in correlations if np.isfinite(value)
            ]
            eligibility_rows.append(
                {
                    "Date": date,
                    "Variant": variant,
                    "Ticker": ticker,
                    "Selected": ticker in entrants,
                    "EntrySignalType": (
                        "Confirmed" if bool(row[signal_column]) else "EarlyProbe"
                    ),
                    "ReversalRank": row["ReversalRank"],
                    "MaxCorrelationToBook": (
                        max(finite_correlations) if finite_correlations else np.nan
                    ),
                    "RSI14": row["RSI14"],
                    "RecentRSIMin20": row["RecentRSIMin20"],
                    "WashoutWatchAge": row["WashoutWatchAge"],
                    "Return5": row["Return5"],
                    "ATR14Pct": row["ATR14Pct"],
                    "FiveDayMoveATR14": row["FiveDayMoveATR14"],
                    "WeeklyRSI14": row["WeeklyRSI14"],
                    "WeeklyMACDHistDelta1": row["WeeklyMACDHistDelta1"],
                }
            )
        for ticker in entrants:
            positions[ticker] = 0
            is_confirmed = bool(snapshot.loc[ticker, signal_column])
            position_weights[ticker] = (
                weight_per_holding
                if is_confirmed or probe_weight_per_holding is None
                else probe_weight_per_holding
            )
            entry_close = float(snapshot.loc[ticker, "Close"])
            position_entry_closes[ticker] = entry_close
            position_peak_prices[ticker] = entry_close
            peak_gains[ticker] = 0.0
            stop_active[ticker] = False
            stop_levels[ticker] = np.nan

        target = pd.Series(0.0, index=candidate_tickers, name=date)
        for ticker in positions:
            target[ticker] = position_weights[ticker]
        target_rows.append(target)

        for ticker in sorted(set(positions) | set(exits)):
            row = snapshot.loc[ticker] if ticker in snapshot.index else pd.Series(dtype=float)
            log_rows.append(
                {
                    "Date": date,
                    "Variant": variant,
                    "Ticker": ticker,
                    "Action": "Exit" if ticker in exits else (
                        "Enter" if ticker in entrants else (
                            "Add" if ticker in additions else "Hold"
                        )
                    ),
                    "TargetWeight": target.get(ticker, 0.0),
                    "HoldingDays": positions.get(ticker, np.nan),
                    "ExitReason": exit_reasons.get(ticker, ""),
                    "PeakGain": peak_gains.get(ticker, np.nan),
                    "ATRStopActive": stop_active.get(ticker, False),
                    "ATRStopLevel": stop_levels.get(ticker, np.nan),
                    "RSI14": row.get("RSI14", np.nan),
                    "WashoutWatchAge": row.get("WashoutWatchAge", np.nan),
                    "Return5": row.get("Return5", np.nan),
                    "ATR14Pct": row.get("ATR14Pct", np.nan),
                    "FiveDayMoveATR14": row.get("FiveDayMoveATR14", np.nan),
                    "WeeklyRSI14": row.get("WeeklyRSI14", np.nan),
                    "WeeklyMACDHistDelta1": row.get("WeeklyMACDHistDelta1", np.nan),
                }
            )

    weekly_targets = pd.DataFrame(target_rows).sort_index()
    daily_targets = weekly_targets.reindex(baseline_returns.index).ffill().shift(1).fillna(0.0)
    sleeve_total = daily_targets.sum(axis=1).clip(upper=max_holdings * weight_per_holding)
    asset_returns = precomputed_asset_returns
    if asset_returns is None:
        asset_returns = pd.DataFrame(
            {
                ticker: indicators[ticker]["Close"].pct_change()
                for ticker in daily_targets.columns
                if ticker in indicators
            }
        )
    asset_returns = asset_returns.reindex(baseline_returns.index).fillna(0.0)
    sleeve_return = (
        daily_targets
        * asset_returns.reindex(columns=daily_targets.columns).fillna(0.0)
    ).sum(axis=1)
    combined = (1.0 - sleeve_total) * baseline_returns + sleeve_return
    base_weight = 1.0 - sleeve_total
    sleeve_delta = daily_targets.diff().abs().sum(axis=1).fillna(0.0)
    base_delta = base_weight.diff().abs().fillna(0.0)
    turnover = 0.5 * (sleeve_delta + base_delta)
    combined_net = combined - turnover * cost_bps / 10_000.0
    daily_output = pd.DataFrame(
        {
            "BaselineReturn": baseline_returns,
            "SleeveWeight": sleeve_total,
            "GrossCombinedReturn": combined,
            "Turnover": turnover,
            "NetCombinedReturn": combined_net,
        }
    )
    return (
        combined_net,
        daily_output,
        pd.DataFrame(log_rows),
        pd.DataFrame(eligibility_rows),
    )


def annual_return_table(return_map: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for name, series in return_map.items():
        for year, values in series.dropna().groupby(series.dropna().index.year):
            rows.append(
                {
                    "Name": name,
                    "Year": int(year),
                    "Return": (1.0 + values).prod() - 1.0,
                }
            )
    return pd.DataFrame(rows)


def add_forward_event_returns(
    events: pd.DataFrame,
    indicators: dict[str, pd.DataFrame],
    baseline_returns: pd.Series,
) -> pd.DataFrame:
    """Attach next-session-open forward returns to weekly entry candidates."""
    if events.empty:
        return events.copy()

    output = events.copy()
    metrics: list[dict[str, float]] = []
    for event in output.itertuples(index=False):
        frame = indicators.get(event.Ticker)
        values: dict[str, float] = {
            "EntryOpen": np.nan,
            "ForwardReturn1W": np.nan,
            "ForwardReturn2W": np.nan,
            "ForwardReturn4W": np.nan,
            "ForwardReturn8W": np.nan,
            "MFE4W": np.nan,
            "MAE4W": np.nan,
        }
        if frame is None:
            metrics.append(values)
            continue

        date = pd.Timestamp(event.Date)
        location = frame.index.get_indexer([date])[0]
        if location < 0 or location + 1 >= len(frame):
            metrics.append(values)
            continue

        entry_open = float(frame["Open"].iloc[location + 1])
        if not np.isfinite(entry_open) or entry_open <= 0.0:
            metrics.append(values)
            continue
        values["EntryOpen"] = entry_open

        for sessions, suffix in [
            (5, "1W"),
            (10, "2W"),
            (20, "4W"),
            (40, "8W"),
        ]:
            exit_location = location + sessions
            if exit_location < len(frame):
                values[f"ForwardReturn{suffix}"] = (
                    float(frame["Close"].iloc[exit_location]) / entry_open - 1.0
                )
            baseline_window = baseline_returns[baseline_returns.index > date].iloc[:sessions]
            if len(baseline_window) == sessions:
                baseline_return = float((1.0 + baseline_window).prod() - 1.0)
                values[f"ProductionReturn{suffix}"] = baseline_return
                if np.isfinite(values.get(f"ForwardReturn{suffix}", np.nan)):
                    values[f"RelativeAlpha{suffix}"] = (
                        values[f"ForwardReturn{suffix}"] - baseline_return
                    )

        end_location = min(location + 20, len(frame) - 1)
        path = frame.iloc[location + 1:end_location + 1]
        if not path.empty:
            values["MFE4W"] = float(path["High"].max()) / entry_open - 1.0
            values["MAE4W"] = float(path["Low"].min()) / entry_open - 1.0
        metrics.append(values)

    return pd.concat(
        [output.reset_index(drop=True), pd.DataFrame(metrics)], axis=1
    )


def summarize_event_study(events: pd.DataFrame, variant: str) -> pd.DataFrame:
    rows: list[dict] = []
    scopes = {
        "AllEligible": events,
        "SelectedEntries": events[events["Selected"].fillna(False).astype(bool)],
    }
    for scope, frame in scopes.items():
        for suffix in ["1W", "2W", "4W", "8W"]:
            asset = frame[f"ForwardReturn{suffix}"].dropna()
            alpha = frame[f"RelativeAlpha{suffix}"].dropna()
            rows.append(
                {
                    "Variant": variant,
                    "Scope": scope,
                    "Horizon": suffix,
                    "Observations": len(alpha),
                    "MeanForwardReturn": asset.mean(),
                    "MedianForwardReturn": asset.median(),
                    "AbsoluteWinRate": (asset > 0.0).mean(),
                    "MeanRelativeAlpha": alpha.mean(),
                    "MedianRelativeAlpha": alpha.median(),
                    "BeatProductionRate": (alpha > 0.0).mean(),
                }
            )
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test a standalone oversold-reversal ETF sleeve.")
    parser.add_argument("--start-date", default="2019-01-01")
    parser.add_argument("--end-date", default="2026-08-09")
    parser.add_argument("--baseline-csv", type=Path, default=DEFAULT_BASELINE_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--max-holdings", type=int, default=2)
    parser.add_argument("--weight-per-holding", type=float, default=0.05)
    parser.add_argument("--max-holding-weeks", type=int, default=8)
    parser.add_argument(
        "--market-data-cache", type=Path, default=DEFAULT_MARKET_DATA_CACHE
    )
    parser.add_argument(
        "--indicator-cache", type=Path, default=DEFAULT_INDICATOR_CACHE
    )
    parser.add_argument(
        "--refresh-data", action="store_true",
        help="Ignore the local OHLCV cache and download fresh market data.",
    )
    parser.add_argument(
        "--variant-suite", choices=["candidate", "atr", "entry", "exit", "full"], default="candidate",
        help=(
            "Run only the ATR-1.25 candidate (default), the focused ATR comparison, "
            "the early-entry probe comparison, the ATR profit-stop comparison, "
            "or every historical variant."
        ),
    )
    return parser.parse_args()


def main() -> None:
    run_started = perf_counter()
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not args.baseline_csv.exists():
        raise FileNotFoundError(
            f"Baseline file not found: {args.baseline_csv}. Run the production strategy first."
        )

    risk_tickers = production.load_tickers(production.CSV_FILE)
    risk_tickers = [
        ticker for ticker in risk_tickers
        if ticker not in production.CASH_EQUIVALENT_TICKERS
    ]
    diagnostic_tickers = ["GLD", "GLDM", "SLV"]
    download_tickers = sorted(set(risk_tickers + diagnostic_tickers))

    print(f"Loading OHLCV for {len(download_tickers)} tickers...")
    data_started = perf_counter()
    ohlcv, data_source = load_or_download_ohlcv(
        download_tickers,
        args.start_date,
        args.end_date,
        args.market_data_cache,
        args.refresh_data,
    )
    print(f"OHLCV {data_source} step completed in {perf_counter() - data_started:.1f}s.")
    indicator_started = perf_counter()
    indicators, indicator_source = load_or_calculate_indicators(
        ohlcv,
        args.start_date,
        args.end_date,
        args.indicator_cache,
        args.refresh_data,
    )
    print(
        f"Indicator {indicator_source} step for {len(indicators)} tickers completed in "
        f"{perf_counter() - indicator_started:.1f}s."
    )

    diagnostic_columns = [
        "Close", "RSI14", "RecentRSIMin20", "EMA5", "EMA10", "EMA20",
        "SMA50", "SMA200", "BBPct", "Drawdown63", "Return3", "Return5",
        "ATR14", "ATR14Pct", "FiveDayMoveATR14",
        "Prior20High", "WashoutWatchAge", "WashoutWatchActive30",
        "MACDHist", "MACDHistDelta3", "CMF20", "CMFDelta5", "MFI14",
        "SetupCount", "SignalStrict", "SignalBalanced", "SignalEarly",
        "SignalWashoutTurn", "SignalWashoutMemory5", "SignalBalancedMemory5",
        "SignalWashoutWeeklyMemory5",
        "SignalEarlyProbeATR125",
        "SignalTwoStageConfirm",
        "SignalTwoStageQuality10", "SignalTwoStageQuality5To10",
        "SignalTwoStageQuality10Cap8", "SignalTwoStageQuality10Cap10",
        "SignalTwoStageQuality10NoCap",
        "SignalTwoStageQuality10ATR100", "SignalTwoStageQuality10ATR125",
        "SignalTwoStageQuality10ATR150", "SignalTwoStageQuality10ATR200",
        "WeeklyRSI14", "WeeklyMACDHist", "WeeklyMACDHistDelta1", "WeeklyCMF20",
    ]
    diagnostic_rows = []
    for ticker in diagnostic_tickers:
        if ticker not in indicators:
            continue
        window = indicators[ticker].loc["2026-07-20":"2026-08-07", diagnostic_columns].copy()
        window.insert(0, "Ticker", ticker)
        diagnostic_rows.append(window.reset_index())
    diagnostics = pd.concat(diagnostic_rows, ignore_index=True)
    diagnostics.to_csv(args.output_dir / "gld_slv_late_july_diagnostics.csv", index=False)

    baseline_frame = pd.read_csv(args.baseline_csv, parse_dates=["Date"]).set_index("Date")
    baseline_returns = baseline_frame["DailyReturn"].astype(float).sort_index()

    broad_tickers = [ticker for ticker in risk_tickers if ticker in indicators]
    categorization = pd.read_csv(production.CSV_FILE)
    excluded_asset_classes = {"Fixed Income & Cash", "Cryptocurrency"}
    risk_asset_set = set(
        categorization.loc[
            ~categorization["Asset_Class"].isin(excluded_asset_classes), "Ticker"
        ].astype(str)
    )
    risk_asset_tickers = [ticker for ticker in broad_tickers if ticker in risk_asset_set]
    variants = {
        "StrictBroad": {
            "signal": "SignalStrict", "tickers": broad_tickers, "max_weeks": 8,
        },
    }
    daily_variants = {
        "TwoStageCurrentRank40D": {
            "max_days": 40, "rank_ascending": False, "max_correlation": 1.0,
        },
        "TwoStageAntiChase40D": {
            "max_days": 40, "rank_ascending": True, "max_correlation": 1.0,
        },
        "TwoStageAntiChaseDiversified40D": {
            "max_days": 40, "rank_ascending": True, "max_correlation": 0.80,
        },
        "TwoStageAntiChaseDiversified20D": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
        },
        "TwoStageReplaceOldest40D": {
            "max_days": 40, "rank_ascending": True, "max_correlation": 0.80,
            "replacement_policy": "oldest", "min_replacement_days": 10,
        },
        "TwoStageReplaceWeakest40D": {
            "max_days": 40, "rank_ascending": True, "max_correlation": 0.80,
            "replacement_policy": "weakest", "min_replacement_days": 10,
        },
        "TwoStageQuality10Risk20D": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DCap8": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10Cap8", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DCap10": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10Cap10", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DNoCap": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10NoCap", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DATR100": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR100", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DATR125": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
        },
        "TwoStageEarlyProbeRisk20DATR125": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "probe_signal": "SignalEarlyProbeATR125", "probe_weight": 0.025,
        },
        "TwoStageATR125Profit3Trail15": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 1.5,
        },
        "TwoStageATR125Profit3Trail20": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 2.0,
        },
        "TwoStageATR125Profit3Trail25": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 2.5,
        },
        "TwoStageATR125Profit3Trail275": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 2.75,
        },
        "TwoStageATR125Profit3Trail30": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 3.0,
        },
        "TwoStageATR125Profit3Trail25NoFloor": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 2.5,
            "atr_stop_floor_at_entry": False,
        },
        "TwoStageATR125Profit3Trail30NoFloor": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.03, "atr_trailing_multiple": 3.0,
            "atr_stop_floor_at_entry": False,
        },
        "TwoStageATR125Profit4Trail25": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.04, "atr_trailing_multiple": 2.5,
        },
        "TwoStageATR125Profit5Trail15": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.05, "atr_trailing_multiple": 1.5,
        },
        "TwoStageATR125Profit5Trail20": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.05, "atr_trailing_multiple": 2.0,
        },
        "TwoStageATR125Profit5Trail25": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR125", "tickers": risk_asset_tickers,
            "profit_stop_activation": 0.05, "atr_trailing_multiple": 2.5,
        },
        "TwoStageQuality10Risk20DATR150": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR150", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality10Risk20DATR200": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality10ATR200", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality5To10Risk20D": {
            "max_days": 20, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality5To10", "tickers": risk_asset_tickers,
        },
        "TwoStageQuality5To10Risk40D": {
            "max_days": 40, "rank_ascending": True, "max_correlation": 0.80,
            "signal": "SignalTwoStageQuality5To10", "tickers": risk_asset_tickers,
        },
    }
    for name, config in daily_variants.items():
        if name.startswith("TwoStageATR125Profit"):
            config["freeze_control_entries"] = True
    if args.variant_suite == "candidate":
        variants = {}
        daily_variants = {
            "TwoStageQuality10Risk20DATR125": daily_variants[
                "TwoStageQuality10Risk20DATR125"
            ]
        }
    elif args.variant_suite == "atr":
        variants = {}
        focused_names = {
            "TwoStageQuality10Risk20D",
            "TwoStageQuality10Risk20DCap8",
            "TwoStageQuality10Risk20DATR100",
            "TwoStageQuality10Risk20DATR125",
            "TwoStageQuality10Risk20DATR150",
            "TwoStageQuality10Risk20DATR200",
        }
        daily_variants = {
            name: config for name, config in daily_variants.items()
            if name in focused_names
        }
    elif args.variant_suite == "entry":
        variants = {}
        focused_names = {
            "TwoStageQuality10Risk20DATR125",
            "TwoStageEarlyProbeRisk20DATR125",
        }
        daily_variants = {
            name: config for name, config in daily_variants.items()
            if name in focused_names
        }
    elif args.variant_suite == "exit":
        variants = {}
        focused_names = {
            "TwoStageQuality10Risk20DATR125",
            "TwoStageATR125Profit3Trail15",
            "TwoStageATR125Profit3Trail20",
            "TwoStageATR125Profit3Trail25",
            "TwoStageATR125Profit3Trail275",
            "TwoStageATR125Profit3Trail30",
            "TwoStageATR125Profit3Trail25NoFloor",
            "TwoStageATR125Profit3Trail30NoFloor",
            "TwoStageATR125Profit4Trail25",
            "TwoStageATR125Profit5Trail15",
            "TwoStageATR125Profit5Trail20",
            "TwoStageATR125Profit5Trail25",
        }
        daily_variants = {
            name: config for name, config in daily_variants.items()
            if name in focused_names
        }

    table_started = perf_counter()
    broad_long_table = build_long_indicator_table(
        {ticker: indicators[ticker] for ticker in broad_tickers}
    )
    risk_mask = broad_long_table.index.get_level_values("Ticker").isin(
        risk_asset_tickers
    )
    risk_long_table = broad_long_table.loc[risk_mask]
    all_asset_returns = pd.DataFrame(
        {
            ticker: frame["Close"].pct_change()
            for ticker, frame in indicators.items()
        }
    ).sort_index()
    print(f"Built shared backtest tables in {perf_counter() - table_started:.1f}s.")
    return_map: dict[str, pd.Series] = {"ProductionBaseline": baseline_returns}
    summary_rows = [production.performance_stats(baseline_returns, "ProductionBaseline")]
    event_summary_rows: list[pd.DataFrame] = []

    for variant, config in variants.items():
        returns, daily_output, signal_log, eligibility_log = backtest_variant(
            variant=variant,
            signal_column=config["signal"],
            indicators=indicators,
            baseline_returns=baseline_returns,
            candidate_tickers=config["tickers"],
            max_holdings=args.max_holdings,
            weight_per_holding=args.weight_per_holding,
            max_holding_weeks=config["max_weeks"],
            cost_bps=args.cost_bps,
            prebuilt_long_table=broad_long_table,
            precomputed_asset_returns=all_asset_returns,
        )
        return_map[variant] = returns
        stats = production.performance_stats(returns, variant)
        stats["AverageSleeveWeight"] = daily_output["SleeveWeight"].mean()
        stats["ActiveDays"] = int((daily_output["SleeveWeight"] > 0.0).sum())
        stats["TotalTurnover"] = daily_output["Turnover"].sum()
        stats["CostBps"] = args.cost_bps
        summary_rows.append(stats)
        daily_output.to_csv(args.output_dir / f"daily_returns_{variant.lower()}.csv")
        signal_log.to_csv(args.output_dir / f"signal_log_{variant.lower()}.csv", index=False)
        event_study = add_forward_event_returns(
            eligibility_log, indicators, baseline_returns
        )
        event_study.to_csv(
            args.output_dir / f"eligibility_log_{variant.lower()}.csv", index=False
        )
        event_summary_rows.append(summarize_event_study(event_study, variant))

    control_entry_whitelist: dict[pd.Timestamp, set[str]] | None = None
    for variant, config in daily_variants.items():
        candidate_tickers = config.get("tickers", broad_tickers)
        prebuilt_long_table = (
            risk_long_table
            if set(candidate_tickers) == set(risk_asset_tickers)
            else broad_long_table
        )
        entry_event_whitelist = None
        if config.get("freeze_control_entries", False):
            if control_entry_whitelist is None:
                raise RuntimeError(
                    "The confirmed-entry control must run before frozen-entry exits."
                )
            entry_event_whitelist = control_entry_whitelist
        returns, daily_output, signal_log, eligibility_log = (
            backtest_daily_confirmation_variant(
                variant=variant,
                indicators=indicators,
                baseline_returns=baseline_returns,
                candidate_tickers=candidate_tickers,
                max_holdings=args.max_holdings,
                weight_per_holding=args.weight_per_holding,
                max_holding_days=config["max_days"],
                cost_bps=args.cost_bps,
                rank_ascending=config["rank_ascending"],
                max_pair_correlation=config["max_correlation"],
                replacement_policy=config.get("replacement_policy", "none"),
                min_replacement_days=config.get("min_replacement_days", 10),
                signal_column=config.get("signal", "SignalTwoStageConfirm"),
                probe_signal_column=config.get("probe_signal"),
                probe_weight_per_holding=config.get("probe_weight"),
                profit_stop_activation=config.get("profit_stop_activation"),
                atr_trailing_multiple=config.get("atr_trailing_multiple"),
                atr_stop_floor_at_entry=config.get("atr_stop_floor_at_entry", True),
                entry_event_whitelist=entry_event_whitelist,
                prebuilt_long_table=prebuilt_long_table,
                precomputed_asset_returns=all_asset_returns,
            )
        )
        if variant == "TwoStageQuality10Risk20DATR125":
            control_entry_whitelist = {}
            for row in signal_log.loc[
                signal_log["Action"].eq("Enter"), ["Date", "Ticker"]
            ].itertuples(index=False):
                control_entry_whitelist.setdefault(
                    pd.Timestamp(row.Date), set()
                ).add(str(row.Ticker))
        return_map[variant] = returns
        stats = production.performance_stats(returns, variant)
        stats["AverageSleeveWeight"] = daily_output["SleeveWeight"].mean()
        stats["ActiveDays"] = int((daily_output["SleeveWeight"] > 0.0).sum())
        stats["TotalTurnover"] = daily_output["Turnover"].sum()
        stats["CostBps"] = args.cost_bps
        summary_rows.append(stats)
        daily_output.to_csv(args.output_dir / f"daily_returns_{variant.lower()}.csv")
        signal_log.to_csv(args.output_dir / f"signal_log_{variant.lower()}.csv", index=False)
        event_study = add_forward_event_returns(
            eligibility_log, indicators, baseline_returns
        )
        event_study.to_csv(
            args.output_dir / f"eligibility_log_{variant.lower()}.csv", index=False
        )
        event_summary_rows.append(summarize_event_study(event_study, variant))

    summary = pd.DataFrame(summary_rows).set_index("Name")
    baseline_stats = summary.loc["ProductionBaseline"]
    for metric in ["CAGR", "Sharpe", "Max Drawdown", "MAR", "Sortino"]:
        summary[f"Delta{metric.replace(' ', '')}VsBaseline"] = summary[metric] - baseline_stats[metric]
    summary.to_csv(args.output_dir / "variant_summary.csv")
    annual_return_table(return_map).to_csv(args.output_dir / "annual_returns.csv", index=False)
    pd.concat(event_summary_rows, ignore_index=True).to_csv(
        args.output_dir / "event_study_summary.csv", index=False
    )

    print("\nLate-July GLD diagnostic:")
    print(
        diagnostics[
            diagnostics["Ticker"].eq("GLD")
        ][[
            "Date", "Close", "RSI14", "RecentRSIMin20", "EMA10", "EMA20",
            "Prior20High", "MACDHist", "MACDHistDelta3", "SetupCount",
            "WashoutWatchAge", "SignalStrict", "SignalWashoutTurn",
            "SignalTwoStageConfirm",
        ]].to_string(index=False)
    )
    print("\nVariant summary:")
    print(summary[[
        "CAGR", "Sharpe", "Max Drawdown", "MAR", "Sortino",
        "AverageSleeveWeight", "ActiveDays", "TotalTurnover",
        "DeltaCAGRVsBaseline", "DeltaSharpeVsBaseline",
    ]])
    print(f"\nOutputs written to {args.output_dir}")
    print(f"Total runtime: {perf_counter() - run_started:.1f}s.")


if __name__ == "__main__":
    main()
