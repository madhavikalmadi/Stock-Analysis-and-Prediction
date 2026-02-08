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
import auth_utils

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Company Advisor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auth check removed
# if not auth_utils.check_auth():
#     st.warning("You must log in to access this page.")
#     st.switch_page("login.py")

# ==========================================
# 2. GLOBAL CSS
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
        color: #1e293b !important;
    }

    /* INPUT SIZE FIX */
    input, textarea, div[data-baseweb="input"] {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
    }
    textarea { height: 48px !important; resize: none !important; }

    /* INPUT BOX CARD */
    .input-box {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(14px);
        padding: 25px;
        border-radius: 20px;
        border: 2px solid #2563eb;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .input-title { font-size: 1.3rem; font-weight: 800; margin-bottom: 8px; }
    .input-desc { font-size: 0.9rem; color: #64748b; margin-bottom: 15px; }

    /* RESULT CARD */
    .stock-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        border-top: 5px solid #2563eb;
        box-shadow: 0 8px 25px rgba(0,0,0,0.07);
        margin-bottom: 15px;
        opacity: 0;
        animation: fadeInUp 0.6s ease-out forwards;
    }

    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }

    .score-suffix { font-size: 0.6em; color: inherit; font-weight: 800; opacity: 0.9; }

    /* METRIC GRID */
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .metric-row { display: flex; justify-content: space-between; font-size: 0.9rem; }
    .label { font-weight: 600; color: #64748b; }
    .val { font-weight: 700; color: #334155; }

    /* RECO BOX */
    .reco-box {
        background: #f0fdf4; padding: 12px; border-left: 4px solid #22c55e;
        border-radius: 8px; color: #166534; margin: 15px 0; font-size: 0.9rem; font-weight: 600;
    }
    .warn { background: #fffbeb !important; border-left-color: #f59e0b !important; color: #92400e !important; }
    .danger { background: #fef2f2 !important; border-left-color: #ef4444 !important; color: #991b1b !important; }

    /* ACTION BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white; border-radius: 12px; padding: 12px; font-weight: 600; width: 100%; border: none; transition: 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-2px); background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPERS
# ==========================================

def resolve_ticker(user_input):
    clean_input = user_input.lower().strip()
    # Check centralized shortcuts first
    if clean_input in data_fetch.SEARCH_SHORTCUTS:
        return data_fetch.SEARCH_SHORTCUTS[clean_input]
    # Fallback to direct input (upper case)
    return user_input.upper()

def get_recommendation_text(cagr, sharpe):
    """Simple recommendation logic based on key metrics"""
    if sharpe > 0.5 and cagr > 0.12: return ("✅ Strong Buy", "Steady Growth")
    elif sharpe > 0.3 and cagr > 0.08: return ("⚠️ Moderate", "Higher Risk")
    else: return ("❌ Avoid", "Inconsistent History")

def create_card_html(row, amount_invested, years, idx=None, delay=0):
    # Extract Metrics from the Row
    ticker = row['Ticker'].replace('.NS','')
    score = round(row.get('FinalScore', 0) * 100, 1)
    cagr = row.get('CAGR', 0)
    sharpe = row.get('Sharpe', 0)
    vol = row.get('Volatility', 0)
    beta = row.get('Beta', 0)
    
    # Calculate Future Value
    # Handle case where amount is None (user left it blank)
    principal = amount_invested if amount_invested is not None else 0
    fv = principal * ((1 + cagr) ** years)
    
    # Get Recommendation Text
    reco, desc = get_recommendation_text(cagr, sharpe)
    
    # Styling classes
    reco_class = "reco-box"
    if "Moderate" in reco: reco_class += " warn"
    if "Avoid" in reco: reco_class += " danger"
    
    header = f"#{idx} {ticker}" if idx else ticker
    
    return f"""
    <div class='stock-card' style='animation-delay: {delay}s;'>
        <div style='display:flex; justify-content:space-between; border-bottom:1px dashed #e2e8f0; padding-bottom:10px;'>
            <div style='font-weight:800; font-size:1.2rem;'>{header}</div>
            <div style='font-weight:800; font-size:1.5rem; color:#16a34a;'>
                {score}<span class='score-suffix'>/100</span>
            </div>
            <div style='font-size:0.7rem; color:#64748b; font-weight:600;'>Risk-Adjusted Score</div>
        </div>
        <div class='{reco_class}'>{reco}<br><span>{desc}</span></div>
        <div class='metrics-grid'>
            <div class='metric-row'><span class='label'>CAGR</span><span class='val'>{cagr*100:.1f}%</span></div>
            <div class='metric-row'><span class='label'>Sharpe</span><span class='val'>{sharpe:.2f}</span></div>
            <div class='metric-row'><span class='label'>Vol</span><span class='val'>{vol*100:.1f}%</span></div>
            <div class='metric-row'><span class='label'>Beta</span><span class='val'>{beta:.2f}</span></div>
        </div>
        <div style='text-align:center; margin-top:15px;'>
            <div style='font-size:0.85rem; color:#64748b;'>Projected Value ({years}y)</div>
            <div style='font-size:1.4rem; font-weight:800; color:#16a34a;'>₹ {fv:,.0f}</div>
        </div>
    </div>
    """

def run_analysis(tickers):
    """
    Centralized function to fetch, calculate, and rank stocks.
    """
    # 1. Add Market Proxy for Beta Calculation
    market_ticker = "NIFTYBEES.NS"
    search_list = list(set(tickers + [market_ticker]))
    
    # 2. Fetch Data (Cached)
    df = data_fetch.fetch_stock_data(search_list)
    
    if df.empty:
        return pd.DataFrame()
        
    # 3. Calculate Metrics (Cached & Vectorized)
    metrics_df = metric_calculator.compute_metrics(df, market_ticker)
    
    # 4. Rank Stocks (Cached)
    ranked_df = scoring_system.rank_stocks(metrics_df)
    
    # Filter out the market ticker from results
    ranked_df = ranked_df[ranked_df['Ticker'] != market_ticker]
    
    return ranked_df

# ==========================================
# 4. MAIN UI
# ==========================================
if 'single_output' not in st.session_state: st.session_state.single_output = None
if 'multi_output' not in st.session_state: st.session_state.multi_output = []
if 'failed_msg' not in st.session_state: st.session_state.failed_msg = None

# --- TITLE ---
st.markdown("<h1 style='text-align:center; animation: slideInDown 0.8s ease-out;'>🏢 Company Advisor</h1>", unsafe_allow_html=True)
st.write("---")

col_single, col_multi = st.columns(2)

# --- SINGLE COMPANY ---
with col_single:
    st.markdown("<div class='input-box'><div class='input-title'>🔍 Single Deep Dive</div><div class='input-desc'>Analyze one stock.</div></div>", unsafe_allow_html=True)
    s_input = st.text_input("Ticker Symbol", value="", placeholder="e.g. Zomato, Reliance")
    
    # No default value (None), placeholder "Type amount..."
    s_amount = st.number_input("Investment Amount (₹)", value=None, placeholder="Type amount...")
    
    # UPDATED: Added HTML labels below slider for visibility
    s_years = st.slider("Years", min_value=1, max_value=20, value=1)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-top: -10px; margin-bottom: 20px;">
        <span>1 Year</span>
        <span>20 Years</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Analyze Single", use_container_width=True):
        if "," in s_input: 
            st.error("Use the Multi-Stock box for lists.")
        elif not s_input.strip(): 
            st.warning("Enter a company.")
        else:
            s_ticker = resolve_ticker(s_input)
            
            with st.spinner(f"Analyzing {s_ticker}..."):
                results = run_analysis([s_ticker])
                
                if results.empty:
                    st.session_state.single_output = None
                    st.session_state.failed_msg = f"Could not find data for {s_ticker}"
                else:
                    row = results.iloc[0]
                    st.session_state.single_output = create_card_html(row, s_amount, s_years)
                    st.session_state.failed_msg = None

    if st.session_state.failed_msg:
        st.error(st.session_state.failed_msg)
        
    if st.session_state.single_output: 
        st.markdown(st.session_state.single_output, unsafe_allow_html=True)

# --- MULTI COMPANY ---
with col_multi:
    st.markdown("<div class='input-box'><div class='input-title'>⚖️ Multi-Stock Ranking</div><div class='input-desc'>Compare multiple stocks.</div></div>", unsafe_allow_html=True)
    m_input = st.text_area("Enter Tickers (Comma Separated)", value="", placeholder="e.g. Zomato, Swiggy, TCS")
    
    # No default value, placeholder matches Ticker input style
    m_amount = st.number_input("Amount Per Stock (₹)", value=None, placeholder="Type amount...")
    
    # UPDATED: Added HTML labels below slider for visibility
    m_years = st.slider("Duration (Years)", min_value=1, max_value=20, value=1)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-top: -10px; margin-bottom: 20px;">
        <span>1 Year</span>
        <span>20 Years</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Compare & Rank", use_container_width=True):
        raw_list = [t.strip() for t in m_input.split(",") if t.strip()]
        
        if len(raw_list) < 2:
            st.warning("Please enter at least two companies to compare.")
        else:
            tickers = [resolve_ticker(t) for t in raw_list]
            
            with st.spinner("Fetching data and ranking stocks..."):
                results = run_analysis(tickers)
                
                if results.empty:
                    st.error("No valid data found for these stocks.")
                else:
                    html_cards = []
                    for idx, row in results.iterrows():
                        html = create_card_html(row, m_amount, m_years, idx=idx+1, delay=idx*0.1)
                        html_cards.append(html)
                    
                    st.session_state.multi_output = html_cards

    if st.session_state.multi_output:
        for html in st.session_state.multi_output: 
            st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. EXPLANATION OF TERMS
# ==========================================
st.markdown('<div class="section-title">🧾 Explanation of Terms</div>', unsafe_allow_html=True)
with st.expander("Show Detailed Definitions", expanded=False):
    st.markdown("""
    * **Risk-Adjusted Score:** Composite score (0-100) combining growth, risk, and stability.
    * **Sharpe Ratio:** Measures risk-adjusted return. Higher is better (>1 is good, >2 is excellent).
    * **Sortino Ratio:** Similar to Sharpe, but only penalizes downside volatility. Better for assessing real loss risk.
    * **Volatility (Std Dev):** How much the stock price swings. Lower means more stable.
    * **Alpha:** The excess return of an investment relative to the return of a benchmark index.
    * **Beta:** A measure of the stock's volatility in relation to the overall market. Beta < 1 is less volatile than market.
    """)

# ==========================================
# 6. NAVIGATION (FOOTER)
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

c_back, _, c_dash = st.columns([1, 4, 1])
with c_back:
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/reinvestor.py")

with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/dashboard.py")