import streamlit as st
import pandas as pd
import numpy as np

# --- IMPORT OPTIMIZED MODULES ---
import data_fetch
import metric_calculator
import scoring_system

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth_utils


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Bluechip Explorer", layout="wide")


# ============================================================
# COMPANY NAME MAPPING (ACADEMICALLY CORRECT)
# ============================================================

COMPANY_NAME_MAP = {
    "ADANIENT": "Adani Enterprises Ltd",
    "ADANIPORTS": "Adani Ports & SEZ Ltd",
    "ASIANPAINT": "Asian Paints Ltd",
    "AXISBANK": "Axis Bank Ltd",
    "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "BAJAJFINSV": "Bajaj Finserv Ltd",
    "BAJFINANCE": "Bajaj Finance Ltd",
    "BHARTIARTL": "Bharti Airtel Ltd",
    "BPCL": "Bharat Petroleum Corp Ltd",
    "BRITANNIA": "Britannia Industries Ltd",
    "CIPLA": "Cipla Ltd",
    "COALINDIA": "Coal India Ltd",
    "DIVISLAB": "Divi’s Laboratories Ltd",
    "DRREDDY": "Dr Reddy’s Laboratories Ltd",
    "EICHERMOT": "Eicher Motors Ltd",
    "GRASIM": "Grasim Industries Ltd",
    "HCLTECH": "HCL Technologies Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    "HDFCLIFE": "HDFC Life Insurance Ltd",
    "HEROMOTOCO": "Hero MotoCorp Ltd",
    "HINDALCO": "Hindalco Industries Ltd",
    "HINDUNILVR": "Hindustan Unilever Ltd",
    "ICICIBANK": "ICICI Bank Ltd",
    "INDUSINDBK": "IndusInd Bank Ltd",
    "INFY": "Infosys Ltd",
    "ITC": "ITC Ltd",
    "JSWSTEEL": "JSW Steel Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd",
    "LT": "Larsen & Toubro Ltd",
    "M&M": "Mahindra & Mahindra Ltd",
    "MARUTI": "Maruti Suzuki India Ltd",
    "NESTLEIND": "Nestlé India Ltd",
    "NTPC": "NTPC Ltd",
    "ONGC": "ONGC Ltd",
    "POWERGRID": "Power Grid Corporation of India Ltd",
    "RELIANCE": "Reliance Industries Ltd",
    "SBILIFE": "SBI Life Insurance Ltd",
    "SBIN": "State Bank of India",
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd",
    "TATACONSUM": "Tata Consumer Products Ltd",
    "TATASTEEL": "Tata Steel Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "TECHM": "Tech Mahindra Ltd",
    "TITAN": "Titan Company Ltd",
    "ULTRACEMCO": "UltraTech Cement Ltd",
    "UPL": "UPL Ltd",
    "WIPRO": "Wipro Ltd"
}


# ============================================================
# CSS (CARD UI)
# ============================================================

st.markdown("""
<style>
.stock-card {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border-top: 5px solid #4CAF50;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
}
.big-score {
    font-size: 1.8em;
    font-weight: 800;
    color: #4CAF50;
}
.metric-row {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 0.85em;
    color: #555;
}
.metric-item {
    text-align: center;
}
.suitability {
    font-size: 0.8em;
    font-weight: bold;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("## 🚀 Blue-Chip Explorer")
st.markdown("### Top 10 Recommendations based on 10-Year Historical Analysis")
st.markdown("---")


try:
    # ============================================================
    # FETCH & PROCESS DATA
    # ============================================================

    tickers = data_fetch.BLUECHIP_TICKERS.copy()
    benchmark = "^NSEI"

    if benchmark not in tickers:
        tickers.append(benchmark)

    stock_data = data_fetch.fetch_stock_data(tickers)

    if stock_data.empty:
        st.error("Failed to fetch stock data.")
        st.stop()

    metrics_df = metric_calculator.compute_metrics(stock_data, benchmark)
    ranked_df = scoring_system.rank_stocks(metrics_df)

    ranked_df = ranked_df[ranked_df["Ticker"] != benchmark]
    top10 = ranked_df.head(10)


    # ============================================================
    # INVESTOR TYPE LOGIC
    # ============================================================

    def investor_type(row):
        if row.Volatility > 0.35 or row.MaxDrawdown < -0.6:
            return "Aggressive Investor"
        elif row.Sharpe > 0.7 and row.Volatility < 0.3:
            return "Conservative Investor"
        else:
            return "Moderate Investor"


    # ============================================================
    # CARD RENDERING (FINAL & CORRECT)
    # ============================================================

    for i in range(0, len(top10), 5):
        cols = st.columns(5)
        batch = top10.iloc[i:i+5]

        for idx, row in enumerate(batch.itertuples()):
            rank = i + idx + 1
            ticker = row.Ticker.replace(".NS", "")
            company = COMPANY_NAME_MAP.get(ticker, ticker)
            score = row.FinalScore * 100
            inv = investor_type(row)

            html = f"""
<div class="stock-card">
    <h4>#{rank} {ticker}</h4>
    <div style="font-size:0.85em; color:#666; margin-bottom:6px;">
        {company}
    </div>

    <div class="big-score">{score:.1f}/100</div>
    <small>Risk-Adjusted Score</small>

    <div class="suitability">Suitable for: {inv}</div>

    <hr>

    <div class="metric-row">
        <div class="metric-item"><b>CAGR</b><br>{row.CAGR*100:.1f}%</div>
        <div class="metric-item"><b>Max DD</b><br>{row.MaxDrawdown*100:.1f}%</div>
    </div>

    <div class="metric-row">
        <div class="metric-item"><b>Sharpe</b><br>{row.Sharpe:.2f}</div>
        <div class="metric-item"><b>Vol</b><br>{row.Volatility*100:.1f}%</div>
    </div>
</div>
"""

            with cols[idx]:
                st.html(html)

except Exception as e:
    st.error("An unexpected error occurred.")
    st.code(str(e))


# ============================================================
# EXPLANATION OF TERMS
# ============================================================

st.markdown("---")
st.markdown("### 🧾 Explanation of Terms")

with st.expander("Show Detailed Definitions"):
    st.markdown("""
**Risk-Adjusted Score** – Composite score combining growth, risk, and stability  
**Aggressive Investor** – High risk tolerance, high volatility acceptable  
**Moderate Investor** – Balanced risk and return  
**Conservative Investor** – Low risk, stable returns  

**CAGR** – Compound Annual Growth Rate  
**Max Drawdown** – Worst historical loss  
**Sharpe Ratio** – Risk-adjusted return  
**Volatility** – Degree of price fluctuation
""")


# ============================================================
# NAVIGATION (FOOTER)
# ============================================================
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

c_back, _, c_dash = st.columns([1, 4, 1])
with c_back:
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        st.switch_page("dashboard.py")