import numpy as np
import pandas as pd
import streamlit as st
from math import sqrt

# --------------------------------------------------------------
# Helper Functions for Each Metric
# --------------------------------------------------------------

def calculate_cagr(series):
    start, end = series.iloc[0], series.iloc[-1]
    years = (series.index[-1] - series.index[0]).days / 365
    return ((end / start) ** (1 / years)) - 1

def calculate_volatility(series):
    returns = series.pct_change().dropna()
    return returns.std() * sqrt(252)

def calculate_sharpe(series, risk_free_rate=0.06):
    returns = series.pct_change().dropna()
    excess_return = returns.mean() * 252 - risk_free_rate
    return excess_return / (returns.std() * sqrt(252))

def calculate_sortino(series, risk_free_rate=0.06):
    returns = series.pct_change().dropna()
    negative = returns[returns < 0]
    downside_std = negative.std() * sqrt(252)
    avg_return = returns.mean() * 252 - risk_free_rate
    return avg_return / downside_std if downside_std != 0 else np.nan

def calculate_calmar(series):
    cagr = calculate_cagr(series)
    mdd = calculate_max_drawdown(series)
    return cagr / abs(mdd) if mdd != 0 else np.nan

def calculate_max_drawdown(series):
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    return drawdown.min()

def calculate_beta(series, market_series):
    # Align the series dates
    common_idx = series.index.intersection(market_series.index)
    series = series.loc[common_idx]
    market_series = market_series.loc[common_idx]
    
    cov_matrix = np.cov(series.pct_change().dropna(), market_series.pct_change().dropna())
    return cov_matrix[0, 1] / cov_matrix[1, 1]

def calculate_recovery_days(series):
    cummax = series.cummax()
    dd = (series / cummax - 1)
    drawdown_periods = dd[dd == dd.min()]
    if drawdown_periods.empty:
        return 0
    recovery_index = np.argmax(series >= cummax.max())
    if recovery_index == 0:
        return np.nan
    recovery_time = (series.index[recovery_index] - drawdown_periods.index[-1]).days
    return recovery_time

# --------------------------------------------------------------
# Apply Metrics to All Stocks (Cached)
# --------------------------------------------------------------
@st.cache_data
def compute_metrics(data, market_ticker):
    # We pass the ticker string (e.g. "RELIANCE.NS") instead of the series
    # so Streamlit can hash it easily.
    market_series = data[market_ticker]
    
    results = []
    for ticker in data.columns:
        series = data[ticker]
        metrics = {
            "Ticker": ticker,
            "CAGR": calculate_cagr(series),
            "Volatility": calculate_volatility(series),
            "Sharpe": calculate_sharpe(series),
            "Sortino": calculate_sortino(series),
            "Calmar": calculate_calmar(series),
            "MaxDrawdown": calculate_max_drawdown(series),
            "Beta": calculate_beta(series, market_series),
            "RecoveryDays": calculate_recovery_days(series)
        }
        results.append(metrics)
    df = pd.DataFrame(results)
    return df