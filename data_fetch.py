import yfinance as yf
import pandas as pd
import streamlit as st

# --- CONFIGURATION ---
# (Ideally, move these to a separate constants.py file in the future)
BLUECHIP_TICKERS = [
    "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE",
    "BHARTIARTL", "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR",
    "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI",
    "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
    "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS", "TECHM", "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
]

INDEX_GROUPS = {
    "NIFTY50": [t + ".NS" for t in BLUECHIP_TICKERS],
    "NIFTYIT": ["INFY.NS", "TCS.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS"],
    "NIFTYBANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
}

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_stock_data(tickers, period="10y"):
    """
    Downloads and cleans stock data.
    
    Args:
        tickers (list): List of ticker symbols (e.g., ['RELIANCE', 'TCS']).
        period (str): The historical period to download (e.g., '1y', '5y', '10y', 'max').
    
    Returns:
        pd.DataFrame: A cleaned DataFrame of Adjusted Close prices.
    """
    if not tickers:
        return pd.DataFrame()

    # 1. OPTIMIZATION: Robust Suffix Handling & Sorting
    # Uses .endswith() for safety and sorts to ensure cache hits (['A','B'] == ['B','A'])
    processed_tickers = sorted([t if t.endswith(".NS") else f"{t}.NS" for t in tickers])

    try:
        # 2. DATA FETCHING
        # using 'period' lets yfinance handle trading days logic automatically
        raw_data = yf.download(
            processed_tickers, 
            period=period, 
            progress=False, 
            auto_adjust=False,
            threads=True
        )
    except Exception as e:
        print(f"Data Download Error: {e}")
        return pd.DataFrame()

    if raw_data.empty:
        return pd.DataFrame()

    # 3. COLUMN SELECTION
    if 'Adj Close' in raw_data.columns:
        data = raw_data['Adj Close']
    elif 'Close' in raw_data.columns:
        data = raw_data['Close']
    else:
        # Fallback if neither exists (rare)
        data = raw_data.iloc[:, 0]

    # Ensure we always return a DataFrame (even for single stock)
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # 4. CLEANING
    # Handle missing values: Forward fill first (carry last price), then backfill
    data = data.ffill().bfill()
    
    # Drop columns that are mostly empty (>20% missing)
    # This removes stocks that might have delisted or have bad data
    threshold = int(0.80 * len(data))
    data = data.dropna(axis=1, thresh=threshold)
    
    return data