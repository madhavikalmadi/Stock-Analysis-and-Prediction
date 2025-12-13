import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

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
# 3. CONFIG
# ==========================================
START_DATE = (datetime.today() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")
END_DATE = datetime.today().strftime("%Y-%m-%d")
RISK_FREE_RATE = 0.05

ETF_INDEX_SYMBOLS = {
    "NIFTY 50": "NIFTYBEES.NS",
    "NIFTY NEXT 50": "JUNIORBEES.NS",
    "NIFTY MIDCAP 100": "MIDCAPETF.NS",
    "NIFTY SMALLCAP 100": "SMALLCAP.NS"
}

# ==========================================
# 4. HELPERS
# ==========================================
def extract_price(df):
    """Safely extracts a single price Series from complex DataFrames."""
    if df.empty:
        return pd.Series(dtype=float)
        
    if isinstance(df, pd.Series):
        return df.astype(float)

    if isinstance(df.columns, pd.MultiIndex):
        try:
            if "Adj Close" in df.columns.get_level_values(1): target_col = "Adj Close"
            elif "Close" in df.columns.get_level_values(1): target_col = "Close"
            else: return df.iloc[:, 0].astype(float)
            
            price_data = df.xs(target_col, level=1, axis=1)
            if isinstance(price_data, pd.DataFrame): return price_data.iloc[:, 0].astype(float)
            return price_data.astype(float)
        except:
            return df.iloc[:, 0].astype(float)

    if "Adj Close" in df.columns: return df["Adj Close"].astype(float)
    if "Close" in df.columns: return df["Close"].astype(float)

    return df.iloc[:, 0].astype(float)


@st.cache_data(ttl=3600)
def download_etf(symbol):
    try:
        df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
        if df.empty: return pd.Series(dtype=float)
        return extract_price(df).dropna()
    except: return pd.Series(dtype=float)


def calculate_metrics(price):
    if isinstance(price, pd.DataFrame): price = price.iloc[:, 0]
    price = price.dropna()
    returns = price.pct_change().dropna()

    if returns.empty: return None
    years = (price.index[-1] - price.index[0]).days / 365.25
    if years < 1: return None

    # Force float conversion to avoid Series ambiguity error
    cagr = float((price.iloc[-1] / price.iloc[0]) ** (1 / years) - 1)
    ann_ret = float(returns.mean() * 252)
    ann_vol = float(returns.std() * np.sqrt(252))

    sharpe = (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else 0

    neg = returns[returns < 0]
    downside = float(neg.std() * np.sqrt(252)) if not neg.empty else 1.0
    sortino = (ann_ret - RISK_FREE_RATE) / downside

    rollmax = price.cummax()
    max_dd = float(((price / rollmax - 1).min()) * 100) # Converted to percentage
    calmar = ann_ret / abs(max_dd/100) if max_dd < 0 else 0

    return {
        "CAGR": cagr, "Sharpe": sharpe, "Sortino": sortino,
        "Calmar": calmar, "Volatility": ann_vol, "Max_Drawdown": max_dd
    }


def calculate_score(m):
    weights = {"CAGR":25, "Sharpe":15, "Sortino":10, "Calmar":10, "Vol":20, "DD":20}
    score = 0
    score += min(m["CAGR"] / 0.20, 1) * weights["CAGR"]
    score += min(m["Sharpe"] / 1.5, 1) * weights["Sharpe"]
    score += min(m["Sortino"] / 2.0, 1) * weights["Sortino"]
    score += min(m["Calmar"] / 1.5, 1) * weights["Calmar"]
    score += max(0, 1 - m["Volatility"] / 0.30) * weights["Vol"]
    score += max(0, 1 - abs(m["Max_Drawdown"]/100) / 0.5) * weights["DD"]
    return round((score / sum(weights.values())) * 100, 1)


# ==========================================
# 5. UI & LOGIC
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

    with st.spinner("🔄 Analyzing 10-Year Market Data..."):
        results = []
        for name, ticker in ETF_INDEX_SYMBOLS.items():
            px = download_etf(ticker)
            if px.empty: continue
            
            try:
                m = calculate_metrics(px)
                if m:
                    m["Index"] = name
                    m["Score"] = calculate_score(m)
                    results.append(m)
            except: continue

        if not results:
            st.error("No valid index data found to analyze.")
            st.stop()

    # Create DataFrame & Sort
    df = pd.DataFrame(results).sort_values("Score", ascending=False)
    best = df.iloc[0]

    st.write("---")
    st.markdown("### 🏆 Market Leaderboard (10-Year Score)")

    # --- GRID DISPLAY ---
    cols = st.columns(len(df))
    
    for i, (idx, row) in enumerate(df.iterrows()):
        with cols[i]:
            delay = i * 0.1
            rank_label = f"#{i+1}"
            if i == 0: rank_label = "🥇 Winner"
            highlight_style = "border: 2px solid #2563eb;" if row["Index"] == user_choice else ""

            # --- FLATTENED HTML STRING TO PREVENT MARKDOWN CODE BLOCK ISSUES ---
            html = f"""<div class="stock-card" style="animation-delay: {delay}s; {highlight_style}">"""
            html += f"""<div class="card-header">{rank_label} {row["Index"]}</div>"""
            html += f"""<div class="big-score">{row["Score"]}<span class="score-suffix">/100</span></div>"""
            html += f"""<div class="score-label">Decision Score</div>"""
            html += f"""<div class="metrics-grid">"""
            html += f"""<div class="metric-item"><span class="metric-label">CAGR</span><span class="metric-val">{row['CAGR']*100:.1f}%</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Max DD</span><span class="metric-val" style="color:#ef4444;">{row['Max_Drawdown']:.1f}%</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Sharpe</span><span class="metric-val">{row['Sharpe']:.2f}</span></div>"""
            html += f"""<div class="metric-item"><span class="metric-label">Vol</span><span class="metric-val">{row['Volatility']*100:.1f}%</span></div>"""
            html += f"""</div></div>"""
            
            st.markdown(html, unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 📌 Your Index Result")

    if user_choice in df["Index"].values:
        user_row = df[df["Index"] == user_choice].iloc[0]

        if user_choice == best["Index"]:
            st.success(f"🎉 You selected **{user_choice}**, the BEST performing index!")
        else:
            diff = best["Score"] - user_row["Score"]
            st.warning(f"⚠️ **{user_choice}** performs lower than **{best['Index']}**.")

            st.markdown(f"""
            **Comparison:**
            - Your Score: **{user_row["Score"]}/100**
            - Winner Score: **{best["Score"]}/100**
            - Gap: **{diff:.1f} points**

            **Recommendation:** 👉 Consider switching to **{best['Index']}** for superior long-term results.
            """)
    else:
        st.error(f"Could not calculate metrics for {user_choice}. Data might be missing.")

# ==========================================
# 6. NAVIGATION (FOOTER)
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