import numpy as np
import pandas as pd
from math import sqrt
from datetime import timedelta
import streamlit as st

# --------------------------------------------------------------
# Helper Function (UNCHANGED)
# --------------------------------------------------------------
def calculate_recovery_days(series, cummax_series=None):
    if cummax_series is None:
        cummax_series = series.cummax()

    dd = (series / cummax_series - 1)
    min_dd = dd.min()

    if min_dd == 0:
        return 0

    drawdown_periods = dd[dd == min_dd]
    if drawdown_periods.empty:
        return 0

    date_of_bottom = drawdown_periods.index[-1]
    future_data = series.loc[date_of_bottom:]
    target_price = cummax_series.loc[date_of_bottom]
    recovered_dates = future_data[future_data >= target_price]

    if recovered_dates.empty:
        return np.nan

    date_of_recovery = recovered_dates.index[0]
    return (date_of_recovery - date_of_bottom).days


# --------------------------------------------------------------
# Main Computation Engine (FINAL, CORRECT VERSION)
# --------------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=3600)
def compute_metrics(data, market_ticker, risk_free_rate=0.06):

    if data is None or data.empty:
        return pd.DataFrame(columns=[
            "Ticker", "CAGR", "Volatility", "Sharpe", "Sortino",
            "Calmar", "MaxDrawdown", "Beta", "RecoveryDays"
        ])

    # ----------------------------------------------------------
    # Enforce SAME 10-YEAR WINDOW
    # ----------------------------------------------------------
    end_date = data.index.max()
    start_date = end_date - timedelta(days=365 * 10)
    data = data.loc[data.index >= start_date]

    TRADING_DAYS = 252
    min_days_required = int(0.90 * TRADING_DAYS * 10)

    data = data.dropna(axis=1, thresh=min_days_required)

    if data.empty:
        return pd.DataFrame(columns=[
            "Ticker", "CAGR", "Volatility", "Sharpe", "Sortino",
            "Calmar", "MaxDrawdown", "Beta", "RecoveryDays"
        ])

    # ----------------------------------------------------------
    # Daily returns (robust for index + ETF)
    # ----------------------------------------------------------
    daily_returns = data.pct_change().dropna()

    # Remove impossible Yahoo glitches (>50% move in one day)
    daily_returns = daily_returns.clip(lower=-0.5, upper=0.5)

    # ----------------------------------------------------------
    # Drawdown prep
    # ----------------------------------------------------------
    cummax_df = data.cummax()
    drawdown_df = (data / cummax_df) - 1
    max_drawdowns = drawdown_df.min()

    # ----------------------------------------------------------
    # Market returns (for beta)
    # ----------------------------------------------------------
    market_ret = None
    market_var = None
    if market_ticker in daily_returns.columns:
        market_ret = daily_returns[market_ticker]
        market_var = market_ret.var()

    results = []

    # ----------------------------------------------------------
    # Metric loop
    # ----------------------------------------------------------
    for ticker in data.columns:
        try:
            series = data[ticker].dropna()
            ret_series = daily_returns[ticker].dropna()

            if len(ret_series) < min_days_required:
                continue

            # --------------------------------------------------
            # ✅ CORRECT CAGR (RETURN-BASED, NOT PRICE-BASED)
            # --------------------------------------------------
            total_return = (1 + ret_series).prod()
            years = len(ret_series) / TRADING_DAYS
            cagr = total_return ** (1 / years) - 1

            # --------------------------------------------------
            # Volatility
            # --------------------------------------------------
            volatility = ret_series.std() * sqrt(TRADING_DAYS)

            # --------------------------------------------------
            # Sharpe (CAGR-based, consistent)
            # --------------------------------------------------
            sharpe = (
                (cagr - risk_free_rate) / volatility
                if volatility != 0 else np.nan
            )

            # --------------------------------------------------
            # Sortino
            # --------------------------------------------------
            downside = ret_series[ret_series < 0]
            downside_std = downside.std() * sqrt(TRADING_DAYS)
            sortino = (
                (cagr - risk_free_rate) / downside_std
                if downside_std != 0 else np.nan
            )

            # --------------------------------------------------
            # Max Drawdown & Calmar
            # --------------------------------------------------
            mdd = max_drawdowns[ticker]
            calmar = cagr / abs(mdd) if mdd != 0 else np.nan

            # --------------------------------------------------
            # Beta (optional, safe)
            # --------------------------------------------------
            beta = (
                ret_series.cov(market_ret) / market_var
                if market_ret is not None and market_var not in (0, None)
                else np.nan
            )

            # --------------------------------------------------
            # Recovery Days
            # --------------------------------------------------
            recovery = calculate_recovery_days(series, cummax_df[ticker])

            results.append({
                "Ticker": ticker,
                "CAGR": cagr,
                "Volatility": volatility,
                "Sharpe": sharpe,
                "Sortino": sortino,
                "Calmar": calmar,
                "MaxDrawdown": mdd,
                "Beta": beta,
                "RecoveryDays": recovery
            })

        except Exception as e:
            print(f"Error computing metrics for {ticker}: {e}")


    return pd.DataFrame(results)

# --------------------------------------------------------------
# Simple Wrapper for One Stock (User Requested)
# --------------------------------------------------------------
def calculate_metrics(df):
    """
    Simplified wrapper that calls compute_metrics for a single dataframe.
    Assumes benchmarking against Nifty 50 (^NSEI).
    """
    # compute_metrics expectes a DataFrame where columns are Tickers.
    # If df is just a single stock search, we pass it as is.
    return compute_metrics(df, market_ticker="^NSEI")
