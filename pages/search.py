import streamlit as st
import yfinance as yf
import pandas as pd
import sys
import os

# --------------------------------------------------
# PATH & IMPORTS
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth_utils
from db import execute
import data_fetch

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Stock Search", page_icon="🔍", layout="wide")

# --------------------------------------------------
# AUTH CHECK (Non-blocking as requested)
# --------------------------------------------------
auth_utils.check_auth() # Attempt to restore session if token exists
# if not auth_utils.check_auth():
#     st.warning("You must log in to access this page.")
#     st.switch_page("login.py")

# --------------------------------------------------
# NAVIGATION CONTROLLER
# --------------------------------------------------
if "page" in st.query_params:
    page_name = st.query_params["page"]
    if page_name == "profile":
        st.switch_page("pages/profile.py") 
    elif page_name == "search":
        st.switch_page("pages/search.py")
    elif page_name == "beginner":
        st.switch_page("pages/beginner.py")
    elif page_name == "reinvestor":
        st.switch_page("pages/reinvestor.py")
    elif page_name == "dashboard":
        st.switch_page("pages/dashboard.py")
    st.query_params.clear()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =============================================================
# CSS ENGINE (COPIED FROM DASHBOARD)
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

/* Hide sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Global font */
body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    overflow-x: hidden;
}

/* Hide deploy button, menu, spinners */
.stAppDeployButton { display: none !important; }
#MainMenu, footer { visibility: hidden; height: 0; }
[data-testid*="stProgress"],
[data-testid*="stSpinner"],
.stAlert:has(.stSpinner) { display: none !important; }

/* Hide native Streamlit header */
[data-testid="stHeader"] {
    display: none !important;
    visibility: hidden;
    height: 0;
}

/* REMOVE HEADER ANCHORS */
[data-testid="stMarkdownContainer"] h1 a,
[data-testid="stMarkdownContainer"] h2 a,
[data-testid="stMarkdownContainer"] h3 a,
[data-testid="stMarkdownContainer"] h4 a,
[data-testid="stMarkdownContainer"] h5 a,
[data-testid="stMarkdownContainer"] h6 a {
    display: none !important;
}

/* ==== CUSTOM FIXED HEADER BAR ==== */
.custom-top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px; /* Taller header */
    background: #eff6ff; /* Light Blue Color */
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    display: flex;
    align-items: center; /* Ensures vertical centering */
    padding: 0 2rem; 
    z-index: 99990;
}
.custom-top-bar-title {
    font-weight: 800;
    font-size: 1.2rem;
    color: #1e3a8a;
    margin: 0 !important; 
}

/* Container for search and profile buttons */
.nav-buttons-container {
    margin-left: auto; /* Push buttons to the right */
    display: flex; 
    align-items: center;
    gap: 10px; /* Space between search and profile buttons */
    height: 100%; 
}

/* ===== SEARCH ICON STYLES (HTML Anchor) ===== */
.search-btn-style {
    background: none;
    color: #1e3a8a !important;
    padding: 0.5rem 0.8rem; 
    border-radius: 999px;
    font-size: 1.1rem;
    border: 2px solid #3b82f6; /* Subtle blue border */
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    text-decoration: none !important; 
    display: inline-block; 
}
.search-btn-style:hover {
    background: #dbeafe; /* Very light blue background on hover */
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2);
}

/* ===== PROFILE BUTTON STYLES (PURE HTML ANCHOR STYLES) ===== */
.profile-btn-style {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
    padding: 0.5rem 1.2rem; 
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    border: none;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    transition: all 0.3s ease;
    text-decoration: none !important; 
    white-space: nowrap;
    /* animation: pulse 2s infinite; REMOVED */
    display: inline-block; 
}

.profile-btn-style:hover {
    transform: translateY(-2px); 
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

/* Main container (push content below custom bar) */
.block-container {
    padding-top: 6rem !important; /* Increased space for the taller header */
    padding-bottom: 5rem !important;
    max-width: 1200px;
    position: relative;
    z-index: 1;
}

/* ANIMATED CLOUD BACKGROUND */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.8), transparent 50%),
        radial-gradient(circle at 80% 30%, rgba(219, 234, 254, 0.8), transparent 50%);
    filter: blur(60px);
    z-index: 0;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# CUSTOM FIXED HEADER BAR
# =============================================================
session_token = st.query_params.get("session", "")

st.markdown(f"""
<div class="custom-top-bar">
    <div class="custom-top-bar-title">Smart Investor Assistant</div>
    <div class="nav-buttons-container">
        <a href="?page=search&session={session_token}" target="_self" class="search-btn-style">
            🔍
        </a>
        <a href="?page=profile&session={session_token}" target="_self" class="profile-btn-style">
            👤 My Profile
        </a>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# COMPANY NAME MAP (Imported from generated file)
# --------------------------------------------------
from pages.search_data_map import STOCK_COMPANY_MAP

# --------------------------------------------------
# TICKER MAP (INDICES + STOCKS)
# --------------------------------------------------
TICKER_MAP = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
}

# Bluechips
for t in data_fetch.BLUECHIP_TICKERS:
    clean = t.replace(".NS", "")
    TICKER_MAP[clean] = f"{clean}.NS"

# ETFs / indices
for name, symbol in data_fetch.ETF_INDEX_SYMBOLS.items():
    TICKER_MAP[name.upper()] = symbol
    TICKER_MAP[name] = symbol

# Sector stocks
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

    price = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[-2] if len(hist) > 1 else price
    change = ((price - prev) / prev) * 100 if prev != 0 else 0

    return {
        "ticker": symbol,
        "price": price,
        "change": change
    }, None

# --------------------------------------------------
# WATCHLIST
# --------------------------------------------------
def add_to_watchlist(ticker):
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.toast("⚠ Not logged in. Watchlist saving disabled.")
        return

    if ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)
        execute(
            "INSERT INTO user_actions (user_id, action, value) VALUES (:u, 'save', :v)",
            {"u": user_id, "v": ticker},
        )
        st.toast(f"⭐ Saved {ticker}")

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🔍 Stock Search")

# Build dropdown options
display_options = []
for symbol in sorted(TICKER_MAP.keys()):
    if symbol in STOCK_COMPANY_MAP:
        display_options.append(f"{symbol} – {STOCK_COMPANY_MAP[symbol]}")

options = ["Select a Stock..."] + display_options

if "search_selection" not in st.session_state:
    st.session_state.search_selection = "Select a Stock..."

with st.form("stock_search_form"):
    selected = st.selectbox(
        "Type to search Stock:",
        options=options,
        key="search_selection",
    )
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

        execute(
            "INSERT INTO user_actions (user_id, action, value) VALUES (:u, 'search', :v)",
            {"u": st.session_state.get("user_id"), "v": stock_symbol},
        )

        stock_data, error = fetch_stock_data(f"{stock_symbol}.NS")

        if stock_data:
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.metric(
                    label=f"{stock_symbol}",
                    value=f"₹ {stock_data['price']:.2f}",
                    delta=f"{stock_data['change']:+.2f}%"
                )
                st.caption(STOCK_COMPANY_MAP.get(stock_symbol))
                st.button(
                    "⭐ Add to Watchlist",
                    on_click=add_to_watchlist,
                    args=(stock_symbol,)
                )
        else:
            st.error(error)
