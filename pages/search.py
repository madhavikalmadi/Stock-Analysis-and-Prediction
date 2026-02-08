import streamlit as st
import yfinance as yf
import pandas as pd
import sys
import os

# --------------------------------------------------
# PATH & IMPORTS
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data_fetch
from mongo_db import actions_col, watchlist_col

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Stock Search", page_icon="🔍", layout="wide")

# --------------------------------------------------
# 🔐 RESTORE SESSION FROM URL (REFRESH SAFE)
# --------------------------------------------------
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# --------------------------------------------------
# SESSION STATE & PERSISTENCE
# --------------------------------------------------
# Sync back to URL if missing (allows refresh to work)
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

if user_id and username:
    # Ensure authenticated flag is set if we have valid session
    st.session_state.authenticated = True
    q = st.query_params
    if "user_id" not in q or "username" not in q:
        st.query_params["user_id"] = user_id
        st.query_params["username"] = username

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =============================================================
# CSS (KEEP YOUR ORIGINAL CSS HERE IF YOU WANT)
# =============================================================
st.markdown("""
<style>
.custom-top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: #eff6ff;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    display: flex;
    align-items: center;
    padding: 0 2rem;
    z-index: 999;
}
.custom-top-bar-title {
    font-weight: 800;
    font-size: 1.2rem;
    color: #1e3a8a;
}
.block-container {
    padding-top: 6rem !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# HEADER (SESSION-SAFE)
# =============================================================
st.markdown("""
<div class="custom-top-bar">
    <div class="custom-top-bar-title">Smart Investor Assistant</div>
</div>
""", unsafe_allow_html=True)



# --------------------------------------------------
# COMPANY NAME MAP
# --------------------------------------------------
from pages.search_data_map import STOCK_COMPANY_MAP

# --------------------------------------------------
# TICKER MAP
# --------------------------------------------------
TICKER_MAP = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
}

for t in data_fetch.BLUECHIP_TICKERS:
    clean = t.replace(".NS", "")
    TICKER_MAP[clean] = f"{clean}.NS"

for name, symbol in data_fetch.ETF_INDEX_SYMBOLS.items():
    TICKER_MAP[name.upper()] = symbol
    TICKER_MAP[name] = symbol

for sector, subcats in data_fetch.MARKET_DATA.items():
    for _, tickers in subcats.items():
        for t in tickers:
            clean = t.replace(".NS", "")
            TICKER_MAP[clean] = f"{clean}.NS"

# --------------------------------------------------
# DATA FETCH
# --------------------------------------------------
@st.cache_data(ttl=300)
def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d")

    if hist.empty:
        return None, "No data found."

    # Get latest row
    latest = hist.iloc[-1]
    price = latest["Close"]
    prev = hist["Close"].iloc[-2] if len(hist) > 1 else price
    change = ((price - prev) / prev) * 100 if prev != 0 else 0

    return {
        "ticker": symbol,
        "price": price,
        "change": change,
        "open": latest["Open"],
        "high": latest["High"],
        "low": latest["Low"],
        "volume": latest["Volume"]
    }, None

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_stock_categories(ticker):
    """Finds which sectors/indices a stock belongs to."""
    tags = []
    clean_ticker = ticker.replace(".NS", "")
    
    for sector, indices in data_fetch.MARKET_DATA.items():
        for index_name, stocks in indices.items():
            if clean_ticker in stocks:
                # Add Index Name (e.g., 'NIFTY Bank')
                tags.append(index_name)
    return list(set(tags))

# --------------------------------------------------
# WATCHLIST (MongoDB)
# --------------------------------------------------
def add_to_watchlist(ticker, bound_user_id=None):
    # Priority: Function Argument (Bound at render time) > Session State > Fallback
    user_id = bound_user_id or st.session_state.get("user_id")

    # Double Check if session was truly lost (Fall back to params)
    if not user_id:
        params = st.query_params
        if "user_id" in params:
            user_id = params["user_id"]
    
    if not user_id:
        # Debugging info to help diagnosis
        debug_info = f"Session: {st.session_state.get('user_id')}, Bound: {bound_user_id}, URL: {st.query_params.get('user_id')}"
        st.toast(f"⚠ Watchlist disabled (guest mode). Debug: {debug_info}")
        return

    # prevent duplicates
    exists = watchlist_col.find_one({
        "user_id": user_id,
        "ticker": ticker
    })

    if exists:
        st.toast("⭐ Already in watchlist")
        return

    watchlist_col.insert_one({
        "user_id": user_id,
        "ticker": ticker
    })

    st.toast(f"⭐ Saved {ticker}")

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🔍 Stock Search")

display_options = [
    f"{symbol} – {STOCK_COMPANY_MAP[symbol]}"
    for symbol in sorted(TICKER_MAP.keys())
    if symbol in STOCK_COMPANY_MAP
]

options = ["Select a Stock..."] + display_options

if "search_selection" not in st.session_state:
    st.session_state.search_selection = "Select a Stock..."

with st.form("stock_search_form"):
    selected = st.selectbox("Type to search Stock:", options=options)
    submitted = st.form_submit_button("🚀 Search")

# --------------------------------------------------
# ACTION
# --------------------------------------------------
if submitted:
    if selected == "Select a Stock...":
        st.warning("Please select a stock.")
    else:
        stock_symbol = selected.split(" – ")[0]
        st.session_state.search_query = stock_symbol

        if actions_col:
            actions_col.insert_one({
                "user_id": st.session_state.get("user_id"),
                "action": "search",
                "value": stock_symbol
            })
        else:
            # Optional: silent fail or debug toast
            st.toast("⚠ Activity logging unavailable", icon="⚠️")

# --------------------------------------------------
# DISPLAY RESULTS (PERSISTENT)
# --------------------------------------------------
if st.session_state.search_query:
    stock_symbol = st.session_state.search_query
    # Redo the fetch or display
    stock_data, error = fetch_stock_data(f"{stock_symbol}.NS")

    if stock_data:
        st.divider()
        
        # 1. HEADER & TAGS
        c_head, c_btn = st.columns([3, 1])
        with c_head:
            st.markdown(f"### {stock_symbol} <span style='font-size:0.8em; color:gray;'>{STOCK_COMPANY_MAP.get(stock_symbol, '')}</span>", unsafe_allow_html=True)
            
            # Display Categories as Tags
            tags = get_stock_categories(stock_symbol)
            if tags:
                # Simple badge styling
                badges = "".join([f"<span style='background:#e0f2fe; color:#0369a1; padding:4px 8px; border-radius:12px; font-size:0.75rem; margin-right:5px; font-weight:600;'>{t}</span>" for t in tags])
                st.markdown(badges, unsafe_allow_html=True)
                st.write("") # Spacer

        with c_btn:
             # Use a callback-independent check for user_id to ensure button state
            uid = st.session_state.get("user_id") or st.query_params.get("user_id")
            
            st.button(
                "⭐ Add to Watchlist",
                on_click=add_to_watchlist,
                args=(stock_symbol, uid)
            )

        # 2. METRICS GRID
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        
        with m1: st.metric("Current Price", f"₹ {stock_data['price']:.2f}", f"{stock_data['change']:+.2f}%")
        with m2: st.metric("Open", f"₹ {stock_data['open']:.2f}")
        with m3: st.metric("Day High", f"₹ {stock_data['high']:.2f}")
        with m4: st.metric("Day Low", f"₹ {stock_data['low']:.2f}")

        # Optional: Secondary metrics row if needed, e.g. Volume
        # vol_str = f"{stock_data['volume']:,}"
        # st.caption(f"Volume: {vol_str}")

    else:
        st.error(error)

# --------------------------------------------------
# FOOTER & NAVIGATION
# --------------------------------------------------
# Custom Button Style (from bluechip.py/profile.py)
st.markdown("""
<style>
div.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}
div.stButton > button {
    padding: 0.4rem 1rem !important; 
    font-size: 0.8rem !important; 
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important; 
    box-shadow: none !important; 
    width: auto !important; 
    margin: 0 auto !important;
    white-space: nowrap !important;
    color: white !important;
    display: block !important;
}
div.stButton > button:hover { 
    background: #2563eb !important; 
    transform: translateY(-2px); 
}
</style>
""", unsafe_allow_html=True)

# Footer Layout (Centered via CSS)
if st.button("⬅ Back to Dashboard", key="btn_search_back"):
    # Preserve session state in query params
    if "user_id" in st.session_state:
        st.query_params["user_id"] = st.session_state.user_id
    if "username" in st.session_state:
        st.query_params["username"] = st.session_state.username
    st.switch_page("pages/dashboard.py")

st.write("---")

st.markdown("""
<div style="margin-top: 10px; margin-bottom: 20px;">
    <center style="opacity:0.6; font-size:0.85rem;">
        Smart Investor Assistant 
    </center>
</div>
""", unsafe_allow_html=True)