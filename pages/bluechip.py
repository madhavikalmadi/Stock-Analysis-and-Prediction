import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import data_fetch
import metric_calculator
import scoring_system

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Bluechip Explorer",
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
# COMPANY NAME MAP
# ==================================================
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

# ==================================================
# GLOBAL CSS (SAME AS DASHBOARD)
# ==================================================
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
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("## 💎 Blue-Chip Explorer")
st.markdown("### Top 10 Risk-Adjusted Long-Term Stocks")
st.markdown("---")

# ==================================================
# DATA PIPELINE
# ==================================================
try:
    tickers = data_fetch.BLUECHIP_TICKERS.copy()
    benchmark = "^NSEI"

    if benchmark not in tickers:
        tickers.append(benchmark)

    stock_data = data_fetch.fetch_stock_data(tickers)
    metrics_df = metric_calculator.compute_metrics(stock_data, benchmark)
    ranked_df = scoring_system.rank_stocks(metrics_df)

    ranked_df = ranked_df[ranked_df["Ticker"] != benchmark]
    top10 = ranked_df.head(10)

    def investor_type(row):
        if row.Volatility > 0.35 or row.MaxDrawdown < -0.6:
            return "Aggressive"
        elif row.Sharpe > 0.7 and row.Volatility < 0.3:
            return "Conservative"
        return "Moderate"

    for i in range(0, len(top10), 5):
        cols = st.columns(5)
        batch = top10.iloc[i:i+5]

        for idx, row in enumerate(batch.itertuples()):
            ticker = row.Ticker.replace(".NS", "")
            company = COMPANY_NAME_MAP.get(ticker, ticker)

            inv_type = investor_type(row)

            with cols[idx]:
                st.markdown(f"""
<div class="stock-card">
<div class="metric" style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:2px;">{ticker}</div>
<div class="small" style="font-size:0.85rem; color:#64748b; margin-bottom:15px; min-height:30px; display:flex; align-items:center; justify-content:center; line-height:1.2;">{company}</div>
<div class="big" style="margin-bottom:15px;">{row.FinalScore*100:.1f}<span style="font-size:1rem; color:#94a3b8;">/100</span></div>
<div class="metrics-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; padding-top:15px; border-top:1px solid #eee;">
<div><span class="small" style="font-weight:700;">CAGR</span><div style="font-weight:600;">{row.CAGR*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Sharpe</span><div style="font-weight:600;">{row.Sharpe:.2f}</div></div>
<div><span class="small" style="font-weight:700;">Vol</span><div style="font-weight:600;">{row.Volatility*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Drawdown</span><div style="font-weight:600; color:#ef4444;">{row.MaxDrawdown*100:.1f}%</div></div>
</div>
</div>
""", unsafe_allow_html=True)

        st.write("")
        st.write("")

except Exception as e:
    st.error("Something went wrong while loading Blue-Chip data.")
    st.code(str(e))

# ==================================================
# EXPLANATION OF TERMS
# ==================================================
st.write("")
st.markdown("### 📚 Explanation of Key Terms")
with st.expander("Click to learn more about the metrics used above", expanded=False):
    st.markdown("""
    * **Final Score (0-100):** A composite rating that rewards high returns and stability while penalizing high risk.
    * **CAGR (Compound Annual Growth Rate):** The average yearly return of the investment over the analyzed period.
    * **Sharpe Ratio:** Measures risk-adjusted return. A higher Sharpe ratio (>1.0) means better returns for the risk taken.
    * **Volatility:** Represents the fluctuation in price. Lower volatility suggests a more stable and safer investment.
    * **Max Drawdown (Max DD):** The largest percentage drop from a peak to a trough. A smaller negative number (closer to 0%) is better.
    * **Investor Type:** Categorization based on volatility and drawdown (Aggressive, Moderate, Conservative).
    """)

# ==================================================
# FOOTER NAVIGATION
# ==================================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Beginner", key="btn_bluechip_back"):
        st.switch_page("pages/beginner.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_bluechip_dashboard"):
        st.switch_page("pages/dashboard.py")
