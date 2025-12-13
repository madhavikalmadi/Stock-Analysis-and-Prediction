import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# --- CONFIGURATION ---
BLUECHIP_TICKERS = [
    "ADANIENT","ADANIPORTS","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE",
    "BHARTIARTL","BPCL","BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY","EICHERMOT",
    "GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO","HINDUNILVR",
    "ICICIBANK","INDUSINDBK","INFY","ITC","JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI",
    "NESTLEIND","NTPC","ONGC","POWERGRID","RELIANCE","SBILIFE","SBIN","SUNPHARMA",
    "TATACONSUM","TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]

# Standard Groups
INDEX_GROUPS = {
    "NIFTY50": [t + ".NS" for t in BLUECHIP_TICKERS],
    "NIFTYIT": ["INFY.NS", "TCS.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS"],
    "NIFTYBANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
}

# 1. OPTIMIZATION: Combine Fetch & Clean into one cached function
# This ensures we don't re-calculate 'ffill' or 'bfill' on every interaction.
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_stock_data(tickers):
    """
    Downloads and cleans stock data. 
    Cached for 24 hours to prevent constant re-downloading.
    """
    if not tickers:
        return pd.DataFrame()

    # 2. OPTIMIZATION: Sort tickers to ensure cache hits regardless of order
    # (e.g., ['TCS', 'INFY'] matches ['INFY', 'TCS'])
    tickers = sorted([t if ".NS" in t else t + ".NS" for t in tickers])
    
    # 3. OPTIMIZATION: Calculate dates inside function so they are always current
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')

    try:
        # Download data
        raw_data = yf.download(
            tickers, 
            start=start_date, 
            end=end_date, 
            progress=False, 
            auto_adjust=False,
            threads=True # Use parallel threads
        )
    except Exception as e:
        st.error(f"Data Download Error: {e}")
        return pd.DataFrame()

    if raw_data.empty:
        return pd.DataFrame()

    # Robust Column Selection
    if 'Adj Close' in raw_data.columns:
        data = raw_data['Adj Close']
    elif 'Close' in raw_data.columns:
        data = raw_data['Close']
    else:
        data = raw_data.iloc[:, 0] # Fallback

    # Ensure we always return a DataFrame, even for a single stock
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # 4. OPTIMIZATION: Perform cleaning HERE so the result is cached
    data = data.ffill().bfill()
    
    # Drop columns with > 20% missing data
    data = data.dropna(axis=1, thresh=int(0.80 * len(data)))
    
    return data

# Wrapper function if you need to call it without caching logic elsewhere (optional)
def clean_data(data):
    # This function is now largely redundant but kept for backward compatibility 
    # if other files import it. It just passes data through.
    return data