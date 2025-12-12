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

START_DATE = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

@st.cache_data(ttl=86400)
def fetch_stock_data(tickers):
    # Ensure .NS extension
    tickers = [t if ".NS" in t else t + ".NS" for t in tickers]
    
    # 1. Download with auto_adjust=False to force 'Adj Close' to appear if possible
    try:
        raw_data = yf.download(tickers, start=START_DATE, end=END_DATE, progress=False, auto_adjust=False)
    except Exception as e:
        st.error(f"Data Download Error: {e}")
        return pd.DataFrame()

    # 2. Robust Column Selection (The Fix)
    if raw_data.empty:
        return pd.DataFrame()

    # Check if 'Adj Close' exists (Multi-level or Single level)
    if 'Adj Close' in raw_data.columns:
        data = raw_data['Adj Close']
    elif 'Close' in raw_data.columns:
        # Fallback to 'Close' if 'Adj Close' is missing (newer yfinance versions)
        data = raw_data['Close']
    else:
        # Emergency fallback: take the first level/column if specific keys fail
        data = raw_data.iloc[:, 0]

    # Handle single ticker returning Series instead of DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame()
        
    data = data.dropna(how='all')
    return data

def clean_data(data):
    data = data.ffill().bfill()
    # Drop columns with > 20% missing data
    data = data.dropna(axis=1, thresh=int(0.80 * len(data)))
    return data