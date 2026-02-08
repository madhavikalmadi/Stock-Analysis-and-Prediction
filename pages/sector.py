import streamlit as st
import pandas as pd
import numpy as np
import time

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system

import sys
import os

# Add parent directory to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth_utils

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="NSE Sector & Thematic Advisor",
    page_icon="📈",
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
# 🔄 PERSIST SESSION BACK TO URL (VERY IMPORTANT)
# =====================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already enforces authentication

# ==========================================
# GLOBAL CSS (SAME AS DASHBOARD)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Hide sidebar */
[data-testid="stSidebar"] { display: none !important; }

/* GLOBAL BACKGROUND */
body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%) !important;
    color: #1e293b;
}

/* Main container */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px;
}

/* TITLES */
.main-title {
    text-align: center;
    animation: slideInDown 0.8s ease-out;
}
.sub-title {
    text-align: center;
    color: #475569;
    margin-bottom: 20px;
}

@keyframes slideInDown {
    from { opacity: 0; transform: translateY(-40px); }
    to { opacity: 1; transform: translateY(0); }
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

/* FOOTER BUTTON */
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

/* STOCK CARD */
.stock-card {
    background-color: white;
    padding: 24px;
    border-radius: 16px;
    border-top: 5px solid #22c55e;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    animation: fadeUp 0.6s ease-out;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stock-rank {
    font-size: 1.4rem;
    font-weight: 800;
    color: #1e293b;
}

.big-score {
    font-size: 2.2rem;
    font-weight: 800;
    color: #16a34a;
}

.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    padding-top: 15px;
    border-top: 1px solid #e5e7eb;
}

.metric-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748b;
}
.metric-val {
    font-size: 1rem;
    font-weight: 600;
    color: #334155;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# MARKET DATA
# ==========================================
MARKET_DATA = data_fetch.MARKET_DATA

# ==========================================
# MAIN UI
# ==========================================
st.markdown('<h1 class="main-title">🏗️ NSE Sector & Thematic Advisor</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Select a category to explore top performing stocks</h3>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
start_analysis = False

with c1:
    selected_category = st.selectbox(
        "1️⃣ Market Category",
        ["SELECT CATEGORY..."] + list(MARKET_DATA.keys())
    )

target_indices = []

with c2:
    if selected_category != "SELECT CATEGORY...":
        selected_index = st.selectbox(
            "2️⃣ Specific Index",
            ["SELECT INDEX...", "Analyze Entire Category"] + list(MARKET_DATA[selected_category].keys())
        )

        if selected_index == "Analyze Entire Category":
            for name, tickers in MARKET_DATA[selected_category].items():
                target_indices.append((name, tickers))
        elif selected_index != "SELECT INDEX...":
            target_indices.append((selected_index, MARKET_DATA[selected_category][selected_index]))

        if target_indices:
            start_analysis = st.button("🚀 Analyze Performance")

# ==========================================
# ANALYSIS
# ==========================================
if start_analysis:
    st.write("---")
    progress = st.progress(0)

    for i, (idx_name, tickers) in enumerate(target_indices):
        st.markdown(f"### 🔎 {idx_name}")

        with st.spinner("Analyzing stocks..."):
            market_ticker = "NIFTYBEES.NS"
            data = data_fetch.fetch_stock_data(tickers + [market_ticker])

            if not data.empty:
                metrics = metric_calculator.compute_metrics(data, market_ticker)
                ranked = scoring_system.rank_stocks(metrics)
                top5 = ranked[ranked["Ticker"] != market_ticker].head(5)

                cols = st.columns(len(top5))
                for j, (_, row) in enumerate(top5.iterrows()):
                    with cols[j]:
                        st.markdown(f"""
                        <div class="stock-card">
                            <div class="stock-rank">#{j+1} {row['Ticker'].replace('.NS','')}</div>
                            <div class="big-score">{row['FinalScore']*100:.1f}/100</div>
                            <div class="metrics-grid">
                                <div><span class="metric-label">CAGR</span><div class="metric-val">{row['CAGR']*100:.1f}%</div></div>
                                <div><span class="metric-label">Sharpe</span><div class="metric-val">{row['Sharpe']:.2f}</div></div>
                                <div><span class="metric-label">Volatility</span><div class="metric-val">{row['Volatility']*100:.1f}%</div></div>
                                <div><span class="metric-label">Max DD</span><div class="metric-val">{row['MaxDrawdown']*100:.1f}%</div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        progress.progress((i + 1) / len(target_indices))

    progress.empty()
    st.success(f"✅ Analysis Complete for {selected_category}")

# ==========================================
# FOOTER NAV
# ==========================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard"):
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")
