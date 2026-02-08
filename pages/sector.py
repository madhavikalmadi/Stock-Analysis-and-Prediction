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
# CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');

    body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #ffffff !important;
    }

    [data-testid="stSidebar"] { display: none; }

    .main-title { text-align: center; animation: slideInDown 0.8s ease-out; }
    .sub-title { text-align: center; color: #555; margin-bottom: 20px; }

    .section-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #333;
        margin-top: 30px;
        margin-bottom: 10px;
        border-bottom: 2px solid #ddd;
        padding-bottom: 5px;
    }

    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div.stButton > button {
        background-color: #1e293b;
        color: white;
        border-radius: 8px;
        height: 3rem;
        width: 100%;
        font-weight: 600;
        margin-top: 28px;
    }

    .stock-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border-top: 5px solid #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .stock-rank { font-size: 1.4rem; font-weight: 800; color: #1e293b; }

    .big-score {
        font-size: 2.2rem;
        font-weight: 800;
        color: #4CAF50;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        padding-top: 15px;
        border-top: 1px solid #f1f5f9;
    }

    .metric-label { font-size: 0.8rem; font-weight: 700; color: #64748b; }
    .metric-val { font-size: 1rem; font-weight: 600; color: #334155; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MARKET DATA
# ==========================================
MARKET_DATA = data_fetch.MARKET_DATA

# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown('<h1 class="main-title">🏗️ NSE Sector & Thematic Advisor</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Select a category to explore top performing stocks.</h3>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
start_analysis = False

with c1:
    cat_options = ["SELECT CATEGORY..."] + list(MARKET_DATA.keys())
    selected_category = st.selectbox("1️⃣ Market Category", cat_options)

target_indices = []

with c2:
    if selected_category != "SELECT CATEGORY...":
        index_options = ["SELECT INDEX...", "Analyze Entire Category"] + list(MARKET_DATA[selected_category].keys())
        selected_index = st.selectbox("2️⃣ Specific Index", index_options)

        if selected_index == "Analyze Entire Category":
            for name, tickers in MARKET_DATA[selected_category].items():
                target_indices.append((selected_category, name, tickers))
        elif selected_index != "SELECT INDEX...":
            target_indices.append((selected_category, selected_index, MARKET_DATA[selected_category][selected_index]))

        if target_indices:
            start_analysis = st.button("🚀 Analyze Performance")

# ==========================================
# ANALYSIS
# ==========================================
if start_analysis:
    st.write("---")
    progress = st.progress(0)

    for i, (cat, idx_name, tickers) in enumerate(target_indices):
        st.markdown(f"### 🔎 {idx_name}")

        with st.spinner(f"Analyzing {idx_name}..."):
            market_ticker = "NIFTYBEES.NS"
            data = data_fetch.fetch_stock_data(tickers + [market_ticker])

            if not data.empty:
                metrics = metric_calculator.compute_metrics(data, market_ticker)
                ranked = scoring_system.rank_stocks(metrics)
                top5 = ranked[ranked["Ticker"] != market_ticker].head(5)

                cols = st.columns(len(top5))
                for j, (_, row) in enumerate(top5.iterrows()):
                    with cols[j]:
                        ticker = row["Ticker"].replace(".NS", "")
                        score = row["FinalScore"] * 100

                        st.markdown(f"""
                        <div class="stock-card">
                            <div class="stock-rank">#{j+1} {ticker}</div>
                            <div class="big-score">{score:.1f}/100</div>
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
# FOOTER
# ==========================================
st.markdown("---")
c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Menu", key="btn_sector_back"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_sector_dashboard"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")
