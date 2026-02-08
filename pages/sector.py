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
# 0. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="NSE Sector & Thematic Advisor", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (VERY IMPORTANT)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔐 AUTH GUARD (AFTER RESTORE)
# =====================================================
if not st.session_state.get("authenticated"):
    st.switch_page("login.py")

# ==========================================
# 1. CSS STYLING
# ==========================================
st.markdown("""
<style>
    /* --- HIDE ANCHOR LINKS --- */
    [data-testid="stHeaderActionElements"] { display: none !important; visibility: hidden !important; }
    [data-testid="stHeaderAnchor"] { display: none !important; visibility: hidden !important; }
    h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a { display: none !important; content: none !important; pointer-events: none; color: transparent !important; }

    /* --- GLOBAL FONT --- */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    
    body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] { display: none; }

    /* --- TITLES & ANIMATIONS --- */
    .main-title { animation: slideInDown 0.8s ease-out; text-align: center; }
    .sub-title { text-align: center; color: #555; margin-bottom: 20px; animation: slideInDown 0.9s ease-out; }
    
    .section-title { 
        font-size: 1.2em; 
        font-weight: bold; 
        color: #333; 
        margin-top: 30px; 
        margin-bottom: 10px; 
        border-bottom: 2px solid #ddd; 
        padding-bottom: 5px; 
        animation: fadeInUp 1s ease-out; 
    }
    
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
    @keyframes slideInDown { from { opacity: 0; transform: translate3d(0, -100%, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }

    /* --- BUTTON STYLING --- */
    div.stButton > button {
        background-color: #1e293b; 
        color: white; 
        border-radius: 8px; 
        height: 3rem; 
        width: 100%;
        font-weight: 600;
        margin-top: 28px; 
    }
    div.stButton > button:hover {
        background-color: #334155; 
        border-color: #334155; 
        color: #fff;
    }
    
    /* CARD STYLING */
    .stock-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border-top: 5px solid #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.2s;
        height: 100%;
        color: #333;
    }
    .stock-card:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    
    .card-header { text-align: center; margin-bottom: 10px; }
    .stock-rank { font-size: 1.4rem; font-weight: 800; color: #1e293b; margin: 0; }
    
    .score-container { text-align: center; margin: 15px 0 20px 0; }
    .big-score { font-size: 2.5rem; font-weight: 800; color: #4CAF50; line-height: 1; margin-bottom: 5px; }
    .score-suffix { font-size: 0.6em; color: inherit; font-weight: 800; opacity: 0.9; }
    .score-label { font-size: 0.9rem; color: #64748b; font-weight: 500; }
    
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding-top: 15px; border-top: 1px solid #f1f5f9; }
    .metric-item { display: flex; flex-direction: column; }
    .metric-item.right { align-items: flex-end; text-align: right; }
    .metric-label { font-size: 0.8rem; font-weight: 700; color: #64748b; margin-bottom: 2px; }
    .metric-val { font-size: 1rem; font-weight: 600; color: #334155; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MARKET DATA
# ==========================================
# ==========================================
# 2. MARKET DATA
# ==========================================
# Imported from centralized data_fetch module
MARKET_DATA = data_fetch.MARKET_DATA

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.markdown('<h1 class="main-title">🏗️ NSE Sector & Thematic Advisor</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Select a category to explore top performing stocks.</h3>', unsafe_allow_html=True)

# --- DROPDOWNS & BUTTON ---
c1, c2 = st.columns([1, 1])
start_analysis = False 

with c1:
    cat_options = ["SELECT CATEGORY..."] + list(MARKET_DATA.keys())
    selected_category = st.selectbox("1️⃣ Market Category", cat_options)

target_indices = []

with c2:
    if selected_category == "SELECT CATEGORY...":
        st.markdown(
            """
            <div style='
                margin-top: 28px; 
                background-color: #e0f2fe; 
                color: #0369a1; 
                padding: 10px; 
                border-radius: 8px; 
                font-size: 13px; 
                display: flex; 
                align-items: center; 
                border: 1px solid #bae6fd;'>
                &nbsp; 👈 Please select a category first.
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        available_indices = list(MARKET_DATA[selected_category].keys())
        index_options = ["SELECT INDEX...", "Analyze Entire Category"] + available_indices
        selected_index = st.selectbox("2️⃣ Specific Index", index_options)
        
        if selected_index == "Analyze Entire Category":
            for name, tickers in MARKET_DATA[selected_category].items():
                target_indices.append((selected_category, name, tickers))
        elif selected_index != "SELECT INDEX...":
            target_indices.append((selected_category, selected_index, MARKET_DATA[selected_category][selected_index]))
            
        if target_indices:
            start_analysis = st.button("🚀 Analyze Performance")

# --- ANALYZE LOGIC (OPTIMIZED) ---
if start_analysis:
    st.write("---")
    progress_bar = st.progress(0)
    total = len(target_indices)
    
    for i, (cat, idx_name, tickers) in enumerate(target_indices):
        st.markdown(f"### 🔎 {idx_name}")
        
        # --- OPTIMIZED CALCULATION BLOCK ---
        with st.spinner(f"Processing {len(tickers)} stocks for {idx_name}..."):
            # 1. Add Market Benchmark for Beta calculation
            market_ticker = "NIFTYBEES.NS"
            search_tickers = tickers + [market_ticker]
            
            # 2. Fetch Data (Uses cached function)
            data = data_fetch.fetch_stock_data(search_tickers)
            
            if data.empty:
                st.warning(f"⚠️ No data available for {idx_name}")
            else:
                # 3. Calculate Metrics (Vectorized)
                metrics = metric_calculator.compute_metrics(data, market_ticker)
                
                # 4. Rank and filter (Uses unified scoring system)
                ranked_stocks = scoring_system.rank_stocks(metrics)
                
                # Filter out the benchmark and get top 5
                top_picks = ranked_stocks[ranked_stocks['Ticker'] != market_ticker].head(5)

                # --- RENDER UI (Instant) ---
                cols = st.columns(len(top_picks))
                
                for j, (idx, row) in enumerate(top_picks.iterrows()):
                    with cols[j]:
                        ticker_name = row['Ticker'].replace('.NS', '')
                        score = row.get('FinalScore', 0) * 100
                        
                        # HTML Card
                        html_content = (
                            f'<div class="stock-card">'
                            f'<div class="card-header"><div class="stock-rank">#{j+1} {ticker_name}</div></div>'
                            f'<div class="score-container"><div class="big-score">{score:.1f}<span class="score-suffix">/100</span></div><div class="score-label">Risk-Adjusted Score</div></div>'
                            f'<div class="metrics-grid">'
                            f'<div class="metric-item"><div class="metric-label">CAGR</div><div class="metric-val">{row["CAGR"]*100:.1f}%</div></div>'
                            f'<div class="metric-item right"><div class="metric-label">Max DD</div><div class="metric-val" style="color: #ef4444;">{row["MaxDrawdown"]*100:.1f}%</div></div>'
                            f'<div class="metric-item"><div class="metric-label">Sharpe</div><div class="metric-val">{row["Sharpe"]:.2f}</div></div>'
                            f'<div class="metric-item right"><div class="metric-label">Vol</div><div class="metric-val">{row["Volatility"]*100:.1f}%</div></div>'
                            f'</div></div>'
                        )
                        st.markdown(html_content, unsafe_allow_html=True)
        
        st.write("---")
        progress_bar.progress((i + 1) / total)
        
    st.success(f"✅ Analysis Complete for {selected_category}!")
    time.sleep(1)
    progress_bar.empty()

# --- EXPLANATION SECTION ---
    st.markdown('<div class="section-title">🧾 Explanation of Terms</div>', unsafe_allow_html=True)
    with st.expander("Show Detailed Definitions", expanded=False):
        st.markdown("""
        * **Risk-Adjusted Score:** A proprietary score (0-100) combining all metrics to rank the best long-term performers.
        * **CAGR (Compound Annual Growth Rate):** Average yearly growth of stock price.
        * **Max Drawdown:** The biggest percentage drop a stock has ever suffered (Measures worst-case risk).
        * **Sharpe Ratio:** Measures how much extra return you get for the risk you take. Higher is better.
        * **Volatility:** How much the stock price swings up or down. Lower = more stable.
        """)
# ==========================================
# 5. FOOTER
# ==========================================
st.write("")
st.write("---")
st.write("")

# Specific CSS for the Footer Buttons
st.markdown("""
<style>
div.stButton:last-of-type > button {
    padding: 0.4rem 1rem !important; 
    font-size: 0.8rem !important; 
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important; 
    box-shadow: none !important; 
    width: auto !important; 
    margin: 0 auto;
    white-space: nowrap !important;
    color: white !important;
}
div.stButton:last-of-type > button:hover { 
    background: #2563eb !important; 
    transform: translateY(-2px); 
}
</style>
""", unsafe_allow_html=True)

# Footer Layout
c_back, _, c_dash = st.columns([1, 4, 1])

with c_back:
    # BUG FIX: Removed try/except block which was blocking the switch
    if st.button("⬅ Back to Menu", key="btn_sector_back"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")