import numpy as np
import pandas as pd
import streamlit as st
from math import sqrt

# --------------------------------------------------------------
# Helper Function (Complex Logic Only)
# --------------------------------------------------------------

def calculate_recovery_days(series, cummax_series=None):
    """
    Calculates days to recover to All-Time High from the lowest point of the Max Drawdown.
    """
    if cummax_series is None:
        cummax_series = series.cummax()
    
    # Calculate drawdown percentage series
    dd = (series / cummax_series - 1)
    min_dd = dd.min()
    
    # If no drawdown or data is flat
    if min_dd == 0:
        return 0
        
    # Find the date of the absolute bottom (Max Drawdown)
    drawdown_periods = dd[dd == min_dd]
    if drawdown_periods.empty:
        return 0
    date_of_bottom = drawdown_periods.index[-1]
    
    # Filter data to look only at dates AFTER the bottom
    future_data = series.loc[date_of_bottom:]
    
    # Target price to beat is the highest price seen BEFORE or AT the bottom
    target_price = cummax_series.loc[date_of_bottom]
    
    # Find days where price >= target
    recovered_dates = future_data[future_data >= target_price]
    
    # If it never recovered
    if len(recovered_dates) < 2: 
        return np.nan
        
    # The first date it crossed the target
    date_of_recovery = recovered_dates.index[0]
    
    # Return difference in days
    return (date_of_recovery - date_of_bottom).days

# --------------------------------------------------------------
# Main Computation Engine (Vectorized)
# --------------------------------------------------------------

@st.cache_data
def compute_metrics(data, market_ticker):
    """
    Computes all financial metrics for all stocks in the provided dataframe efficiently.
    """
    if data.empty:
        return pd.DataFrame()

    # 1. VECTORIZED PRE-CALCULATION
    daily_returns = data.pct_change().dropna()
    cummax_df = data.cummax()
    drawdown_df = (data / cummax_df) - 1
    max_drawdowns = drawdown_df.min()

    # Prepare Market Data for Beta
    if market_ticker in daily_returns.columns:
        market_ret = daily_returns[market_ticker]
        market_var = market_ret.var()
    else:
        market_ret = pd.Series(np.ones(len(daily_returns)), index=daily_returns.index)
        market_var = 1.0

    RISK_FREE_RATE = 0.06
    TRADING_DAYS = 252
    results = []

    # 2. FAST LOOKUP LOOP
    for ticker in data.columns:
        series = data[ticker]
        ret_series = daily_returns[ticker]
        
        # CAGR
        start_val, end_val = series.iloc[0], series.iloc[-1]
        years = (series.index[-1] - series.index[0]).days / 365.0
        cagr = ((end_val / start_val) ** (1 / years)) - 1 if years > 0 else 0
        
        # Volatility
        volatility = ret_series.std() * sqrt(TRADING_DAYS)
        
        # Sharpe
        excess_return_daily = ret_series.mean() * TRADING_DAYS - RISK_FREE_RATE
        sharpe = excess_return_daily / volatility if volatility != 0 else np.nan
        
        # Sortino
        neg_rets = ret_series[ret_series < 0]
        downside_std = neg_rets.std() * sqrt(TRADING_DAYS)
        sortino = excess_return_daily / downside_std if downside_std != 0 else np.nan
        
        # Max Drawdown & Calmar
        mdd = max_drawdowns[ticker]
        calmar = cagr / abs(mdd) if mdd != 0 else np.nan
        
        # Beta
        cov = ret_series.cov(market_ret)
        beta = cov / market_var if market_var != 0 else np.nan

        # Recovery Days
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

    return pd.DataFrame(results)