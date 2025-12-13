import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Company Advisor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. GLOBAL CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    [data-testid="stSidebar"] { display: none; }

    /* --- HIDE ANCHOR LINKS NEXT TO TITLES --- */
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

    /* SCORE SUFFIX STYLE (Matches Bluechip Explorer) */
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

    /* ACTION BUTTONS (Analyze) */
    div.stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white; border-radius: 12px; padding: 12px; font-weight: 600; width: 100%; border: none; transition: 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-2px); background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOGIC & HELPERS
# ==========================================
START_DATE = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')
RISK_FREE_RATE = 0.05

COMMON_NAMES = {
    "infosys": "INFY", "reliance": "RELIANCE", "tcs": "TCS", "hdfc bank": "HDFCBANK",
    "icici bank": "ICICIBANK", "sbi": "SBIN", "bharti airtel": "BHARTIARTL",
    "kotak": "KOTAKBANK", "itc": "ITC", "l&t": "LT", "axis bank": "AXISBANK",
    "hindustan unilever": "HINDUNILVR", "hul": "HINDUNILVR", "maruti": "MARUTI",
    "tata motors": "TATAMOTORS", "sun pharma": "SUNPHARMA", "titan": "TITAN",
    "bajaj finance": "BAJFINANCE", "wipro": "WIPRO", "hcl": "HCLTECH", 
    "zomato": "ZOMATO", "paytm": "PAYTM", "nykaa": "NYKAA", "swiggy": "SWIGGY", 
    "policybazaar": "POLICYBZR", "delhivery": "DELHIVERY"
}

WEIGHTS = {"CAGR": 25, "Sharpe": 15, "Sortino": 10, "Calmar": 10, "Vol": 10, "MaxDD": 10, "Beta": 5, "RecDays": 5}

def resolve_ticker(user_input):
    return COMMON_NAMES.get(user_input.lower().strip(), user_input.upper())

def create_card_html(ticker, score, reco, desc, m, fv, idx=None, delay=0):
    reco_class = "reco-box"
    if "Moderate" in reco: reco_class += " warn"
    if "Avoid" in reco: reco_class += " danger"
    
    header = f"#{idx} {ticker}" if idx else ticker
    
    # --- UPDATED: Score Display using .score-suffix class ---
    return f"""
    <div class='stock-card' style='animation-delay: {delay}s;'>
    <div style='display:flex; justify-content:space-between; border-bottom:1px dashed #e2e8f0; padding-bottom:10px;'>
    <div style='font-weight:800; font-size:1.2rem;'>{header}</div>
    <div style='font-weight:800; font-size:1.5rem; color:#16a34a;'>
        {score}<span class='score-suffix'>/100</span>
    </div>
    </div>
    <div class='{reco_class}'>{reco}<br><span>{desc}</span></div>
    <div class='metrics-grid'>
    <div class='metric-row'><span class='label'>CAGR</span><span class='val'>{m['CAGR']*100:.1f}%</span></div>
    <div class='metric-row'><span class='label'>Sharpe</span><span class='val'>{m['Sharpe']:.2f}</span></div>
    <div class='metric-row'><span class='label'>Vol</span><span class='val'>{m['Vol']*100:.1f}%</span></div>
    <div class='metric-row'><span class='label'>Beta</span><span class='val'>{m['Beta']:.2f}</span></div>
    </div>
    <div style='text-align:center; margin-top:15px;'>
    <div style='font-size:0.85rem; color:#64748b;'>Projected Value</div>
    <div style='font-size:1.4rem; font-weight:800; color:#16a34a;'>₹ {fv:,.0f}</div>
    </div>
    </div>
    """

@st.cache_data(ttl=3600)
def get_nifty_data():
    try:
        df = yf.download("^NSEI", start=START_DATE, end=END_DATE, progress=False)
        if isinstance(df, pd.DataFrame):
            if "Adj Close" in df.columns: return df["Adj Close"].squeeze()
            elif "Close" in df.columns: return df["Close"].squeeze()
            else: return df.iloc[:, 0].squeeze()
        return df
    except: return pd.Series(dtype=float)

