from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from .config import DataConfig


EXCLUDED_ASSET_CLASSES = {"Fixed Income & Cash", "Cryptocurrency"}


def load_risk_universe(universe_csv: Path) -> list[str]:
    categorization = pd.read_csv(universe_csv)
    required = {"Ticker", "Asset_Class"}
    missing = required - set(categorization.columns)
    if missing:
        raise ValueError(f"Universe file is missing columns: {sorted(missing)}")
    eligible = categorization.loc[
        ~categorization["Asset_Class"].isin(EXCLUDED_ASSET_CLASSES), "Ticker"
    ]
    return sorted(eligible.dropna().astype(str).unique().tolist())


def _extract_field(raw: pd.DataFrame, field: str) -> pd.DataFrame:
    if not isinstance(raw.columns, pd.MultiIndex):
        if field not in raw.columns:
            return pd.DataFrame(index=raw.index)
        return raw[[field]].rename(columns={field: "SINGLE"})
    if field in raw.columns.get_level_values(0):
        panel = raw[field].copy()
    elif field in raw.columns.get_level_values(1):
        panel = raw.xs(field, axis=1, level=1).copy()
    else:
        return pd.DataFrame(index=raw.index)
    return panel.to_frame() if isinstance(panel, pd.Series) else panel


def download_adjusted_ohlcv(
    tickers: list[str], start_date: str, end_date: str
) -> dict[str, pd.DataFrame]:
    yfinance_cache = Path("outputs_experiment_market_data_cache/yfinance_cache")
    yfinance_cache.mkdir(parents=True, exist_ok=True)
    if hasattr(yf, "set_tz_cache_location"):
        yf.set_tz_cache_location(str(yfinance_cache))
    raw = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=True,
        group_by="column",
        threads=True,
    )
    panels = {
        field: _extract_field(raw, field)
        for field in ["Open", "High", "Low", "Close", "Volume"]
    }
    close = panels["Close"].replace([np.inf, -np.inf], np.nan)
    close = close.dropna(axis=1, how="all")
    frames: dict[str, pd.DataFrame] = {}
    for ticker in close.columns:
        frame = pd.DataFrame(index=close.index)
        for field in ["Open", "High", "Low", "Close", "Volume"]:
            panel = panels[field]
            frame[field] = panel[ticker] if ticker in panel.columns else np.nan
        frame = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["Close"])
        if not frame.empty:
            frames[str(ticker)] = frame.sort_index()
    return frames


def _save_cache(
    frames: dict[str, pd.DataFrame], cache_file: Path, config: DataConfig
) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for ticker, frame in frames.items():
        item = frame.reset_index().rename(columns={frame.index.name or "index": "Date"})
        item.insert(1, "Ticker", ticker)
        rows.append(item)
    pd.concat(rows, ignore_index=True).to_pickle(cache_file)
    cache_file.with_suffix(".json").write_text(
        json.dumps(
            {
                "start_date": config.start_date,
                "end_date": config.end_date,
                "requested_tickers": sorted(frames),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def load_market_data(
    config: DataConfig, tickers: list[str], refresh: bool = False
) -> tuple[dict[str, pd.DataFrame], str]:
    cache_file = config.market_data_cache
    metadata_file = cache_file.with_suffix(".json")
    requested = set(tickers)
    if not refresh and cache_file.exists():
        cached = pd.read_pickle(cache_file)
        cached["Date"] = pd.to_datetime(cached["Date"])
        available = set(cached["Ticker"].astype(str).unique())
        selected = cached.loc[
            cached["Ticker"].isin(requested & available)
            & cached["Date"].ge(pd.Timestamp(config.start_date))
            & cached["Date"].lt(pd.Timestamp(config.end_date))
        ]
        frames = {
            str(ticker): group.drop(columns="Ticker").set_index("Date").sort_index()
            for ticker, group in selected.groupby("Ticker", sort=False)
        }
        missing = sorted(requested - available)
        if missing:
            try:
                downloaded = download_adjusted_ohlcv(
                    missing, config.start_date, config.end_date
                )
                frames.update(downloaded)
                if downloaded:
                    additions = []
                    for ticker, frame in downloaded.items():
                        item = frame.reset_index().rename(
                            columns={frame.index.name or "index": "Date"}
                        )
                        item.insert(1, "Ticker", ticker)
                        additions.append(item)
                    retained = cached.loc[~cached["Ticker"].isin(downloaded)]
                    pd.concat([retained, *additions], ignore_index=True).to_pickle(
                        cache_file
                    )
                    metadata = {}
                    if metadata_file.exists():
                        metadata = json.loads(
                            metadata_file.read_text(encoding="utf-8")
                        )
                    metadata["requested_tickers"] = sorted(available | set(downloaded))
                    metadata_file.write_text(
                        json.dumps(metadata, indent=2), encoding="utf-8"
                    )
            except Exception as exc:
                print(f"Warning: could not download missing tickers {missing}: {exc}")
        source = "cache" if requested <= set(frames) else "cache-partial"
        return frames, source
    frames = download_adjusted_ohlcv(tickers, config.start_date, config.end_date)
    if not frames:
        raise RuntimeError("No market data was downloaded; the cache was not modified.")
    _save_cache(frames, cache_file, config)
    return frames, "download"


def load_baseline_returns(config: DataConfig) -> pd.Series:
    if not config.baseline_csv.exists():
        raise FileNotFoundError(
            f"Baseline file not found: {config.baseline_csv}. Run production first."
        )
    frame = pd.read_csv(config.baseline_csv, parse_dates=["Date"]).set_index("Date")
    return frame["DailyReturn"].astype(float).sort_index()
