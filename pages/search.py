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
import metric_calculator
from mongo_db import actions_col, watchlist_col

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Stock Search", page_icon="🔍", layout="wide")

# =====================================================
# 🔁 RESTORE SESSION FROM URL (SOURCE OF TRUTH)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔄 PERSIST SESSION BACK TO URL (VERY IMPORTANT)
# =====================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already guarantees authentication

# =====================================================
# SESSION DEFAULTS
# =====================================================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""
# =============================================================
# CSS
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
div.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
div.stButton > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important;
    color: white !important;
    border: none !important;
}
div.stButton > button * {
    color: white !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# HEADER
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
# RECOMMENDATION LOGIC (COPIED FROM COMPANY.PY)
# --------------------------------------------------
def get_recommendation_text(cagr, sharpe):
    if sharpe > 0.5 and cagr > 0.12:
        return {
            "verdict": "✅ Strong Buy",
            "reason": "This stock shows high growth power and stays very steady over time.",
            "color": "#059669", 
            "bg": "#ecfdf5"
        }
    elif sharpe > 0.3 and cagr > 0.08:
        return {
            "verdict": "⚠️ Moderate",
            "reason": "It has good growth speed, but the upward path can be a bit bumpy.",
            "color": "#b45309", 
            "bg": "#fffbeb"
        }
    else:
        if cagr < 0.08:
            reason = "The growth speed is too slow to significantly increase your wealth."
        elif sharpe <= 0.3:
            reason = "The growth is very inconsistent, making the stock quite risky."
        else:
            reason = "The upward growth hasn't been reliable enough to trust it fully."
        return {
            "verdict": "❌ Avoid",
            "reason": reason,
            "color": "#dc2626", 
            "bg": "#fef2f2"
        }

# --------------------------------------------------
# DATA FETCH
# --------------------------------------------------
@st.cache_data(ttl=300)
def fetch_stock_data(symbol):
    # Fetch 10y data for long-term metrics
    full_data = data_fetch.fetch_stock_data([symbol, "^NSEI"])
    if full_data.empty:
        return None, "No data found."

    metrics = metric_calculator.compute_metrics(full_data, "^NSEI")
    if metrics.empty:
        return None, "Could not compute metrics."
    
    row = metrics[metrics["Ticker"] == symbol].iloc[0]
    
    # --- Robust price fetch (3-tier priority) ---
    # 1. ticker.info (live during market hours)
    # 2. regularMarketPrice (near-real-time fallback)
    # 3. 5d history last Close (works when market is closed / holidays)
    stock_ticker = yf.Ticker(symbol)

    price = None
    change = 0.0
    open_p = high_p = low_p = None
    volume = 0

    try:
        info  = stock_ticker.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price:
            price = float(price)
    except Exception:
        price = None

    # Fallback: 5-day history
    hist = stock_ticker.history(period="5d")
    if not hist.empty:
        hist = hist.dropna(subset=["Close"])
        if not hist.empty:
            latest = hist.iloc[-1]
            hist_price = float(latest["Close"])

            # Only override if info gave nothing
            if not price:
                price = hist_price

            prev   = float(hist["Close"].iloc[-2]) if len(hist) > 1 else hist_price
            change = ((hist_price - prev) / prev) * 100 if prev else 0.0
            open_p = float(latest["Open"])   if "Open"   in latest else None
            high_p = float(latest["High"])   if "High"   in latest else None
            low_p  = float(latest["Low"])    if "Low"    in latest else None
            volume = int(latest["Volume"])   if "Volume" in latest else 0

    return {
        "ticker": symbol,
        "price":  price,
        "change": change,
        "open":   open_p,
        "high":   high_p,
        "low":    low_p,
        "volume": volume,
        "cagr":   row["CAGR"],
        "sharpe": row["Sharpe"]
    }, None

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_stock_categories(ticker):
    tags = []
    clean = ticker.replace(".NS", "")
    for sector, indices in data_fetch.MARKET_DATA.items():
        for index_name, stocks in indices.items():
            if clean in stocks:
                tags.append(index_name)
    return list(set(tags))

# --------------------------------------------------
# WATCHLIST (MongoDB SAFE)
# --------------------------------------------------
def add_to_watchlist(ticker, bound_user_id=None):
    user_id = bound_user_id or st.session_state.get("user_id")

    if not user_id:
        user_id = st.query_params.get("user_id")

    if not user_id:
        st.toast("⚠ Login required to use watchlist")
        return

    # Check if already in watchlist (MongoDB)
    if watchlist_col.find_one({"user_id": user_id, "ticker": ticker}):
        st.toast("⭐ Already in watchlist")
        return

    # Save to MongoDB
    watchlist_col.insert_one({
        "user_id": user_id,
        "ticker": ticker
    })

    # 🔥 Also update session state so UI refreshes correctly
    if ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)

    st.toast(f"✅ Added {ticker} to Watchlist")

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

with st.form("stock_search_form"):
    selected = st.selectbox("Type to search Stock:", options=options)
    submitted = st.form_submit_button("🚀 Search")

# --------------------------------------------------
# ACTION
# --------------------------------------------------
if submitted:
    if selected != "Select a Stock...":
        stock_symbol = selected.split(" – ")[0]
        st.session_state.search_query = stock_symbol

        if actions_col is not None:
            actions_col.insert_one({
                "user_id": st.session_state.get("user_id"),
                "action": "search",
                "value": stock_symbol
            })

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------
if st.session_state.search_query:
    stock_symbol = st.session_state.search_query
    stock_data, error = fetch_stock_data(f"{stock_symbol}.NS")

    if stock_data:
        st.divider()

        c_head, c_btn = st.columns([3, 1])
        with c_head:
            st.markdown(
                f"### {stock_symbol} <span style='font-size:0.8em; color:gray;'>"
                f"{STOCK_COMPANY_MAP.get(stock_symbol,'')}</span>",
                unsafe_allow_html=True
            )

            tags = get_stock_categories(stock_symbol)
            if tags:
                badges = "".join([
                    f"<span style='background:#e0f2fe; padding:4px 8px; border-radius:12px; font-size:0.75rem; margin-right:5px;'>{t}</span>"
                    for t in tags
                ])
                st.markdown(badges, unsafe_allow_html=True)

        with c_btn:
            uid = st.session_state.get("user_id")
            st.button("⭐ Add to Watchlist", on_click=add_to_watchlist, args=(stock_symbol, uid))

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            if stock_data['price'] is not None:
                st.metric("Price", f"₹ {stock_data['price']:.2f}", f"{stock_data['change']:+.2f}%")
            else:
                st.warning("Price not available (Market Closed / No Data)")
        with m2: st.metric("Yearly Growth", f"{stock_data['cagr']*100:.1f}%")
        with m3: st.metric("Efficiency", f"{stock_data['sharpe']:.2f}")
        with m4: st.metric("Volume", f"{stock_data['volume']:,.0f}")

        # GROWTH VERDICT BOX
        res = get_recommendation_text(stock_data['cagr'], stock_data['sharpe'])
        st.markdown(f"""
<div style="margin-top:25px; background:{res['bg']}; color:{res['color']}; padding:20px; border-radius:15px; border: 1px solid {res['color']}33; text-align:center;">
    <div style="font-weight:800; font-size:1.2rem; margin-bottom:8px;">Growth Verdict: {res['verdict']}</div>
    <div style="font-size:1rem; font-weight:600; opacity:0.9; line-height:1.4;">{res['reason']}</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.error(error)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
if st.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")