def download_data(ticker):
    sym = ticker.upper() + (".NS" if not ticker.endswith(".NS") else "")
    df = yf.download(sym, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
    if df.empty: df = yf.download(sym, period="max", progress=False, auto_adjust=True)
    
    if df.empty: return pd.Series(dtype=float)

    try:
        if isinstance(df.columns, pd.MultiIndex):
            try: data = df.xs('Close', level=0, axis=1)
            except: data = df.iloc[:, 0]
        elif "Close" in df.columns: data = df["Close"]
        else: data = df.iloc[:, 0]
        if isinstance(data, pd.DataFrame): data = data.iloc[:, 0]
        return data.dropna()
    except: return pd.Series(dtype=float)

def calculate_metrics(price, nifty=None):
    if price.empty: return None
    if isinstance(price, pd.DataFrame): price = price.squeeze()
    if nifty is not None and isinstance(nifty, pd.DataFrame): nifty = nifty.squeeze()

    returns = price.pct_change().dropna()
    years = (price.index[-1] - price.index[0]).days / 365.25
    if years < 0.2: return None 

    ann_ret = float(returns.mean() * 252)
    ann_vol = float(returns.std() * np.sqrt(252))
    if years < 1: cagr = ann_ret 
    else: cagr = float((price.iloc[-1] / price.iloc[0]) ** (1 / years) - 1)
    
    sharpe = (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol != 0 else 0
    neg = returns[returns < 0]
    downside = float(neg.std() * np.sqrt(252)) if not neg.empty else 1.0
    sortino = (ann_ret - RISK_FREE_RATE) / downside
    
    roll_max = price.cummax()
    max_dd = float(((price / roll_max) - 1).min())
    calmar = ann_ret / abs(max_dd) if max_dd < 0 else 0

    rec = 0
    peak = price.iloc[0]
    peak_date = price.index[0]
    for dt, val in price.items():
        if val >= peak:
            peak = val; peak_date = dt
        else:
            rec = max(rec, (dt - peak_date).days)

    beta = 1.0
    if nifty is not None and not nifty.empty:
        n_ret = nifty.pct_change().dropna()
        common = returns.index.intersection(n_ret.index)
        if len(common) > 30:
            beta = float(np.cov(returns.loc[common], n_ret.loc[common])[0, 1] / np.var(n_ret.loc[common]))

    return {"CAGR": cagr, "Sharpe": sharpe, "Sortino": sortino, "Calmar": calmar, "Vol": ann_vol, "MaxDD": max_dd, "Beta": beta, "RecDays": rec}

def calculate_score(m):
    s = 0
    s += min(m["CAGR"] / 0.20, 1) * WEIGHTS["CAGR"]
    s += min(m["Sharpe"] / 1.5, 1) * WEIGHTS["Sharpe"]
    s += min(m["Sortino"] / 2.0, 1) * WEIGHTS["Sortino"]
    s += min(m["Calmar"] / 1.5, 1) * WEIGHTS["Calmar"]
    s += max(0, 1 - m["Vol"] / 0.35) * WEIGHTS["Vol"]
    s += max(0, 1 - abs(m["MaxDD"]) / 0.6) * WEIGHTS["MaxDD"]
    s += max(0, 1 - abs(m["Beta"] - 1) / 0.5) * WEIGHTS["Beta"]
    s += max(0, 1 - m["RecDays"] / 800) * WEIGHTS["RecDays"]
    return round((s / sum(WEIGHTS.values())) * 100, 1)

def get_recommendation(m):
    if m["Sharpe"] > 0.5 and m["CAGR"] > 0.12: return ("✅ Strong Buy", "Steady Growth")
    elif m["Sharpe"] > 0.3 and m["CAGR"] > 0.08: return ("⚠️ Moderate", "Higher Risk")
    else: return ("❌ Avoid", "Inconsistent")

# ==========================================
# 4. MAIN UI
# ==========================================
if 'single_output' not in st.session_state: st.session_state.single_output = None
if 'multi_output' not in st.session_state: st.session_state.multi_output = []
if 'failed_tickers' not in st.session_state: st.session_state.failed_tickers = []

# --- UPDATED TITLE WITH EMOJI ---
st.markdown("<h1 style='text-align:center; animation: slideInDown 0.8s ease-out;'>🏢 Company Advisor</h1>", unsafe_allow_html=True)
st.write("---")

col_single, col_multi = st.columns(2)

# --- SINGLE COMPANY ---
with col_single:
    st.markdown("<div class='input-box'><div class='input-title'>🔍 Single Deep Dive</div><div class='input-desc'>Analyze one stock.</div></div>", unsafe_allow_html=True)
    s_input = st.text_input("Ticker Symbol", value="", placeholder="e.g. Zomato, Reliance")
    s_amount = st.number_input("Investment Amount (₹)", value=None, placeholder="Type amount...")
    s_years = st.slider("Years", 1, 20, 1)

    if st.button("🚀 Analyze Single", use_container_width=True):
        if "," in s_input: st.error("Use the Multi-Stock box for lists."); st.session_state.single_output = None
        elif not s_input.strip(): st.warning("Enter a company."); st.session_state.single_output = None
        else:
            s_ticker = resolve_ticker(s_input)
            nifty = get_nifty_data()
            price = download_data(s_ticker)
            if price.empty: st.error(f"⚠️ Could not find data for '{s_input}'."); st.session_state.single_output = None
            else:
                m = calculate_metrics(price, nifty)
                if m:
                    score = calculate_score(m)
                    reco, desc = get_recommendation(m)
                    fv = (s_amount if s_amount else 0) * ((1 + m["CAGR"]) ** s_years)
                    st.session_state.single_output = create_card_html(s_ticker, score, reco, desc, m, fv)
    
    if st.session_state.single_output: st.markdown(st.session_state.single_output, unsafe_allow_html=True)

# --- MULTI COMPANY ---
with col_multi:
    st.markdown("<div class='input-box'><div class='input-title'>⚖️ Multi-Stock Ranking</div><div class='input-desc'>Compare multiple stocks.</div></div>", unsafe_allow_html=True)
    m_input = st.text_area("Enter Tickers (Comma Separated)", value="", placeholder="e.g. Zomato, Swiggy, TCS")
    m_amount = st.number_input("Amount Per Stock (₹)", value=None, placeholder="Type amount...")
    m_years = st.slider("Duration", 1, 20, 1)

    if st.button("🚀 Compare & Rank", use_container_width=True):
        raw_list = [t.strip() for t in m_input.split(",") if t.strip()]
        
        if not m_input.strip():
            st.warning("Please enter at least two companies.")
        elif len(raw_list) < 2:
            st.error("⚠️ Error: For single company analysis, please use the 'Single Deep Dive' box on the left.")
            st.session_state.multi_output = []
            st.session_state.failed_tickers = []
        else:
            tickers = [resolve_ticker(t) for t in raw_list]
            results, failed = [], []
            nifty = get_nifty_data()
            bar = st.progress(0)
            
            for i, t in enumerate(tickers):
                price = download_data(t)
                if not price.empty:
                    m = calculate_metrics(price, nifty)
                    if m:
                        m["Ticker"] = t; m["Score"] = calculate_score(m)
                        m["FV"] = (m_amount if m_amount else 0) * ((1 + m["CAGR"]) ** m_years)
                        m["Reco"], m["Desc"] = get_recommendation(m)
                        results.append(m)
                    else: failed.append(t)
                else: failed.append(t)
                bar.progress((i + 1) / len(tickers))
            bar.empty()

            st.session_state.multi_output = []
            st.session_state.failed_tickers = failed

            if results:
                df = pd.DataFrame(results).sort_values("Score", ascending=False)
                st.success(f"Ranked {len(df)} stocks")
                for idx, row in df.iterrows():
                    html = create_card_html(row['Ticker'], row['Score'], row['Reco'], row['Desc'], row, row['FV'], idx=idx+1, delay=idx*0.1)
                    st.session_state.multi_output.append(html)
            elif not failed: st.error("No valid stocks found.")

    if st.session_state.failed_tickers:
        st.error(f"⚠️ No data for: {', '.join(st.session_state.failed_tickers)}")

    if st.session_state.multi_output:
        for html in st.session_state.multi_output: st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. NAVIGATION (FOOTER)
# ==========================================
st.write(""); st.write("---"); st.write("")

# Inject specific CSS for the footer buttons to look like pills
st.markdown("""
<style>
/* Targets the buttons in the columns below to match the rounded pill style */
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

# Footer Layout: Back button on top left, Dashboard button centered below
c_back, _, _ = st.columns([1, 4, 1])
with c_back:
    if st.button("⬅ Back to Menu"):
        try:
            st.switch_page("pages/reinvestor.py")
        except Exception as e:
            st.error("Page 'pages/reinvestor.py' not found.")

_, c_dash, _ = st.columns([5, 2, 5])
with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        try:
            st.switch_page("app.py")
        except Exception as e:
            st.error("Page 'app.py' not found.")