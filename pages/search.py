import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stock Search", page_icon="🔍", layout="wide")

# =============================================================
# CSS STYLING (MATCHES PROFILE PAGE DASHBOARD)
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');

/* Hide default Streamlit elements */
[data-testid="stSidebar"],
.stAppDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer {
    display: none !important;
}

/* Global Font */
body {
    font-family: 'Outfit', sans-serif !important;
}

/* Custom Search Input */
[data-testid="stTextInput"] > div > div > input {
    font-size: 1.2rem;
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #3b82f6;
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.1);
}

/* Save Button */
div.stButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 700;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    width: auto !important;
}

/* Cache clear button */
.stClearButton > button {
    width: auto !important;
    background: #fef08a !important;
    color: #a16207 !important;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    border: 1px solid #fde047;
}

/* ================================
   WHITE DASHBOARD BUTTON (PROFILE STYLE)
   ================================ */
div.stButton:last-of-type > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;

    background: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #e5e7eb !important;

    box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
    width: auto !important;
    margin: 0 auto;
    white-space: nowrap !important;
}

div.stButton:last-of-type > button:hover {
    background: #f8fafc !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# SESSION STATE
# =============================================================
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

# =============================================================
# TICKER MAP
# =============================================================
TICKER_MAP = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "INFOSYS": "INFY",
    "HDFC BANK": "HDFCBANK",
    "TATA STEEL": "TATASTEEL",
    "TATA MOTORS": "TATAMOTORS",
    "RELIANCE INDUSTRIES": "RELIANCE",
    "HUL": "HINDUNILVR",
}

# =============================================================
# DATA FETCH
# =============================================================
@st.cache_data(ttl=300, show_spinner="Fetching stock data...")
def fetch_stock_data(ticker_input):
    if not ticker_input:
        return None, "No input provided."

    ticker_upper = ticker_input.upper().strip()
    base_ticker = TICKER_MAP.get(ticker_upper, ticker_upper)
    possible_tickers = [base_ticker]

    if not any(s in base_ticker for s in [".NS", ".BO", "^"]):
        possible_tickers.extend([f"{base_ticker}.NS", f"{base_ticker}.BO"])

    for ticker in possible_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="2d")

            if history.empty:
                continue

            current_price = history["Close"].iloc[-1]
            prev_close = history["Close"].iloc[-2] if len(history) > 1 else current_price
            change_percent = ((current_price - prev_close) / prev_close) * 100

            return {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "price": current_price,
                "change_percent": change_percent,
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
            }, None

        except Exception:
            continue

    return None, f"Could not find valid stock data for '{ticker_input}'."

def add_to_watchlist(ticker):
    if ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)
        st.toast(f"✅ Added {ticker} to watchlist")

def clear_fetch_cache():
    st.cache_data.clear()
    st.toast("Cache cleared")

# =============================================================
# MAIN UI
# =============================================================
st.markdown("<h1 style='color:#2563eb;'>🔍 Stock Search</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- UPDATED SEARCH INPUT ---
search_input = st.text_input(
    "Enter Stock Ticker or Symbol",
    placeholder="Type symbol and press Enter to search...",
    value=st.session_state.search_query,
)

if search_input:
    st.session_state.search_query = search_input
    stock_data, error = fetch_stock_data(search_input)

    if stock_data:
        st.markdown(f"### {stock_data['name']} ({stock_data['ticker']})")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if stock_data["ticker"] not in st.session_state.watchlist:
                st.button(
                    "⭐ SAVE",
                    on_click=add_to_watchlist,
                    args=(stock_data["ticker"],),
                    use_container_width=True,
                )
            else:
                st.button("⭐ SAVED", disabled=True, use_container_width=True)

        with col2:
            st.metric(
                "Price",
                f"₹ {stock_data['price']:,.2f}",
                f"{stock_data['change_percent']:+.2f}%",
            )

        with col3:
            st.metric("Sector", stock_data["sector"])

        with col4:
            cap = stock_data["market_cap"]
            cap_display = f"₹ {cap:,}" if isinstance(cap, (int, float)) else "N/A"
            st.metric("Market Cap", cap_display)

    else:
        st.error(error)

# =============================================================
# BOTTOM NAV
# =============================================================
st.write("")
st.write("---")

col1, col2, col3 = st.columns([5, 2, 5])

with col1:
    st.button("🔄 Fetch Live Prices", on_click=clear_fetch_cache)

with col2:
    if st.button("⬅ Dashboard", key="btn_dashboard_nav"):
        st.switch_page("app.py")

# =============================================================
# FOOTER
# =============================================================
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>"
    "Smart Investor Assistant • Data provided by Yahoo Finance"
    "</div>",
    unsafe_allow_html=True,
)
