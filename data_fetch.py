import yfinance as yf
import pandas as pd
import streamlit as st

# --------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------
# --------------------------------------------------------------
# SEARCH SHORTCUTS (Friendly Name -> Ticker)
# --------------------------------------------------------------
# Used in: pages/company.py
SEARCH_SHORTCUTS = {
    # Original List
    "infosys": "INFY", "infy": "INFY",
    "reliance": "RELIANCE", "ril": "RELIANCE",
    "tcs": "TCS", 
    "hdfc bank": "HDFCBANK", "hdfc": "HDFCBANK",
    "icici bank": "ICICIBANK", "icici": "ICICIBANK",
    "sbi": "SBIN", "state bank": "SBIN",
    "bharti airtel": "BHARTIARTL", "airtel": "BHARTIARTL",
    "kotak": "KOTAKBANK", "kotak bank": "KOTAKBANK",
    "itc": "ITC", 
    "l&t": "LT", "larson": "LT",
    "axis bank": "AXISBANK", "axis": "AXISBANK",
    "hindustan unilever": "HINDUNILVR", "hul": "HINDUNILVR", 
    "maruti": "MARUTI", "maruti suzuki": "MARUTI",
    "sun pharma": "SUNPHARMA", 
    "titan": "TITAN", 
    "bajaj finance": "BAJFINANCE", 
    "wipro": "WIPRO", 
    "hcl": "HCLTECH", "hcl tech": "HCLTECH",
    "paytm": "PAYTM", 
    "nykaa": "NYKAA", 
    "swiggy": "SWIGGY", 
    "policybazaar": "POLICYBZR", 
    "delhivery": "DELHIVERY",

    # Additions (Top 50+)
    "adani ent": "ADANIENT", "adani enterprises": "ADANIENT",
    "adani ports": "ADANIPORTS", 
    "adani power": "ADANIPOWER",
    "asian paints": "ASIANPAINT", 
    "bajaj auto": "BAJAJ-AUTO", 
    "bajaj finserv": "BAJAJFINSV", 
    "bpcl": "BPCL", 
    "britannia": "BRITANNIA", 
    "cipla": "CIPLA", 
    "coal india": "COALINDIA", 
    "divis lab": "DIVISLAB", 
    "dr reddy": "DRREDDY", 
    "eicher": "EICHERMOT", "eicher motors": "EICHERMOT",
    "grasim": "GRASIM", 
    "hero": "HEROMOTOCO", "hero motocorp": "HEROMOTOCO",
    "hindalco": "HINDALCO", 
    "indusind": "INDUSINDBK", "indusind bank": "INDUSINDBK",
    "jsw steel": "JSWSTEEL", "jsw": "JSWSTEEL",
    "nestle": "NESTLEIND", 
    "ntpc": "NTPC", 
    "ongc": "ONGC", 
    "power grid": "POWERGRID", "pwrgrid": "POWERGRID",
    "tata consumer": "TATACONSUM", 
    "tata steel": "TATASTEEL", 
    "tata power": "TATAPOWER",
    "tech mahindra": "TECHM", "techm": "TECHM",
    "ultratech": "ULTRACEMCO", "ultratech cement": "ULTRACEMCO",
    "upl": "UPL", 
    "vedanta": "VEDL", 
    "jio fin": "JIOFIN", "jio financial": "JIOFIN",
    "irfc": "IRFC", 
    "pfc": "PFC", 
    "rec": "RECLTD", 
    "bel": "BEL", 
    "hal": "HAL", 
    "trent": "TRENT", 
    "varun beverages": "VBL", "vbl": "VBL",
    "siemens": "SIEMENS", 
    "abb": "ABB", 
    "dlf": "DLF", 
    "indigo": "INDIGO", 
    "irctc": "IRCTC",
    "mazagon": "MAZDOCK",
    "bhel": "BHEL"
}

# Used in: pages/bluechip.py
BLUECHIP_TICKERS = [
    "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE",
    "BHARTIARTL", "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR",
    "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI",
    "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
    "TATACONSUM", "TATASTEEL", "TCS", "TECHM", "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
]

# --------------------------------------------------------------
# DATA FETCHER (FINAL, CORRECTED)
# --------------------------------------------------------------
# Used in: pages/company.py
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_stock_data(tickers, period="10y"):

    if not tickers:
        return pd.DataFrame()

    # Ensure proper NSE symbols
    processed_tickers = sorted([
        t if t.endswith(".NS") or t.startswith("^") else f"{t}.NS"
        for t in tickers
    ])

    try:
        raw_data = yf.download(
            processed_tickers,
            period=period,
            progress=False,
            auto_adjust=True,   # 🔥 CRITICAL FIX
            threads=True
        )
    except Exception as e:
        print(f"Data Download Error: {e}")
        return pd.DataFrame()

    if raw_data.empty:
        return pd.DataFrame()

    # ----------------------------------------------------------
    # Use adjusted CLOSE prices (safe for indices + ETFs)
    # ----------------------------------------------------------
    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data["Close"]
    else:
        data = raw_data

    if isinstance(data, pd.Series):
        data = data.to_frame()

    # Clean missing data
    data = data.ffill().bfill()

    # Drop assets with insufficient history
    threshold = int(0.80 * len(data))
    data = data.dropna(axis=1, thresh=threshold)

    return data


# ==============================================================
# CENTRALIZED INDEX DATA (INDEX + ETF PROXY)
# ==============================================================
# NOTE:
# Yahoo Finance does NOT provide historical data for
# NIFTY NEXT 50, MIDCAP 100, SMALLCAP 100 indices.
# Hence ETF proxies are used ONLY where required.
# Used in: pages/index.py
ETF_INDEX_SYMBOLS = {
    # ✅ True index data (Yahoo supported)
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "NIFTY IT": "^CNXIT",

    # ⚠️ ETF proxies
    "NIFTY NEXT 50": "JUNIORBEES.NS",
    "NIFTY MIDCAP 100": "MIDCAPETF.NS",
    "NIFTY SMALLCAP 100": "SMALLCAP.NS"
}

# Optional metadata (for UI / explanation)
INDEX_DATA_SOURCE = {
    "NIFTY 50": "Index",
    "BANK NIFTY": "Index",
    "NIFTY IT": "Index",
    "NIFTY NEXT 50": "ETF Proxy",
    "NIFTY MIDCAP 100": "ETF Proxy",
    "NIFTY SMALLCAP 100": "ETF Proxy"
}

# ==============================================================
# EVERYTHING BELOW REMAINS UNCHANGED
# (MARKET_DATA dictionary is kept exactly as you had it)
# ==============================================================

# Used in: pages/sector.py
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