import streamlit as st
import pandas as pd
import numpy as np

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system

# --- 1. PAGE CONFIG & CSS ---
st.set_page_config(page_title="Bluechip Explorer", layout="wide")

st.markdown("""
<style>
    /* FORCE HIDE HEADER ANCHORS */
    [data-testid="stHeaderActionElements"] { display: none !important; visibility: hidden !important; }
    [data-testid="stHeaderAnchor"] { display: none !important; visibility: hidden !important; }
    h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a { display: none !important; content: none !important; pointer-events: none; color: transparent !important; }
    
    /* ANIMATION DEFINITIONS */
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
    @keyframes slideInDown { from { opacity: 0; transform: translate3d(0, -100%, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }

    /* COMPONENT STYLING */
    .main-title { animation: slideInDown 0.8s ease-out; text-align: center; } 
    .sub-title { text-align: center; color: #555; margin-bottom: 20px; animation: slideInDown 0.9s ease-out; } 

    /* Card Styling */
    .stock-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-top: 5px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        opacity: 0; 
        animation: fadeInUp 0.6s ease-out forwards;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stock-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }

    .big-score { font-size: 1.8em; font-weight: 800; color: #4CAF50; }
    .score-suffix { font-size: 0.6em; color: inherit; font-weight: 800; opacity: 0.9; } 
    
    .metric-row { font-size: 0.85em; color: #555; margin-top: 10px; display: flex; justify-content: space-between; }
    .metric-item { text-align: center; }
    .section-title { font-size: 1.2em; font-weight: bold; color: #333; margin-top: 30px; margin-bottom: 10px; border-bottom: 2px solid #ddd; padding-bottom: 5px; animation: fadeInUp 1s ease-out; }
    
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    /* Footer Button Style */
    .footer-btn-container { text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. MAIN PAGE LOGIC ---

st.markdown('<h1 class="main-title">🚀 Blue-Chip Explorer</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Top 10 Recommendations based on 10-Year History</h3>', unsafe_allow_html=True)
st.markdown("---")

# --- STEP 1: FETCH DATA ---
with st.spinner("Analyzing Market Data & Calculating Scores..."):
    try:
        # 1. Get List of Bluechips
        tickers = data_fetch.BLUECHIP_TICKERS
        
        # Ensure Benchmark Ticker is in the list
        benchmark_ticker = "^NSEI" 
        if benchmark_ticker not in tickers:
            tickers.append(benchmark_ticker)

        # 2. Fetch Data (Cached)
        stock_data = data_fetch.fetch_stock_data(tickers)
        
        if stock_data.empty:
            st.error("No data found. Please check your internet connection.")
            st.stop()
            
        # 3. Compute Metrics
        metrics_df = metric_calculator.compute_metrics(stock_data, benchmark_ticker) 
        
        # 4. Rank Stocks
        ranked_stocks = scoring_system.rank_stocks(metrics_df)
        
        # Filter out the Benchmark itself so it doesn't show as a card
        ranked_stocks = ranked_stocks[ranked_stocks['Ticker'] != benchmark_ticker]

        # Get Top 10
        top10 = ranked_stocks.head(10)

    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        st.stop()

# --- STEP 2: RENDER UI ---
if not top10.empty:
    for i in range(0, 10, 5):
        cols = st.columns(5)
        batch = top10.iloc[i:i+5]
        
        for idx, (sym, row) in enumerate(batch.iterrows()):
            # Prepare Variables
            ticker_name = row['Ticker'].replace('.NS', '')
            cagr = row.get('CAGR', 0)
            max_dd = row.get('MaxDrawdown', 0)
            sharpe = row.get('Sharpe', 0)
            vol = row.get('Volatility', 0)
            score = row.get('FinalScore', 0) * 100 

            with cols[idx]:
                delay = (i + idx) * 0.1 
                
                # HTML CARD (No Indentation to prevent code blocks)
                html_code = f"""
<div class="stock-card" style="animation-delay: {delay}s;">
<h4 style="margin-bottom: 0;">#{i + idx + 1} {ticker_name}</h4>
<div class="big-score">{score:.1f}<span class="score-suffix">/100</span></div>
<small>Decision Score</small>
<hr style="margin: 10px 0; opacity: 0.3;">
<div class="metric-row">
<div class="metric-item"><b>CAGR</b><br>{cagr*100:.1f}%</div>
<div class="metric-item"><b>Max DD</b><br>{max_dd*100:.1f}%</div>
</div>
<div class="metric-row">
<div class="metric-item"><b>Sharpe</b><br>{sharpe:.2f}</div>
<div class="metric-item"><b>Vol</b><br>{vol*100:.1f}%</div>
</div>
</div>
"""
                st.markdown(html_code, unsafe_allow_html=True)
                st.write("") 

    st.markdown("---")
    
    # Interpretation & Footer
    st.markdown('<div class="section-title" style="animation-delay: 1.2s; animation-fill-mode: backwards;">✅ Interpretation</div>', unsafe_allow_html=True)
    st.info("""
    * **Higher CAGR** = Stronger long-term growth.
    * **Sharpe > 0.5** = Steady, risk-adjusted returns.
    * **Lower Volatility & Drawdown** = Safer investment.
    * **Decision Score** = The higher the score, the better the overall performance.
    """)

    st.markdown('<div class="section-title">🧾 Explanation of Terms</div>', unsafe_allow_html=True)
    with st.expander("Show Detailed Definitions", expanded=False):
        st.markdown("""
        * **Decision Score:** A proprietary score (0-100) combining all metrics to rank the best long-term performers.
        * **CAGR (Compound Annual Growth Rate):** Average yearly growth of stock price.
        * **Max Drawdown:** The biggest percentage drop a stock has ever suffered (Measures worst-case risk).
        * **Sharpe Ratio:** Measures how much extra return you get for the risk you take. Higher is better.
        * **Volatility:** How much the stock price swings up or down. Lower = more stable.
        """)

else:
    st.warning("No stock data available to display. Please try again later.")

# --- FOOTER ---
st.write(""); st.write("---"); st.write("")

st.markdown("""
<style>
div.stButton > button {
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
div.stButton > button:hover { 
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
        st.switch_page("app.py")