from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import ExecutionConfig, StandalonePortfolioConfig, WeeklyAWBConfig
from .strategies.weekly_awb import rank_weekly_candidates


@dataclass
class WeeklyBacktestResult:
    daily: pd.DataFrame
    trades: pd.DataFrame
    candidates: pd.DataFrame


@dataclass
class StandaloneBacktestResult:
    daily: pd.DataFrame
    trades: pd.DataFrame
    candidates: pd.DataFrame


def _weekly_snapshot(signal_table: pd.DataFrame, date: pd.Timestamp) -> pd.DataFrame:
    if signal_table.empty or date not in signal_table.index.get_level_values("Date"):
        return pd.DataFrame()
    return signal_table.xs(date, level="Date").copy()


def run_weekly_awb_backtest(
    daily_features: dict[str, pd.DataFrame],
    signal_table: pd.DataFrame,
    baseline_returns: pd.Series,
    execution: ExecutionConfig,
    strategy: WeeklyAWBConfig,
) -> WeeklyBacktestResult:
    common_start = max(
        baseline_returns.index.min(),
        min(frame.index.min() for frame in daily_features.values()),
    )
    common_end = min(
        baseline_returns.index.max(),
        max(frame.index.max() for frame in daily_features.values()),
    )
    dates = baseline_returns.loc[common_start:common_end].index
    cost_rate = execution.cost_bps_per_side / 10_000.0

    cash = 1.0
    shares = 0.0
    position: dict | None = None
    pending_entry: dict | None = None
    pending_exit: dict | None = None
    previous_equity = 1.0
    daily_rows: list[dict] = []
    trade_rows: list[dict] = []
    candidate_rows: list[dict] = []

    for date in dates:
        if pending_exit is not None and position is not None:
            frame = daily_features[position["Ticker"]]
            if date > pending_exit["SignalDate"] and date in frame.index:
                exit_open = float(frame.loc[date, "Open"])
                if np.isfinite(exit_open) and exit_open > 0.0:
                    cash = shares * exit_open * (1.0 - cost_rate)
                    gross_return = exit_open / position["EntryOpen"] - 1.0
                    net_return = (
                        (1.0 - cost_rate) ** 2
                        * exit_open
                        / position["EntryOpen"]
                        - 1.0
                    )
                    trade_rows.append(
                        {
                            **position,
                            "ExitSignalDate": pending_exit["SignalDate"],
                            "ExitDate": date,
                            "ExitOpen": exit_open,
                            "ExitReason": pending_exit["Reason"],
                            "GrossReturn": gross_return,
                            "NetReturn": net_return,
                            "Status": "Closed",
                        }
                    )
                    shares = 0.0
                    position = None
                    pending_exit = None

        if pending_entry is not None and position is None:
            ticker = pending_entry["Ticker"]
            frame = daily_features[ticker]
            if date > pending_entry["SignalDate"] and date in frame.index:
                entry_open = float(frame.loc[date, "Open"])
                if np.isfinite(entry_open) and entry_open > 0.0:
                    shares = cash * (1.0 - cost_rate) / entry_open
                    cash = 0.0
                    position = {
                        "Ticker": ticker,
                        "EntrySignalDate": pending_entry["SignalDate"],
                        "EntryDate": date,
                        "EntryOpen": entry_open,
                        "HoldingDays": 0,
                        "PeakHigh": entry_open,
                        "PeakGain": 0.0,
                        "EntryScore": pending_entry["Score"],
                        "EntryWeeklyRSI14": pending_entry["WeeklyRSI14"],
                        "EntryWeeksSinceLow": pending_entry["WeeksSinceLow26"],
                    }
                    pending_entry = None

        stop_level = np.nan
        stop_is_active = False
        close_value = np.nan
        if position is not None:
            ticker = position["Ticker"]
            frame = daily_features[ticker]
            if date in frame.index:
                row = frame.loc[date]
                close_value = float(row["Close"])
                position["HoldingDays"] += 1
                position["PeakHigh"] = max(
                    position["PeakHigh"], float(row["High"])
                )
                position["PeakGain"] = (
                    position["PeakHigh"] / position["EntryOpen"] - 1.0
                )
                stop_is_active = (
                    position["PeakGain"] >= execution.profit_activation
                )
                if stop_is_active:
                    stop_level = (
                        position["PeakHigh"]
                        - execution.atr_trailing_multiple * float(row["ATR14"])
                    )
                    if execution.stop_floor_at_entry:
                        stop_level = max(position["EntryOpen"], stop_level)
                if pending_exit is None and stop_is_active and close_value < stop_level:
                    pending_exit = {
                        "SignalDate": date,
                        "Reason": "ATRProfitStop",
                    }
                if (
                    pending_exit is None
                    and not stop_is_active
                    and execution.initial_stop_atr_multiple is not None
                ):
                    initial_stop = (
                        position["EntryOpen"]
                        - execution.initial_stop_atr_multiple * float(row["ATR14"])
                    )
                    stop_level = initial_stop
                    if close_value < initial_stop:
                        pending_exit = {
                            "SignalDate": date,
                            "Reason": "ATRInitialRiskStop",
                        }
                if (
                    pending_exit is None
                    and position["HoldingDays"] >= execution.max_holding_days
                ):
                    pending_exit = {
                        "SignalDate": date,
                        "Reason": "MaxHoldingDays",
                    }

                weekly = _weekly_snapshot(signal_table, date)
                if ticker in weekly.index and pending_exit is None:
                    weekly_row = weekly.loc[ticker]
                    thesis_failed = (
                        weekly_row["Close"] < weekly_row["WeeklySMA40"]
                        and weekly_row["WeeklyRSI14"] < strategy.thesis_failure_rsi
                        and weekly_row["WeeklyMACDHist"] < 0.0
                    )
                    if thesis_failed:
                        pending_exit = {
                            "SignalDate": date,
                            "Reason": "WeeklyThesisFailure",
                        }

        snapshot = _weekly_snapshot(signal_table, date)
        if not snapshot.empty:
            eligible = snapshot.loc[snapshot["WeeklyAWBSignal"].fillna(False)].copy()
            if not eligible.empty:
                eligible["CandidateScore"] = rank_weekly_candidates(eligible)
                ordered = eligible.sort_values("CandidateScore", ascending=False)
                selected_ticker = None
                if position is None and pending_entry is None:
                    selected_ticker = str(ordered.index[0])
                    selected = ordered.loc[selected_ticker]
                    pending_entry = {
                        "Ticker": selected_ticker,
                        "SignalDate": date,
                        "Score": float(selected["CandidateScore"]),
                        "WeeklyRSI14": float(selected["WeeklyRSI14"]),
                        "WeeksSinceLow26": float(selected["WeeksSinceLow26"]),
                    }
                elif (
                    position is not None
                    and pending_entry is None
                    and pending_exit is None
                    and execution.replacement_min_holding_days is not None
                    and position["HoldingDays"]
                    >= execution.replacement_min_holding_days
                    and position["Ticker"] not in eligible.index
                ):
                    selected_ticker = str(ordered.index[0])
                    selected = ordered.loc[selected_ticker]
                    pending_exit = {
                        "SignalDate": date,
                        "Reason": "WeeklyReplacement",
                    }
                    pending_entry = {
                        "Ticker": selected_ticker,
                        "SignalDate": date,
                        "Score": float(selected["CandidateScore"]),
                        "WeeklyRSI14": float(selected["WeeklyRSI14"]),
                        "WeeksSinceLow26": float(selected["WeeksSinceLow26"]),
                    }
                for ticker, row in ordered.iterrows():
                    candidate_rows.append(
                        {
                            "Date": date,
                            "Ticker": ticker,
                            "Selected": ticker == selected_ticker,
                            "CandidateScore": row["CandidateScore"],
                            "Close": row["Close"],
                            "WeeklyRSI14": row["WeeklyRSI14"],
                            "RecentWeeklyRSIMin26": row["RecentWeeklyRSIMin26"],
                            "WeeksSinceLow26": row["WeeksSinceLow26"],
                            "RecentDrawdownMin26": row["RecentDrawdownMin26"],
                            "WeeklyMACDHist": row["WeeklyMACDHist"],
                            "WeeklyMACDHistDelta1": row["WeeklyMACDHistDelta1"],
                            "WeeklyCMF20": row["WeeklyCMF20"],
                            "WeeklyATR14Pct": row["WeeklyATR14Pct"],
                            "DistanceAboveSMA40": row["DistanceAboveSMA40"],
                        }
                    )

        if position is not None:
            equity = shares * close_value if np.isfinite(close_value) else previous_equity
        else:
            equity = cash
        standalone_return = equity / previous_equity - 1.0
        baseline_return = float(baseline_returns.loc[date])
        overlay_return = (
            (1.0 - execution.overlay_weight) * baseline_return
            + execution.overlay_weight * standalone_return
        )
        daily_rows.append(
            {
                "Date": date,
                "BaselineReturn": baseline_return,
                "StandaloneSleeveReturn": standalone_return,
                "OverlayReturn": overlay_return,
                "StandaloneEquity": equity,
                "Ticker": position["Ticker"] if position is not None else "",
                "HoldingDays": position["HoldingDays"] if position is not None else 0,
                "PeakGain": position["PeakGain"] if position is not None else np.nan,
                "ATRStopActive": stop_is_active,
                "ATRStopLevel": stop_level,
                "PendingExitReason": pending_exit["Reason"] if pending_exit else "",
            }
        )
        previous_equity = equity

    if position is not None:
        ticker = position["Ticker"]
        frame = daily_features[ticker]
        final_date = dates[-1]
        final_close = float(frame.loc[:final_date, "Close"].iloc[-1])
        trade_rows.append(
            {
                **position,
                "ExitSignalDate": pd.NaT,
                "ExitDate": final_date,
                "ExitOpen": final_close,
                "ExitReason": "OpenMark",
                "GrossReturn": final_close / position["EntryOpen"] - 1.0,
                "NetReturn": (
                    (1.0 - cost_rate) * final_close / position["EntryOpen"] - 1.0
                ),
                "Status": "Open",
            }
        )

    daily = pd.DataFrame(daily_rows).set_index("Date")
    return WeeklyBacktestResult(
        daily=daily,
        trades=pd.DataFrame(trade_rows),
        candidates=pd.DataFrame(candidate_rows),
    )


