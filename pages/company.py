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
# HELPERS
# ==================================================
def resolve_ticker(user_input):
    clean = user_input.lower().strip()
    if clean in data_fetch.SEARCH_SHORTCUTS:
        return data_fetch.SEARCH_SHORTCUTS[clean]
    return user_input.upper()

def get_recommendation_text(cagr, sharpe):
    if sharpe > 0.5 and cagr > 0.12:
        return {
            "verdict": "✅ Strong Buy",
            "desc": "A Star Performer",
            "reason": "This stock shows high growth power and stays very steady over time.",
            "color": "#059669", 
            "bg": "#ecfdf5"
        }
    elif sharpe > 0.3 and cagr > 0.08:
        return {
            "verdict": "⚠️ Moderate",
            "desc": "Good Potential",
            "reason": "It has good growth speed, but the upward path can be a bit bumpy.",
            "color": "#b45309", 
            "bg": "#fffbeb"
        }
    else:
        if cagr < 0.08:
            reason = "The growth speed is too slow to significantly increase your wealth."
        elif sharpe <= 0.3:
            reason = "The growth is very inconsistent, making the stock quite risky."
        else:
            reason = "The upward growth hasn't been reliable enough to trust it fully."
        return {
            "verdict": "❌ Avoid",
            "desc": "Wait and See",
            "reason": reason,
            "color": "#dc2626", 
            "bg": "#fef2f2"
        }

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
st.markdown("## 🏢 Company Advisor")
st.markdown("### Analytics & Stock Comparison")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

# ---------------- SINGLE COMPANY ----------------
with col1:
    st.markdown("<div class='input-box'><b>🔍 Single Company Analysis</b></div>", unsafe_allow_html=True)
    ticker = st.text_input("Ticker")
    amount = st.number_input("Investment Amount ₹", value=None)
    years = st.slider("Investment Horizon (Years)", 1, 20, 1)

    if st.button("🚀 Analyze Company", key="btn_company_analyze"):
        if ticker.strip():
            t = resolve_ticker(ticker)
            result = run_analysis([t])

            if result.empty:
                st.error("No data found for this company.")
                st.session_state.single_result = None
            else:
                st.session_state.single_result = result.iloc[0]
                # Store inputs for calculation (use distinct keys to avoid widget collision)
                st.session_state.calc_amount_s = amount if amount else 0
                st.session_state.calc_years_s = years
    
    # Display Single Company Result
    if "single_result" in st.session_state and st.session_state.single_result is not None:
        row = st.session_state.single_result
        res = get_recommendation_text(row.CAGR, row.Sharpe)
        desc = res["desc"]
        
        # Calculate Potential Returns
        amt = st.session_state.get("calc_amount_s", 0)
        yrs = st.session_state.get("calc_years_s", 1)
        future_val = amt * ((1 + row.CAGR) ** yrs)
        profit = future_val - amt

        st.markdown(f"""
<div class="stock-card">
<div class="metric" style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:2px;">{row.Ticker.replace('.NS','')}</div>
<div class="small" style="font-size:0.85rem; color:#64748b; margin-bottom:10px; min-height:30px; display:flex; align-items:center; justify-content:center; line-height:1.2;">{desc}</div>
<div class="small" style="font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:2px;">Risk-Adjusted Score</div>
<div class="big" style="margin-bottom:15px; color:#059669;">{row.FinalScore*100:.1f}<span style="font-size:1rem; color:#94a3b8;">/100</span></div>

<div style="background: #f8fafc; border-radius: 10px; padding: 12px; margin-bottom: 15px; border: 1px solid #e2e8f0;">
    <div class="small" style="font-weight:700; color:#475569; margin-bottom:4px;">ESTIMATED RETURNS ({yrs}Y)</div>
    <div style="font-size:1.1rem; font-weight:800; color:#047857;">₹{future_val:,.0f}</div>
    <div style="font-size:0.85rem; font-weight:600; color:#10b981;">+ ₹{profit:,.0f} Profit</div>
</div>

<div class="metrics-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; padding-top:15px; border-top:1px solid #eee;">
<div><span class="small" style="font-weight:700;">CAGR</span><div style="font-weight:600;">{row.CAGR*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Sharpe</span><div style="font-weight:600;">{row.Sharpe:.2f}</div></div>
<div><span class="small" style="font-weight:700;">Vol</span><div style="font-weight:600;">{row.Volatility*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Drawdown</span><div style="font-weight:600; color:#ef4444;">{row.MaxDrawdown*100:.1f}%</div></div>
</div>
<div class="small" style="margin-top:10px; font-weight:600; color:#475569; font-size:0.85rem; background:#f1f5f9; padding:8px; border-radius:6px; text-align:center;">
    Verdict: <span style="color:#2563eb;">{res['verdict']}</span><br>
    <span style="font-size:0.75rem; color:#64748b; font-weight:400;">Reason: {res['reason']}</span>
</div>
</div>
""", unsafe_allow_html=True)

