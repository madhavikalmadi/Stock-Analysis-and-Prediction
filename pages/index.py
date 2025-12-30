import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Index Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    [data-testid="stSidebar"] { display: none; }

    /* --- HIDE ANCHOR LINKS --- */
    [data-testid="stHeaderActionElements"] { display: none !important; visibility: hidden !important; }
    [data-testid="stHeaderAnchor"] { display: none !important; visibility: hidden !important; }
    h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a { display: none !important; content: none !important; pointer-events: none; color: transparent !important; }

    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%);
        font-family: 'Outfit', sans-serif !important;
    }

    /* --- STOCK CARD STYLING --- */
    .stock-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-top: 5px solid #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        height: 100%;
        text-align: center;
        transition: transform 0.2s;
        animation: fadeInUp 0.6s ease-out;
    }
    .stock-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }

    .card-header { font-size: 1.1rem; font-weight: 800; color: #333; margin-bottom: 5px; }
    
    .big-score { font-size: 2rem; font-weight: 800; color: #4CAF50; margin: 10px 0; }
    .score-suffix { font-size: 0.6em; color: inherit; font-weight: 800; opacity: 0.9; }
    .score-label { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

    /* METRIC GRID */
    .metrics-grid { 
        display: grid; 
        grid-template-columns: 1fr 1fr; 
        gap: 10px; 
        margin-top: 15px; 
        padding-top: 15px;
        border-top: 1px dashed #e2e8f0;
    }
    .metric-item { display: flex; flex-direction: column; }
    .metric-label { font-size: 0.75rem; font-weight: 700; color: #64748b; }
    .metric-val { font-size: 0.95rem; font-weight: 700; color: #1e293b; }

    /* ANIMATIONS */
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0px); } }

    /* BUTTON STYLING */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 10px;
        font-weight: 600;
        background: linear-gradient(90deg, #2563eb 0%, #1e40af 100%);
        color: white;
        border: none;
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    /* SECTION TITLE */
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
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CONFIG & DATA MAPS
# ==========================================
ETF_INDEX_SYMBOLS = {
    "NIFTY 50": "NIFTYBEES.NS",
    "NIFTY NEXT 50": "JUNIORBEES.NS",
    "NIFTY MIDCAP 100": "MIDCAPETF.NS",
    "NIFTY SMALLCAP 100": "SMALLCAP.NS"
}

# Reverse mapping to find "NIFTY 50" from "NIFTYBEES.NS" later
TICKER_TO_NAME = {v: k for k, v in ETF_INDEX_SYMBOLS.items()}

# ==========================================
# 4. MAIN UI & LOGIC
# ==========================================
st.markdown("<h1 style='text-align:center;'>📊 Index Fund Analyzer</h1>", unsafe_allow_html=True)
st.write("---")

st.markdown("### 🔍 Check Your Investment First")

user_choice = st.selectbox(
    "Select Your Index:",
    ["Select..."] + list(ETF_INDEX_SYMBOLS.keys())
)

analyze = st.button("🚀 Compare Performance")

if analyze:
    if user_choice == "Select...":
        st.warning("Please select an index first.")
        st.stop()

    # --- STEP 1: CALCULATIONS (Hidden behind spinner) ---
    with st.spinner("🔄 Analyzing 10-Year Market Data..."):
        # 1. Fetch All Data in One Batch
        tickers = list(ETF_INDEX_SYMBOLS.values())
        raw_data = data_fetch.fetch_stock_data(tickers)
        
        if raw_data.empty:
            st.error("Could not fetch market data. Please check connection.")
            st.stop()
            
        # 2. Compute Metrics (Vectorized)
        # Using NIFTYBEES as the benchmark for Beta
        metrics_df = metric_calculator.compute_metrics(raw_data, "NIFTYBEES.NS")
        
        # 3. Score Indices
        ranked_df = scoring_system.rank_stocks(metrics_df)
        
        # 4. Map Tickers back to Readable Names
        ranked_df['Index Name'] = ranked_df['Ticker'].map(TICKER_TO_NAME)
        
        # Get the Winner
        best = ranked_df.iloc[0]

    # --- STEP 2: RENDER UI (Instant) ---
    
    st.write("---")
    st.markdown("### 🏆 Market Leaderboard (10-Year Score)")

    # --- GRID DISPLAY ---
    cols = st.columns(len(ranked_df))
    
    for i, (idx, row) in enumerate(ranked_df.iterrows()):
        index_name = row.get('Index Name', row['Ticker'])
        score = row.get('FinalScore', 0) * 100
        
        with cols[i]:
            delay = i * 0.1
            rank_label = f"#{i+1}"
            if i == 0: rank_label = "🥇 Winner"
            
            # Highlight user's choice
            highlight_style = "border: 2px solid #2563eb;" if index_name == user_choice else ""

            # HTML Card construction
            html = f"""<div class="stock-card" style="animation-delay: {delay}s; {highlight_style}">"""
            html += f"""<div class="card-header">{rank_label} {index_name}</div>"""
            html += f"""<div class="big-score">{score:.1f}<span class="score-suffix">/100</span></div>"""
            html += f"""<div class="score-label">Decision Score</div>"""
            html += f"""<div class="metrics-grid">"""
            html += f"""<div class="metric-item"><span class="metric-label">CAGR</span><span class="metric-val">{row['CAGR']*100:.1f}%</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Max DD</span><span class="metric-val" style="color:#ef4444;">{row['MaxDrawdown']*100:.1f}%</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Sharpe</span><span class="metric-val">{row['Sharpe']:.2f}</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Vol</span><span class="metric-val">{row['Volatility']*100:.1f}%</span></div>"""
            html += f"""</div></div>"""
            
            st.markdown(html, unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 📌 Your Index Result")

    # Find User Selection in Results
    user_row = ranked_df[ranked_df["Index Name"] == user_choice]

    if not user_row.empty:
        user_row = user_row.iloc[0]
        user_score = user_row.get('FinalScore', 0) * 100
        best_score = best.get('FinalScore', 0) * 100

        if user_choice == best['Index Name']:
            st.success(f"🎉 You selected **{user_choice}**, the BEST performing index!")
            st.balloons()
        else:
            diff = best_score - user_score
            st.warning(f"⚠️ **{user_choice}** performs lower than **{best['Index Name']}**.")

            st.markdown(f"""
            **Comparison:**
            - Your Score: **{user_score:.1f}/100**
            - Winner Score: **{best_score:.1f}/100**
            - Gap: **{diff:.1f} points**

            **Recommendation:** 👉 Consider switching to **{best['Index Name']}** for superior long-term results.
            """)
    else:
        st.error(f"Could not calculate metrics for {user_choice}. Data might be missing.")

# ==========================================
# 5. NAVIGATION (FOOTER)
# ==========================================
st.write(""); st.write("---"); st.write("")

# Inject specific CSS for the footer buttons
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
    if st.button("⬅ Back to Menu"):
        try:
            st.switch_page("pages/reinvestor.py")
        except:
             st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        st.switch_page("pages/dashboard.py")