def run_weekly_awb_strategy(
    daily_features: dict[str, pd.DataFrame],
    signal_table: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    execution: StandalonePortfolioConfig,
    strategy: WeeklyAWBConfig,
) -> StandaloneBacktestResult:
    """Backtest Weekly AWB as an independent fixed-slot portfolio."""
    cost_rate = execution.cost_bps_per_side / 10_000.0
    daily_cash_return = execution.annual_cash_return / 252.0
    cash = 1.0
    positions: dict[str, dict] = {}
    pending_entries: dict[str, dict] = {}
    pending_exits: dict[str, dict] = {}
    previous_equity = 1.0
    daily_rows: list[dict] = []
    trade_rows: list[dict] = []
    candidate_rows: list[dict] = []

    for date in calendar:
        cash *= 1.0 + daily_cash_return

        for ticker, order in list(pending_exits.items()):
            if ticker not in positions:
                pending_exits.pop(ticker, None)
                continue
            frame = daily_features[ticker]
            if date <= order["SignalDate"] or date not in frame.index:
                continue
            exit_open = float(frame.loc[date, "Open"])
            if not np.isfinite(exit_open) or exit_open <= 0.0:
                continue
            position = positions.pop(ticker)
            cash += position["Shares"] * exit_open * (1.0 - cost_rate)
            trade_rows.append(
                {
                    **{k: v for k, v in position.items() if k != "Shares"},
                    "ExitSignalDate": order["SignalDate"],
                    "ExitDate": date,
                    "ExitOpen": exit_open,
                    "ExitReason": order["Reason"],
                    "GrossReturn": exit_open / position["EntryOpen"] - 1.0,
                    "NetReturn": (
                        (1.0 - cost_rate) ** 2
                        * exit_open
                        / position["EntryOpen"]
                        - 1.0
                    ),
                    "Status": "Closed",
                }
            )
            pending_exits.pop(ticker, None)

        for ticker, order in list(pending_entries.items()):
            if len(positions) >= execution.max_positions:
                break
            frame = daily_features[ticker]
            if date <= order["SignalDate"] or date not in frame.index:
                continue
            entry_open = float(frame.loc[date, "Open"])
            if not np.isfinite(entry_open) or entry_open <= 0.0:
                continue
            slot_notional = previous_equity / execution.max_positions
            allocation = min(cash, slot_notional)
            if allocation <= 0.0:
                continue
            shares = allocation * (1.0 - cost_rate) / entry_open
            cash -= allocation
            positions[ticker] = {
                "Ticker": ticker,
                "EntrySignalDate": order["SignalDate"],
                "EntryDate": date,
                "EntryOpen": entry_open,
                "EntryAllocation": allocation,
                "EntryScore": order["Score"],
                "EntryWeeklyRSI14": order["WeeklyRSI14"],
                "EntryWeeksSinceLow": order["WeeksSinceLow26"],
                "HoldingDays": 0,
                "PeakHigh": entry_open,
                "PeakGain": 0.0,
                "LastClose": entry_open,
                "Shares": shares,
            }
            pending_entries.pop(ticker, None)

        for ticker, position in list(positions.items()):
            frame = daily_features[ticker]
            if date not in frame.index:
                continue
            row = frame.loc[date]
            close_value = float(row["Close"])
            position["HoldingDays"] += 1
            position["LastClose"] = close_value
            position["PeakHigh"] = max(position["PeakHigh"], float(row["High"]))
            position["PeakGain"] = position["PeakHigh"] / position["EntryOpen"] - 1.0
            profit_stop_active = (
                position["PeakGain"] >= execution.profit_activation
            )
            stop_level = np.nan
            exit_reason = None
            if profit_stop_active:
                stop_level = (
                    position["PeakHigh"]
                    - execution.atr_trailing_multiple * float(row["ATR14"])
                )
                if execution.stop_floor_at_entry:
                    stop_level = max(position["EntryOpen"], stop_level)
                if close_value < stop_level:
                    exit_reason = "ATRProfitStop"
            else:
                stop_level = (
                    position["EntryOpen"]
                    - execution.initial_stop_atr_multiple * float(row["ATR14"])
                )
                if close_value < stop_level:
                    exit_reason = "ATRInitialRiskStop"
            if exit_reason is None and position["HoldingDays"] >= execution.max_holding_days:
                exit_reason = "MaxHoldingDays"

            weekly = _weekly_snapshot(signal_table, date)
            if exit_reason is None and ticker in weekly.index:
                weekly_row = weekly.loc[ticker]
                if (
                    weekly_row["Close"] < weekly_row["WeeklySMA40"]
                    and weekly_row["WeeklyRSI14"] < strategy.thesis_failure_rsi
                    and weekly_row["WeeklyMACDHist"] < 0.0
                ):
                    exit_reason = "WeeklyThesisFailure"
            if exit_reason is not None and ticker not in pending_exits:
                pending_exits[ticker] = {
                    "SignalDate": date,
                    "Reason": exit_reason,
                    "StopLevel": stop_level,
                }

        snapshot = _weekly_snapshot(signal_table, date)
        if not snapshot.empty:
            eligible = snapshot.loc[snapshot["WeeklyAWBSignal"].fillna(False)].copy()
            if not eligible.empty:
                eligible["CandidateScore"] = rank_weekly_candidates(eligible)
                ordered = eligible.sort_values("CandidateScore", ascending=False)
                occupied = set(positions) | set(pending_entries)
                available_slots = execution.max_positions - len(occupied)
                selected_tickers: list[str] = []
                if available_slots > 0:
                    for ticker, row in ordered.iterrows():
                        ticker = str(ticker)
                        if ticker in occupied or ticker in pending_exits:
                            continue
                        pending_entries[ticker] = {
                            "Ticker": ticker,
                            "SignalDate": date,
                            "Score": float(row["CandidateScore"]),
                            "WeeklyRSI14": float(row["WeeklyRSI14"]),
                            "WeeksSinceLow26": float(row["WeeksSinceLow26"]),
                        }
                        selected_tickers.append(ticker)
                        if len(selected_tickers) >= available_slots:
                            break
                for ticker, row in ordered.iterrows():
                    candidate_rows.append(
                        {
                            "Date": date,
                            "Ticker": ticker,
                            "Selected": str(ticker) in selected_tickers,
                            "CandidateScore": row["CandidateScore"],
                            "Close": row["Close"],
                            "WeeklyRSI14": row["WeeklyRSI14"],
                            "RecentWeeklyRSIMin26": row["RecentWeeklyRSIMin26"],
                            "WeeksSinceLow26": row["WeeksSinceLow26"],
                            "RecentDrawdownMin26": row["RecentDrawdownMin26"],
                            "WeeklyMACDHist": row["WeeklyMACDHist"],
                            "WeeklyCMF20": row["WeeklyCMF20"],
                            "WeeklyATR14Pct": row["WeeklyATR14Pct"],
                        }
                    )

        position_value = sum(
            item["Shares"] * item["LastClose"] for item in positions.values()
        )
        equity = cash + position_value
        daily_rows.append(
            {
                "Date": date,
                "StrategyReturn": equity / previous_equity - 1.0,
                "StrategyEquity": equity,
                "Cash": cash,
                "CashWeight": cash / equity if equity > 0.0 else np.nan,
                "PositionCount": len(positions),
                "Tickers": ",".join(sorted(positions)),
                "PendingEntries": ",".join(sorted(pending_entries)),
                "PendingExits": ",".join(sorted(pending_exits)),
            }
        )
        previous_equity = equity

    final_date = calendar[-1]
    for ticker, position in positions.items():
        final_price = position["LastClose"]
        trade_rows.append(
            {
                **{k: v for k, v in position.items() if k != "Shares"},
                "ExitSignalDate": pd.NaT,
                "ExitDate": final_date,
                "ExitOpen": final_price,
                "ExitReason": "OpenMark",
                "GrossReturn": final_price / position["EntryOpen"] - 1.0,
                "NetReturn": (
                    (1.0 - cost_rate) * final_price / position["EntryOpen"] - 1.0
                ),
                "Status": "Open",
            }
        )

    return StandaloneBacktestResult(
        daily=pd.DataFrame(daily_rows).set_index("Date"),
        trades=pd.DataFrame(trade_rows),
        candidates=pd.DataFrame(candidate_rows),
    )
