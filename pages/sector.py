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
.stock-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border-top: 5px solid #22c55e;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.big { font-size: 2rem; font-weight: 800; color:#16a34a; }
.small { color:#64748b; font-size:0.8rem; }
.metric { font-weight:700; }

div.stButton > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.85rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.85) !important;
    color: white !important;
    white-space: nowrap !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}

/* Standardize Selectbox and Info Box heights */
[data-testid="stSelectbox"] > div, 
[data-testid="stAlert"] {
    min-height: 45px !important;
}

/* Ensure the info box content is centered and fits nicely */
[data-testid="stAlert"] > div {
    padding-top: 5px !important;
    padding-bottom: 5px !important;
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
            start_analysis = st.button("🚀 Analyze Performance", key="btn_sector_analyze")
    else:
        # Invisible label spacer to align with left column selectbox label
        st.markdown('<p style="margin-bottom: 24px;"></p>', unsafe_allow_html=True)
        st.info("👈 Please select a category first.")

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

                # Get Top Ticker and calculate summary
                top_stock = top5.iloc[0]
                top_ticker = top_stock['Ticker'].replace('.NS','')

                # Center the cards by wrapping in a centered container
                st.markdown("<div style='display:flex; justify-content:center; gap:1.5rem; flex-wrap:wrap;'>", unsafe_allow_html=True)
                cols_count = len(top5)
                cols = st.columns(5) # Standardize to 5 columns for balance
                
                for j, (_, row) in enumerate(top5.iterrows()):
                    ticker_name = row['Ticker'].replace('.NS','')
                    with cols[j]:
                        st.markdown(f"""
<div class="stock-card">
<div class="metric" style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:2px;">{ticker_name}</div>
<div class="small" style="font-size:0.85rem; color:#64748b; margin-bottom:10px; min-height:40px; display:flex; align-items:center; justify-content:center; line-height:1.2;">Leader #{j+1} in {idx_name}</div>
<div class="small" style="font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:2px;">Growth Score</div>
<div class="big" style="margin-bottom:15px; color:#059669;">{row['FinalScore']*100:.1f}<span style="font-size:1rem; color:#94a3b8;">/100</span></div>
<div class="metrics-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; padding-top:15px; border-top:1px solid #eee;">
<div><span class="small" style="font-weight:700;">Yearly Growth</span><div style="font-weight:600;">{row['CAGR']*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Efficiency</span><div style="font-weight:600;">{row['Sharpe']:.2f}</div></div>
</div>
</div>
""", unsafe_allow_html=True)
                
                # Market Leader Insight for Sector
                st.markdown(f"""
<div style="background:#f8fafc; border: 1px solid #e2e8f0; padding:20px; border-radius:15px; text-align:center; margin-top:25px; margin-bottom:30px;">
    <h4 style="color:#1e293b; margin-bottom:12px;">🏗️ {idx_name}: Sector Growth Insight</h4>
    <div style="font-size:1rem; color:#475569; line-height:1.6; max-width:800px; margin:0 auto;">
        <b>{top_ticker}</b> is currently the champion of this sector. It shows the <b>strongest wealth-building power</b> 
        and the most <b>reliable upward trend</b> compared to its peers. For investors looking for 
        sector-specific growth, it offers the best balance of speed and safety.
    </div>
</div>
""", unsafe_allow_html=True)

        progress.progress((i + 1) / len(target_indices))

    progress.empty()
    st.write("")
    st.write("")
    st.write("")
    st.success(f"✅ Analysis Complete for {selected_category}")

# ==========================================
# EXPLANATION OF TERMS
# ==========================================
st.write("")
st.markdown("### 📚 Explanation of Key Terms")
with st.expander("Click to learn more about the metrics used above", expanded=False):
    st.markdown("""
    * **Growth Score:** A simplified rating from 0 to 100. It picks stocks that grow wealth consistently without extreme risk.
    * **Yearly Growth (CAGR):** The average speed at which the stock price has climbed each year.
    * **Efficiency (Sharpe):** Measures if the stock is generating smart returns for the risk taken. Higher is better.
    * **Risk (Vol):** How much the price jumps up and down. Lower means a calmer, smoother ride.
    * **Worst Drop (Drawdown):** The deepest fall the stock has seen. Small drops mean it recovers faster from market crashes.
    """)

# ==========================================
# FOOTER NAV
# ==========================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Menu", key="btn_sector_back"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_sector_dashboard"):
        st.switch_page("pages/dashboard.py")
