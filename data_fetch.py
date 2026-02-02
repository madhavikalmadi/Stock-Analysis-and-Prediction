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
    "TATACONSUM", "TATASTEEL", "TCS", "TECHM", "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
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

# ==========================================
# CENTRALIZED STOCK DATA (Refactored from pages)
# ==========================================

ETF_INDEX_SYMBOLS = {
    "NIFTY 50": "NIFTYBEES.NS",
    "NIFTY NEXT 50": "JUNIORBEES.NS",
    "NIFTY MIDCAP 100": "MIDCAPETF.NS",
    "NIFTY SMALLCAP 100": "SMALLCAP.NS",
    "BANK NIFTY": "BANKBEES.NS",  # Added for completeness
    "NIFTY IT": "ITBEES.NS"       # Added for completeness
}

MARKET_DATA = {
    "✈️ Services Sector": {
        "NIFTY Services Sector": [
            "HDFCBANK", "TCS", "ICICIBANK", "BHARTIARTL", "INFY", "SBIN", "AXISBANK",
            "KOTAKBANK", "BAJFINANCE", "HCLTECH", "ADANIENT", "TITAN", "TECHM",
            "WIPRO", "BAJAJFINSV", "ADANIPORTS", "APOLLOHOSP", "HDFCLIFE", "SBILIFE",
            "POWERGRID", "NTPC", "INDIGO", "TRENT"
        ]
    },
    "🏦 Financial & Banking": {
        "NIFTY Bank": [
            "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
            "BANKBARODA", "PNB", "AUBANK", "FEDERALBNK", "IDFCFIRSTB", "BANDHANBNK"
        ],
        "NIFTY PSU Bank": [
            "SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "INDIANB",
            "BANKINDIA", "IOB", "UCOBANK", "CENTRALBK", "MAHABANK", "PSB"
        ],
        "NIFTY Private Bank": [
            "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
            "FEDERALBNK", "IDFCFIRSTB", "RBLBANK", "CUB", "BANDHANBNK"
        ],
        "NIFTY Fin Services": [
            "HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN", "BAJFINANCE", "BAJAJFINSV",
            "KOTAKBANK", "HDFCLIFE", "SBILIFE", "PFC", "CHOLAFIN",
            "SHRIRAMFIN", "MUTHOOTFIN", "HDFCAMC", "ICICIGI", "SBICARD", "RECLTD", "LICHSGFIN"
        ]
    },
    "💻 Technology & IT": {
        "NIFTY IT": [
            "TCS", "INFY", "HCLTECH", "TECHM", "WIPRO",
            "LTIM", "PERSISTENT", "COFORGE", "LTTS", "MPHASIS"
        ],
        "NIFTY Digital": [
            "NAUKRI", "PAYTM", "POLICYBZR", "NYKAA", "TATACOMM",
            "DELHIVERY", "INDIAMART", "AFFLE", "MAPMYINDIA",
            "TANLA", "LATENTVIEW", "CARTRADE", "FSL"
        ]
    },
    "🏠 Consumer & Lifestyle": {
        "NIFTY FMCG": [
            "HINDUNILVR", "ITC", "NESTLEIND", "VBL", "BRITANNIA", "GODREJCP",
            "TATACONSUM", "MARICO", "DABUR", "COLPAL",
            "UBL", "RADICO", "EMAMILTD"
        ],
        "NIFTY Auto": [
            "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT", "TVSMOTOR",
            "HEROMOTOCO", "MOTHERSON", "ASHOKLEY", "BHARATFORG", "TIINDIA",
            "MRF", "BOSCHLTD", "BALKRISIND", "SONACOMS"
        ],
        "NIFTY India Consumption 30": [
            "BHARTIARTL", "ITC", "HINDUNILVR", "M&M", "MARUTI", "TITAN",
            "ASIANPAINT", "INDIGO", "TRENT", "BAJAJ-AUTO", "DMART",
            "NESTLEIND", "ADANIPOWER", "DLF", "VBL", "GODREJCP", "APOLLOHOSP"
        ],
        "NIFTY Consumer Durables": [
            "TITAN", "HAVELLS", "DIXON", "VOLTAS", "BLUESTARCO",
            "AMBER", "CENTURYPLY", "KAJARIACER", "CROMPTON", "VGUARD",
            "RAJESHEXPO", "BATAINDIA", "WHIRLPOOL", "CERA"
        ],
        "NIFTY Media": [
            "SUNTV", "ZEEL", "PVRINOX", "NAZARA", "NETWORK18", "PFOCUS",
            "SAREGAMA", "DBCORP", "HATHWAY"
        ]
    },
    "🏗️ Realty & Construction": {
        "NIFTY Realty": [
            "DLF", "GODREJPROP", "PHOENIXLTD", "LODHA", "PRESTIGE",
            "OBEROIRLTY", "BRIGADE", "SOBHA", "SIGNATURE", "ANANTRAJ"
        ],
        "NIFTY Housing": [
            "LT", "NTPC", "ULTRACEMCO", "HDFCBANK", "ICICIBANK", "SBIN",
            "TATASTEEL", "JSWSTEEL", "GRASIM", "ASIANPAINT", "AMBUJACEM",
            "PIDILITIND", "DLF", "GODREJPROP", "HAVELLS", "VOLTAS",
            "CHOLAFIN", "LICHSGFIN", "PNBHOUSING", "KAJARIACER"
        ]
    },
    "🛢️ Energy & Resources": {
        "NIFTY Energy": [
            "RELIANCE", "NTPC", "ONGC", "POWERGRID", "COALINDIA",
            "BPCL", "IOC", "TATAPOWER", "GAIL", "ADANIGREEN"
        ],
        "NIFTY Oil & Gas": [
            "RELIANCE", "ONGC", "IOC", "BPCL", "GAIL", "HINDPETRO",
            "OIL", "PETRONET", "IGL", "ATGL", "GUJGASLTD", "MGL",
            "CASTROLIND", "GSPL"
        ],
        "NIFTY Metal": [
            "TATASTEEL", "HINDALCO", "JSWSTEEL", "JINDALSTEL", "VEDL",
            "ADANIENT", "NMDC", "SAIL", "NATIONALUM", "APLAPOLLO",
            "HINDZINC", "JSL", "WELCORP", "RATNAMANI"
        ],
        "NIFTY Commodities": [
            "RELIANCE", "ULTRACEMCO", "TATASTEEL", "NTPC", "JSWSTEEL",
            "ONGC", "GRASIM", "HINDALCO", "COALINDIA", "PIDILITIND",
            "VEDL", "SHREECEM", "AMBUJACEM", "BPCL", "JINDALSTEL"
        ]
    },
    "💊 Healthcare": {
        "NIFTY Pharma": [
            "SUNPHARMA", "DIVISLAB", "CIPLA", "TORNTPHARM", "DRREDDY",
            "LUPIN", "ZYDUSLIFE", "MANKIND", "ALKEM", "AUROPHARMA",
            "ABBOTINDIA", "GLENMARK", "BIOCON", "LAURUSLABS", "IPCALAB",
            "JBCHEPHARM", "GLAND", "NATCOPHARM", "PFIZER", "GRANULES"
        ],
        "NIFTY Healthcare": [
            "APOLLOHOSP", "MAXHEALTH", "FORTIS", "MEDANTA", "NH",
            "LALPATHLAB", "METROPOLIS", "SYNGENE", "POLYMED", "RAINBOW",
            "SUNPHARMA", "DIVISLAB", "CIPLA", "DRREDDY", "ALKEM",
            "LUPIN", "AUROPHARMA", "ZYDUSLIFE", "TORNTPHARM", "ABBOTINDIA"
        ]
    },
    "⚙️ Infra & Industrial": {
        "NIFTY Infrastructure": [
            "RELIANCE", "BHARTIARTL", "LT", "NTPC", "POWERGRID", "ULTRACEMCO",
            "ONGC", "ADANIPORTS", "GRASIM", "INDIGO", "TITAN", "TATAPOWER",
            "HINDUNILVR", "BPCL", "APOLLOHOSP", "SHREECEM", "INDHOTEL", "GAIL"
        ],
        "NIFTY CPSE": [
            "NTPC", "ONGC", "BEL", "COALINDIA", "POWERGRID", "NHPC", "OIL",
            "SJVN", "COCHINSHIP", "NLCINDIA", "NBCC", "IRCON"
        ],
        "NIFTY PSE": [
            "NTPC", "ONGC", "BEL", "HAL", "POWERGRID", "COALINDIA", "IOC",
            "PFC", "GAIL", "BPCL", "BHARATFORG", "BHEL", "OIL",
            "CONCOR", "NMDC", "LICHSGFIN", "HINDPETRO"
        ],
        "NIFTY Industrials": [
            "LT", "HAL", "SIEMENS", "ABB", "BEL", "CGPOWER", "CUMMINSIND",
            "POLYCAB", "BHEL", "THERMAX", "BHARATFORG", "TIMKEN",
            "AIAENG", "SCHAEFFLER", "APLAPOLLO", "SUZLON"
        ]
    },
    "🌱 Thematic & Emerging": {
        "NIFTY SME EMERGE": [
            "KOTYARK", "UCL", "HPIL", "E2E", "ORIANA",
            "RELIABLE", "BASILIC"
        ],
        "NIFTY India Defence": [
            "HAL", "BEL", "MAZDOCK", "BDL", "COCHINSHIP", "SOLARINDS",
            "BHARATFORG", "MTARTECH", "ASTRAMICRO",
            "PARAS", "GRSE", "MIDHANI", "IDEAFORGE"
        ],
        "NIFTY Mobility": [
            "MARUTI", "M&M", "BAJAJ-AUTO", "INDIGO",
            "MOTHERSON", "BOSCHLTD", "SONACOMS", "EXIDEIND", "APOLLOTYRE",
            "MRF", "HEROMOTOCO", "TVSMOTOR", "EICHERMOT"
        ],
        "NIFTY MNC": [
            "HINDUNILVR", "NESTLEIND", "BRITANNIA", "MARUTI", "SIEMENS",
            "ABB", "COLPAL", "CUMMINSIND", "ABBOTINDIA",
            "HONAUT", "BOSCHLTD", "PFIZER", "SANOFI", "BATAINDIA"
        ],
        "NIFTY Dividend Opps 50": [
            "ITC", "HINDUNILVR", "TCS", "INFY", "HCLTECH", "POWERGRID",
            "ONGC", "COALINDIA", "VEDL", "IOC", "BPCL", "HINDZINC",
            "PETRONET", "NHPC", "RECLTD", "PFC"
        ],
        "NIFTY EV & New Age Auto": [
            "M&M", "EXIDEIND", "MOTHERSON",
            "TATACHEM", "OLECTRA", "JBMA", "TVSMOTOR", "SONACOMS",
            "GREAVESCOT"
        ],
        "NIFTY ESG": [
            "INFY", "TCS", "HDFCBANK", "TITAN", "WIPRO", "TECHM",
            "HCLTECH", "HAVELLS", "GODREJCP", "LT", "KOTAKBANK",
            "MARICO", "ASIANPAINT", "APOLLOHOSP"
        ]
    },
    "🧠 NIFTY Strategy & Factor": {
        "NIFTY Alpha 50": ["BHARTIARTL", "BAJFINANCE", "MARUTI", "M&M", "TRENT", "ADANIENT", "HAL", "BEL", "INDIGO"],
        "NIFTY Momentum 30": ["HDFCBANK", "ICICIBANK", "BHARTIARTL", "TRENT", "BEL", "COALINDIA", "NTPC", "BAJFINANCE"],
        "NIFTY Low Volatility 30": ["RELIANCE", "HDFCBANK", "TCS", "SBIN", "CIPLA", "SUNPHARMA", "HINDUNILVR", "ITC", "POWERGRID", "INFY"],
        "NIFTY Quality 30": ["HDFCBANK", "INFY", "NESTLEIND", "ITC", "COALINDIA", "HCLTECH", "BRITANNIA", "HINDUNILVR", "TCS", "ASIANPAINT"],
        "NIFTY Growth Sectors 15": ["TCS", "INFY", "M&M", "BAJFINANCE", "TITAN", "MARUTI", "SUNPHARMA", "EICHERMOT", "HINDUNILVR", "CIPLA"],
        "NIFTY Shariah 25": ["ULTRACEMCO", "LTIM", "DIVISLAB", "CUMMINSIND", "RELIANCE", "TCS", "INFY", "HCLTECH", "ASIANPAINT", "TITAN"]
    }
}
