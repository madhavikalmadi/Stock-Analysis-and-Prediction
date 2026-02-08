import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system
import sys
import os

# Add parent directory to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Company Advisor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (SOURCE OF TRUTH)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔄 PERSIST SESSION (VERY IMPORTANT)
# =====================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already guarantees authentication

# ==========================================
# GLOBAL CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
[data-testid="stSidebar"] { display: none; }

body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%);
    font-family: 'Outfit', sans-serif !important;
    color: #1e293b !important;
}

.input-box {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(14px);
    padding: 25px;
    border-radius: 20px;
    border: 2px solid #2563eb;
    margin-bottom: 20px;
}

.stock-card {
    background-color: white;
    padding: 20px;
    border-radius: 16px;
    border-top: 5px solid #2563eb;
    box-shadow: 0 8px 25px rgba(0,0,0,0.07);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPERS
# ==========================================
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

# ==========================================
# MAIN UI
# ==========================================
st.markdown("<h1 style='text-align:center;'>🏢 Company Advisor</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

# ---------------- SINGLE COMPANY ----------------
with col1:
    st.markdown("<div class='input-box'><b>🔍 Single Company</b></div>", unsafe_allow_html=True)
    ticker = st.text_input("Ticker")
    amount = st.number_input("Investment Amount ₹", value=None, placeholder="Optional")
    years = st.slider("Years", 1, 20, 1)

    if st.button("🚀 Analyze"):
        if ticker.strip():
            t = resolve_ticker(ticker)
            result = run_analysis([t])
            if result.empty:
                st.error("No data found")
            else:
                row = result.iloc[0]
                reco, desc = get_recommendation_text(row.CAGR, row.Sharpe)
                st.success(f"{reco} — {desc}")

# ---------------- MULTI COMPANY ----------------
with col2:
    st.markdown("<div class='input-box'><b>⚖️ Compare Companies</b></div>", unsafe_allow_html=True)
    tickers = st.text_area("Comma separated tickers")
    years_m = st.slider("Years ", 1, 20, 1, key="multi")

    if st.button("📊 Compare"):
        lst = [resolve_ticker(t.strip()) for t in tickers.split(",") if t.strip()]
        if len(lst) < 2:
            st.warning("Enter at least 2 companies")
        else:
            ranked = run_analysis(lst)
            st.dataframe(ranked[["Ticker", "FinalScore", "CAGR", "Sharpe"]])

# ==========================================
# FOOTER NAVIGATION
# ==========================================
st.write("---")
c1, _, c2 = st.columns([1,4,1])

with c1:
    if st.button("⬅ Back"):
        st.switch_page("pages/reinvestor.py")

with c2:
    if st.button("⬅ Dashboard"):
        st.switch_page("pages/dashboard.py")
