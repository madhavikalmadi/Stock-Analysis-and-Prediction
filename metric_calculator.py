import numpy as np
import pandas as pd
from math import sqrt

# --------------------------------------------------------------
# Helper Function
# --------------------------------------------------------------

def calculate_recovery_days(series, cummax_series=None):
    """
    Calculates the number of days to recover to the All-Time High 
    from the lowest point of the Max Drawdown.

    Args:
        series (pd.Series): The daily stock prices.
        cummax_series (pd.Series, optional): Pre-calculated cumulative max.

    Returns:
        int or np.nan: Days to recover, or NaN if not recovered.
    """
    if cummax_series is None:
        cummax_series = series.cummax()
    
    # Calculate drawdown percentage series
    dd = (series / cummax_series - 1)
    min_dd = dd.min()
    
    # If no drawdown (flat or straight up)
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
    if len(recovered_dates) < 1: 
        return np.nan
        
    # The first date it crossed the target
    date_of_recovery = recovered_dates.index[0]
    
    # Return difference in days
    return (date_of_recovery - date_of_bottom).days

# --------------------------------------------------------------
# Main Computation Engine
# --------------------------------------------------------------

def compute_metrics(data, market_ticker, risk_free_rate=0.06):
    """
    Computes financial metrics (CAGR, Sharpe, Sortino, etc.) for a dataframe of stocks.

    Args:
        data (pd.DataFrame): DataFrame with datetime index and columns as Tickers.
        market_ticker (str): The column name representing the market benchmark (e.g., '^NSEI').
        risk_free_rate (float): The annual risk-free rate (default 0.06 for 6%).

    Returns:
        pd.DataFrame: A summary table of metrics for each ticker.
    """
    if data.empty:
        return pd.DataFrame()

    # 1. VECTORIZED PRE-CALCULATION
    daily_returns = data.pct_change().dropna()
    cummax_df = data.cummax()
    drawdown_df = (data / cummax_df) - 1
    max_drawdowns = drawdown_df.min()

    # Prepare Market Data for Beta
    market_ret = None
    market_var = None
    
    if market_ticker in daily_returns.columns:
        market_ret = daily_returns[market_ticker]
        market_var = market_ret.var()

    TRADING_DAYS = 252
    results = []

    # 2. METRIC LOOP
    for ticker in data.columns:
        # Skip the market ticker itself if you don't want it in the results, 
        # or keep it to see benchmark stats.
        
        try:
            series = data[ticker]
            ret_series = daily_returns[ticker]
            
            # CAGR
            start_val, end_val = series.iloc[0], series.iloc[-1]
            years = (series.index[-1] - series.index[0]).days / 365.0
            cagr = ((end_val / start_val) ** (1 / years)) - 1 if years > 0 else 0
            
            # Volatility
            volatility = ret_series.std() * sqrt(TRADING_DAYS)
            
            # Sharpe Ratio
            excess_return_daily = ret_series.mean() * TRADING_DAYS - risk_free_rate
            sharpe = excess_return_daily / volatility if volatility != 0 else np.nan
            
            # Sortino Ratio
            neg_rets = ret_series[ret_series < 0]
            downside_std = neg_rets.std() * sqrt(TRADING_DAYS)
            sortino = excess_return_daily / downside_std if downside_std != 0 else np.nan
            
            # Max Drawdown & Calmar
            mdd = max_drawdowns[ticker]
            calmar = cagr / abs(mdd) if mdd != 0 else np.nan
            
            # Beta
            if market_ret is not None and market_var is not None and market_var != 0:
                cov = ret_series.cov(market_ret)
                beta = cov / market_var
            else:
                beta = np.nan

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
            
        except Exception as e:
            # If one ticker fails, log it (or print) but don't crash the app
            print(f"Error computing metrics for {ticker}: {e}")
            continue

    return pd.DataFrame(results)