# ---------------- MULTI COMPANY ----------------
with col2:
    st.markdown("<div class='input-box'><b>⚖️ Multi Companies</b></div>", unsafe_allow_html=True)
    tickers = st.text_input("Comma-separated tickers (e.g. TCS, INFY, RELIANCE)")
    amount_m = st.number_input("Investment Amount ₹", value=None, key="multi_amount")
    years_m = st.slider("Investment Horizon (Years)", 1, 20, 1, key="multi")

    if st.button("📊 Multi Companies", key="btn_company_compare"):
        lst = [resolve_ticker(t.strip()) for t in tickers.split(",") if t.strip()]
        if len(lst) < 2:
            st.warning("Please enter at least 2 companies.")
            st.session_state.multi_result = None
        else:
            ranked = run_analysis(lst)
            st.session_state.multi_result = ranked
            # Store inputs for calculation (use distinct keys to avoid widget collision)
            st.session_state.calc_amount_m = amount_m if amount_m else 0
            st.session_state.calc_years_m = years_m

    # Display Multi Company Result
    if "multi_result" in st.session_state and st.session_state.multi_result is not None:
        ranked = st.session_state.multi_result
        amt_m = st.session_state.get("calc_amount_m", 0)
        yrs_m = st.session_state.get("calc_years_m", 1)
        
        st.write("")
        for idx, row in ranked.sort_values("FinalScore", ascending=False).iterrows():
            # Re-calculate verdict for each
            res_m = get_recommendation_text(row.CAGR, row.Sharpe)
            desc_m = res_m["desc"]
            
            # Calculate Potential Returns
            future_val_m = amt_m * ((1 + row.CAGR) ** yrs_m)
            profit_m = future_val_m - amt_m

            st.markdown(f"""
<div class="stock-card" style="margin-bottom:20px;">
<div class="metric" style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:2px;">{row.Ticker.replace('.NS','')}</div>
<div class="small" style="font-size:0.85rem; color:#64748b; margin-bottom:10px; min-height:30px; display:flex; align-items:center; justify-content:center; line-height:1.2;">{desc_m}</div>
<div class="small" style="font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:2px;">Risk-Adjusted Score</div>
<div class="big" style="margin-bottom:15px; color:#059669;">{row.FinalScore*100:.1f}<span style="font-size:1rem; color:#94a3b8;">/100</span></div>

<div style="background: #f8fafc; border-radius: 10px; padding: 12px; margin-bottom: 15px; border: 1px solid #e2e8f0;">
    <div class="small" style="font-weight:700; color:#475569; margin-bottom:4px;">ESTIMATED RETURNS ({yrs_m}Y)</div>
    <div style="font-size:1.1rem; font-weight:800; color:#047857;">₹{future_val_m:,.0f}</div>
    <div style="font-size:0.85rem; font-weight:600; color:#10b981;">+ ₹{profit_m:,.0f} Profit</div>
</div>

<div class="metrics-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; padding-top:15px; border-top:1px solid #eee;">
<div><span class="small" style="font-weight:700;">CAGR</span><div style="font-weight:600;">{row.CAGR*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Sharpe</span><div style="font-weight:600;">{row.Sharpe:.2f}</div></div>
<div><span class="small" style="font-weight:700;">Vol</span><div style="font-weight:600;">{row.Volatility*100:.1f}%</div></div>
<div><span class="small" style="font-weight:700;">Drawdown</span><div style="font-weight:600; color:#ef4444;">{row.MaxDrawdown*100:.1f}%</div></div>
</div>
<div class="small" style="margin-top:10px; font-weight:600; color:#475569; font-size:0.85rem; background:#f1f5f9; padding:8px; border-radius:6px; text-align:center;">
    Verdict: <span style="color:#2563eb;">{res_m['verdict']}</span><br>
    <span style="font-size:0.75rem; color:#64748b; font-weight:400;">Reason: {res_m['reason']}</span>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# EXPLANATION OF TERMS
# ==========================================
st.write("")
st.markdown("### 📚 Explanation of Key Terms")
with st.expander("Click to learn more about the metrics used above", expanded=False):
    st.markdown("""
    * **Risk-Adjusted Score (0-100):** The primary score to judge a company. Higher is better. It balances growth (CAGR) against risk (Volatility).
    * **CAGR (Compound Annual Growth Rate):** The average yearly return. 20% means your money is growing fast.
    * **Sharpe:** A measure of risk-adjusted return. >1 is good, >2 is excellent. shows if returns are due to smarts or risk luck.
    * **Vol (Volatility):** How much the stock price fluctuates. Low vol = stable; High vol = risky/rollercoaster.
    * **Drawdown (Max Loss):** The worst possible drop from a peak to a trough. If this is -50%, it means the stock once lost half its value.
    * **Verdict:** A quick summary based on the combination of growth and risk:
        * **✅ Strong Buy:** A star performer with high growth and very safe stability.
        * **⚠️ Moderate:** Good potential for growth, but the price waves can be a bit bumpy.
        * **❌ Avoid:** Moving a bit too slowly or carries too much risk for most investors.
    """)

# ==================================================
# FOOTER NAVIGATION
# ==================================================
st.write("")
st.markdown("---")
st.write("")

c_back, _, c_dash = st.columns([1, 6, 1])

with c_back:
    if st.button("⬅ Back to Menu", key="btn_company_back"):
        st.switch_page("pages/reinvestor.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_company_dashboard"):
        st.switch_page("pages/dashboard.py")
