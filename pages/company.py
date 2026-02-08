import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Company Advisor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# 🔁 RESTORE SESSION FROM URL (ONLY RESTORE)
# ==================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# ❌ NO LOGIN REDIRECT HERE
# Dashboard is the auth gate

# --------------------------------------------------
# 🔄 PERSIST SESSION
# --------------------------------------------------
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ==================================================
# GLOBAL CSS (SAME AS DASHBOARD / BLUECHIP / SECTOR)
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Hide sidebar */
[data-testid="stSidebar"] { display: none !important; }

/* BACKGROUND */
body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%) !important;
    color: #1e293b !important;
}

/* Layout */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px;
}

/* INPUT CARDS */
.input-box {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(14px);
    padding: 25px;
    border-radius: 20px;
    border: 2px solid #2563eb;
    margin-bottom: 20px;
}

/* RESULT CARDS */
.stock-card {
    background-color: white;
    padding: 20px;
    border-radius: 16px;
    border-top: 5px solid #2563eb;
    box-shadow: 0 8px 25px rgba(0,0,0,0.07);
    margin-bottom: 15px;
}

/* PRIMARY BUTTONS */
div.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.25s ease-in-out !important;
    white-space: nowrap !important;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
}

/* FOOTER BUTTONS */
div.stButton:last-of-type > button {
    background: rgba(24, 40, 72, 0.85) !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;
    padding: 0.4rem 1.1rem !important;
    box-shadow: none !important;
}
div.stButton:last-of-type > button:hover {
    background: #2563eb !important;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HELPERS
# ==================================================
def resolve_ticker(user_input):
    clean = user_input.lower().strip()
    if clean in data_fetch.SEARCH_SHORTCUTS:
        return data_fetch.SEARCH_SHORTCUTS[clean]
    return user_input.upper()

def get_recommendation_text(cagr, sharpe):
    if sharpe > 0.5 and cagr > 0.12:
        return ("✅ Strong Buy", "Steady Growth")
    elif sharpe > 0.3 and cagr > 0.08:
        return ("⚠️ Moderate", "Higher Risk")
    else:
        return ("❌ Avoid", "Inconsistent History")

def run_analysis(tickers):
    market = "NIFTYBEES.NS"
    tickers = list(set(tickers + [market]))

    df = data_fetch.fetch_stock_data(tickers)
    if df.empty:
        return pd.DataFrame()

    metrics = metric_calculator.compute_metrics(df, market)
    ranked = scoring_system.rank_stocks(metrics)
    return ranked[ranked["Ticker"] != market]

# ==================================================
# MAIN UI
# ==================================================
st.markdown("<h1 style='text-align:center;'>🏢 Company Advisor</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2, gap="large")

# ---------------- SINGLE COMPANY ----------------
with col1:
    st.markdown("<div class='input-box'><b>🔍 Single Company Analysis</b></div>", unsafe_allow_html=True)
    ticker = st.text_input("Ticker")
    amount = st.number_input("Investment Amount ₹", value=None, placeholder="Optional")
    years = st.slider("Investment Horizon (Years)", 1, 20, 1)

    if st.button("🚀 Analyze Company"):
        if ticker.strip():
            t = resolve_ticker(ticker)
            result = run_analysis([t])

            if result.empty:
                st.error("No data found for this company.")
            else:
                row = result.iloc[0]
                reco, desc = get_recommendation_text(row.CAGR, row.Sharpe)
                st.success(f"{reco} — {desc}")
                st.metric("CAGR", f"{row.CAGR*100:.2f}%")
                st.metric("Sharpe Ratio", f"{row.Sharpe:.2f}")
                st.metric("Risk Score", f"{row.FinalScore*100:.1f}/100")

# ---------------- MULTI COMPANY ----------------
with col2:
    st.markdown("<div class='input-box'><b>⚖️ Compare Companies</b></div>", unsafe_allow_html=True)
    tickers = st.text_area("Comma-separated tickers (e.g. TCS, INFY, RELIANCE)")
    years_m = st.slider("Investment Horizon (Years)", 1, 20, 1, key="multi")

    if st.button("📊 Compare Companies"):
        lst = [resolve_ticker(t.strip()) for t in tickers.split(",") if t.strip()]
        if len(lst) < 2:
            st.warning("Please enter at least 2 companies.")
        else:
            ranked = run_analysis(lst)
            st.dataframe(
                ranked[["Ticker", "FinalScore", "CAGR", "Sharpe"]]
                .sort_values("FinalScore", ascending=False),
                use_container_width=True
            )

# ==================================================
# FOOTER NAVIGATION
# ==================================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back"):
        st.switch_page("pages/reinvestor.py")

with c_dash:
    if st.button("⬅ Dashboard"):
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")
