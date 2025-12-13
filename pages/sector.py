import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time

# ==========================================
# 0. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="NSE Sector & Thematic Advisor", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 1. CSS STYLING (Matched to Bluechip Explorer)
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
        background-color: #ffffff !important; /* Force White Background */
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

    /* --- BUTTON STYLING (General) --- */
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.95); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MARKET DATA
# ==========================================
MARKET_DATA = {
    "✈️ Services Sector": {
        "NIFTY Services Sector": [
            "HDFCBANK", "TCS", "ICICIBANK", "BHARTIARTL", "INFY", "SBIN", "AXISBANK",
            "KOTAKBANK", "BAJFINANCE", "HCLTECH", "ADANIENT", "TITAN", "TECHM",
            "WIPRO", "BAJAJFINSV", "ADANIPORTS", "APOLLOHOSP", "HDFCLIFE", "SBILIFE",
            "POWERGRID", "NTPC", "INDIGO", "TRENT"
        ]
    },
    "🏦 Financial & Banking": {
        "NIFTY Bank": [
            "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
            "BANKBARODA", "PNB", "AUBANK", "FEDERALBNK", "IDFCFIRSTB", "BANDHANBNK"
        ],
        "NIFTY PSU Bank": [
            "SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "INDIANB",
            "BANKINDIA", "IOB", "UCOBANK", "CENTRALBK", "MAHABANK", "PSB"
        ],
        "NIFTY Private Bank": [
            "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
            "FEDERALBNK", "IDFCFIRSTB", "RBLBANK", "CUB", "BANDHANBNK"
        ],
        "NIFTY Fin Services": [
            "HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN", "BAJFINANCE", "BAJAJFINSV",
            "KOTAKBANK", "HDFCLIFE", "SBILIFE", "PFC", "REC", "CHOLAFIN",
            "SHRIRAMFIN", "MUTHOOTFIN", "HDFCAMC", "ICICIGI", "SBICARD", "RECLTD", "LICHSGFIN"
        ]
    },
    "💻 Technology & IT": {
        "NIFTY IT": [
            "TCS", "INFY", "HCLTECH", "TECHM", "WIPRO",
            "LTIM", "PERSISTENT", "COFORGE", "LTTS", "MPHASIS"
        ],
        "NIFTY Digital": [
            "NAUKRI", "ZOMATO", "PAYTM", "POLICYBZR", "NYKAA", "TATACOMM",
            "DELHIVERY", "INDIAMART", "AFFLE", "HAPPSTMINDS", "MAPMYINDIA",
            "TANLA", "LATENTVIEW", "CARTRADE", "FSL"
        ]
    },
    "🏠 Consumer & Lifestyle": {
        "NIFTY FMCG": [
            "HINDUNILVR", "ITC", "NESTLEIND", "VBL", "BRITANNIA", "GODREJCP",
            "TATACONSUM", "MCDOWELL-N", "MARICO", "DABUR", "COLPAL", "PATAINDIA",
            "UBL", "RADICO", "EMAMILTD"
        ],
        "NIFTY Auto": [
            "M&M", "MARUTI", "TATAMOTORS", "BAJAJ-AUTO", "EICHERMOT", "TVSMOTOR",
            "HEROMOTOCO", "MOTHERSON", "ASHOKLEY", "BHARATFORG", "TIINDIA",
            "MRF", "BOSCHLTD", "BALKRISIND", "SONACOMS"
        ],
        "NIFTY India Consumption 30": [
            "BHARTIARTL", "ITC", "HINDUNILVR", "M&M", "MARUTI", "TITAN",
            "ASIANPAINT", "ZOMATO", "INDIGO", "TRENT", "BAJAJ-AUTO", "DMART",
            "NESTLEIND", "ADANIPOWER", "DLF", "VBL", "GODREJCP", "APOLLOHOSP"
        ],
        "NIFTY Consumer Durables": [
            "TITAN", "HAVELLS", "DIXON", "KALYANJEWEL", "VOLTAS", "BLUESTARCO",
            "AMBER", "CENTURYPLY", "KAJARIACER", "CROMPTON", "VGUARD",
            "RAJESHEXPO", "BATAINDIA", "WHIRLPOOL", "CERA"
        ],
        "NIFTY Media": [
            "SUNTV", "ZEEL", "PVRINOX", "NAZARA", "NETWORK18", "PFOCUS",
            "SAREGAMA", "TIPSIND", "DBCORP", "HATHWAY"
        ]
    },
    "🏗️ Realty & Construction": {
        "NIFTY Realty": [
            "DLF", "GODREJPROP", "PHOENIXLTD", "LODHA", "PRESTIGE",
            "OBEROIRLTY", "BRIGADE", "SOBHA", "SIGNATURE", "ANANTRAJ"
        ],
        "NIFTY Housing": [
            "LT", "NTPC", "ULTRACEMCO", "HDFCBANK", "ICICIBANK", "SBIN",
            "TATASTEEL", "JSWSTEEL", "GRASIM", "ASIANPAINT", "AMBUJACEM",
            "PIDILITIND", "DLF", "GODREJPROP", "HAVELLS", "VOLTAS",
            "CHOLAFIN", "LICHSGFIN", "PNBHOUSING", "KAJARIACER"
        ]
    },
    "🛢️ Energy & Resources": {
        "NIFTY Energy": [
            "RELIANCE", "NTPC", "ONGC", "POWERGRID", "COALINDIA",
            "BPCL", "IOC", "TATAPOWER", "GAIL", "ADANIGREEN"
        ],
        "NIFTY Oil & Gas": [
            "RELIANCE", "ONGC", "IOC", "BPCL", "GAIL", "HINDPETRO",
            "OIL", "PETRONET", "IGL", "ATGL", "GUJGASLTD", "MGL",
            "CASTROLIND", "GSPL"
        ],
        "NIFTY Metal": [
            "TATASTEEL", "HINDALCO", "JSWSTEEL", "JINDALSTEL", "VEDL",
            "ADANIENT", "NMDC", "SAIL", "NATIONALUM", "APLAPOLLO",
            "HINDZINC", "JSL", "WELCORP", "RATNAMANI"
        ],
        "NIFTY Commodities": [
            "RELIANCE", "ULTRACEMCO", "TATASTEEL", "NTPC", "JSWSTEEL",
            "ONGC", "GRASIM", "HINDALCO", "COALINDIA", "PIDILITIND",
            "VEDL", "SHREECEM", "AMBUJACEM", "BPCL", "JINDALSTEL"
        ]
    },
    "💊 Healthcare": {
        "NIFTY Pharma": [
            "SUNPHARMA", "DIVISLAB", "CIPLA", "TORNTPHARM", "DRREDDY",
            "LUPIN", "ZYDUSLIFE", "MANKIND", "ALKEM", "AUROPHARMA",
            "ABBOTINDIA", "GLENMARK", "BIOCON", "LAURUSLABS", "IPCALAB",
            "JBCHEPHARM", "GLAND", "NATCOPHARM", "PFIZER", "GRANULES"
        ],
        "NIFTY Healthcare": [
            "APOLLOHOSP", "MAXHEALTH", "FORTIS", "MEDANTA", "NH",
            "LALPATHLAB", "METROPOLIS", "SYNGENE", "POLYMED", "RAINBOW",
            "SUNPHARMA", "DIVISLAB", "CIPLA", "DRREDDY", "ALKEM",
            "LUPIN", "AUROPHARMA", "ZYDUSLIFE", "TORNTPHARM", "ABBOTINDIA"
        ]
    },
    "⚙️ Infra & Industrial": {
        "NIFTY Infrastructure": [
            "RELIANCE", "BHARTIARTL", "LT", "NTPC", "POWERGRID", "ULTRACEMCO",
            "ONGC", "ADANIPORTS", "GRASIM", "INDIGO", "TITAN", "TATAPOWER",
            "HINDUNILVR", "BPCL", "APOLLOHOSP", "SHREECEM", "INDHOTEL", "GAIL"
        ],
        "NIFTY CPSE": [
            "NTPC", "ONGC", "BEL", "COALINDIA", "POWERGRID", "NHPC", "OIL",
            "SJVN", "COCHINSHIP", "NLCINDIA", "NBCC", "IRCON"
        ],
        "NIFTY PSE": [
            "NTPC", "ONGC", "BEL", "HAL", "POWERGRID", "COALINDIA", "IOC",
            "PFC", "REC", "GAIL", "BPCL", "BHARATFORG", "BHEL", "OIL",
            "CONCOR", "NMDC", "LICHSGFIN", "HINDPETRO"
        ],
        "NIFTY Industrials": [
            "LT", "HAL", "SIEMENS", "ABB", "BEL", "CGPOWER", "CUMMINSIND",
            "POLYCAB", "BHEL", "THERMAX", "BHARATFORG", "TIMKEN",
            "AIAENG", "SCHAEFFLER", "APLAPOLLO", "SUZLON"
        ]
    },
    "🌱 Thematic & Emerging": {
        "NIFTY SME EMERGE": [
            "KOTYARK", "ALFALOGIC", "UCL", "HPIL", "E2E", "ORIANA",
            "RELIABLE", "BASILIC"
        ],
        "NIFTY India Defence": [
            "HAL", "BEL", "MAZDOCK", "BDL", "COCHINSHIP", "SOLARINDS",
            "BHARATFORG", "DATAPATTERNS", "MTARTECH", "ASTRAMICRO",
            "PARAS", "GRSE", "MIDHANI", "IDEAFORGE"
        ],
        "NIFTY Mobility": [
            "TATAMOTORS", "MARUTI", "M&M", "BAJAJ-AUTO", "INDIGO",
            "MOTHERSON", "BOSCHLTD", "SONACOMS", "EXIDEIND", "APOLLOTYRE",
            "MRF", "HEROMOTOCO", "TVSMOTOR", "EICHERMOT"
        ],
        "NIFTY MNC": [
            "HINDUNILVR", "NESTLEIND", "BRITANNIA", "MARUTI", "SIEMENS",
            "ABB", "COLPAL", "CUMMINSIND", "ABBOTINDIA", "MCDOWELL-N",
            "HONAUT", "BOSCHLTD", "PFIZER", "SANOFI", "BATAINDIA"
        ],
        "NIFTY Dividend Opps 50": [
            "ITC", "HINDUNILVR", "TCS", "INFY", "HCLTECH", "POWERGRID",
            "ONGC", "COALINDIA", "VEDL", "IOC", "BPCL", "HINDZINC",
            "PETRONET", "NHPC", "RECLTD", "PFC"
        ],
        "NIFTY EV & New Age Auto": [
            "TATAMOTORS", "M&M", "EXIDEIND", "AMARAJABAT", "MOTHERSON",
            "TATACHEM", "OLECTRA", "JBMA", "TVSMOTOR", "SONACOMS",
            "GREAVESCOT"
        ],
        "NIFTY ESG": [
            "INFY", "TCS", "HDFCBANK", "TITAN", "WIPRO", "TECHM",
            "HCLTECH", "HAVELLS", "GODREJCP", "LT", "KOTAKBANK",
            "MARICO", "ASIANPAINT", "APOLLOHOSP"
        ]
    },
    "🧠 NIFTY Strategy & Factor": {
        "NIFTY Alpha 50": ["BHARTIARTL", "BAJFINANCE", "MARUTI", "M&M", "ZOMATO", "TRENT", "ADANIENT", "HAL", "BEL", "INDIGO"],
        "NIFTY Momentum 30": ["HDFCBANK", "ICICIBANK", "BHARTIARTL", "TRENT", "BEL", "COALINDIA", "NTPC", "TATAMOTORS", "BAJFINANCE"],
        "NIFTY Low Volatility 30": ["RELIANCE", "HDFCBANK", "TCS", "SBIN", "CIPLA", "SUNPHARMA", "HINDUNILVR", "ITC", "POWERGRID", "INFY"],
        "NIFTY Quality 30": ["HDFCBANK", "INFY", "NESTLEIND", "ITC", "COALINDIA", "HCLTECH", "BRITANNIA", "HINDUNILVR", "TCS", "ASIANPAINT"],
        "NIFTY Growth Sectors 15": ["TCS", "INFY", "M&M", "BAJFINANCE", "TITAN", "MARUTI", "SUNPHARMA", "EICHERMOT", "HINDUNILVR", "CIPLA"],
        "NIFTY Shariah 25": ["ULTRACEMCO", "LTIM", "DIVISLAB", "CUMMINSIND", "RELIANCE", "TCS", "INFY", "HCLTECH", "ASIANPAINT", "TITAN"]
    }
}

START_DATE = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')
RISK_FREE_RATE = 0.05

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def download_data(tickers):
    if not tickers: return pd.DataFrame()
    tickers = [t + ".NS" if not t.endswith(".NS") else t for t in tickers]
    try:
        data = yf.download(tickers, start=START_DATE, end=END_DATE, progress=False, group_by='ticker')
    except: return pd.DataFrame()
    
    adj = pd.DataFrame()
    for t in tickers:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if (t, "Adj Close") in data.columns: adj[t] = data[(t, "Adj Close")]
                elif (t, "Close") in data.columns: adj[t] = data[(t, "Close")]
            else:
                if "Adj Close" in data.columns: adj[t] = data["Adj Close"]
                elif "Close" in data.columns: adj[t] = data["Close"]
        except: pass
    
    adj.columns = [c.replace(".NS", "") for c in adj.columns]
    adj = adj.ffill().bfill().dropna(axis=1, thresh=int(0.8 * len(adj)))
    return adj

def calculate_score(adj_df):
    if adj_df.empty: return pd.DataFrame()
    ret = adj_df.pct_change().dropna()
    days = (adj_df.index[-1] - adj_df.index[0]).days
    if days < 365: return pd.DataFrame() 
    years = days / 365.25
    cagr = ((adj_df.iloc[-1] / adj_df.iloc[0]) ** (1 / years)) - 1
    vol = ret.std() * np.sqrt(252)
    sharpe = (ret.mean() * 252 - RISK_FREE_RATE) / vol
    cum_max = adj_df.cummax()
    drawdown = (adj_df / cum_max) - 1
    max_dd = drawdown.min()
    
    metrics = pd.DataFrame({"CAGR": cagr, "Sharpe": sharpe, "Vol": vol, "MaxDD": max_dd})
    
    metrics["Score"] = (
        (metrics["CAGR"].rank(pct=True) * 0.4) +
        (metrics["Sharpe"].rank(pct=True) * 0.2) +
        (metrics["MaxDD"].rank(pct=True) * 0.2) + 
        (metrics["Vol"].rank(pct=True, ascending=False) * 0.2)
    ) * 100
    
    return metrics.sort_values("Score", ascending=False).head(5)

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

# --- CSS for Button & Card ---
st.markdown("""
<style>
    /* Button Styling */
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
    
    /* ADDED: Score Suffix Style */
    .score-suffix { font-size: 0.6em; color: inherit; font-weight: 800; opacity: 0.9; }

    .score-label { font-size: 0.9rem; color: #64748b; font-weight: 500; }
    
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding-top: 15px; border-top: 1px solid #f1f5f9; }
    .metric-item { display: flex; flex-direction: column; }
    .metric-item.right { align-items: flex-end; text-align: right; }
    .metric-label { font-size: 0.8rem; font-weight: 700; color: #64748b; margin-bottom: 2px; }
    .metric-val { font-size: 1rem; font-weight: 600; color: #334155; }
</style>
""", unsafe_allow_html=True)

# --- ANALYZE LOGIC ---
if start_analysis:
    st.write("---")
    progress_bar = st.progress(0)
    total = len(target_indices)
    
    for i, (cat, idx_name, tickers) in enumerate(target_indices):
        st.markdown(f"### 🔎 {idx_name}")
        
        with st.spinner(f"📥 Crunching numbers for {len(tickers)} stocks..."):
            data = download_data(tickers)
            
            if data.empty:
                st.warning(f"⚠️ No data available for {idx_name}")
            else:
                top_picks = calculate_score(data)
                cols = st.columns(len(top_picks))
                
                for j, (sym, row) in enumerate(top_picks.iterrows()):
                    with cols[j]:
                        # HTML Card
                        html_content = (
                            f'<div class="stock-card">'
                            f'<div class="card-header"><div class="stock-rank">#{j+1} {sym}</div></div>'
                            # UPDATED: Added Score Suffix
                            f'<div class="score-container"><div class="big-score">{row["Score"]:.1f}<span class="score-suffix">/100</span></div><div class="score-label">Decision Score</div></div>'
                            f'<div class="metrics-grid">'
                            f'<div class="metric-item"><div class="metric-label">CAGR</div><div class="metric-val">{row["CAGR"]*100:.1f}%</div></div>'
                            f'<div class="metric-item right"><div class="metric-label">Max DD</div><div class="metric-val" style="color: #ef4444;">{row["MaxDD"]*100:.1f}%</div></div>'
                            f'<div class="metric-item"><div class="metric-label">Sharpe</div><div class="metric-val">{row["Sharpe"]:.2f}</div></div>'
                            f'<div class="metric-item right"><div class="metric-label">Vol</div><div class="metric-val">{row["Vol"]*100:.1f}%</div></div>'
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
        * **CAGR (Compound Annual Growth Rate):** Average yearly growth of stock price.       
        * **Max Drawdown:** Biggest price fall from peak to bottom. Lower = safer.  
        * **Sharpe Ratio:** Measures how much return you earn for the risk you take. Higher = better.
        * **Sortino Ratio:** Like Sharpe, but only counts downside (bad) volatility. Higher = safer returns.
        * **Calmar Ratio:** Compares yearly return vs biggest loss. Higher = strong recovery ability.
        * **Volatility:** How much the stock price moves up or down. Lower = more stable.
        * **Beta:** How much the stock moves compared to market (1 = same as market, <1 = safer).
        * **Recovery Days:** Time it takes for stock to recover after big fall. Fewer = better.
        * **Decision Score:** Final 0–100 score combining all metrics for beginner investors.
        """)

# ==========================================
# 5. FOOTER / NAVIGATION (EXACT COPY OF BLUECHIP)
# ==========================================
st.write("")
st.write("---")
st.write("")

# Specific CSS for the Footer Buttons (same as Beginner page)
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
c_back, _, _ = st.columns([1, 4, 1])
with c_back:
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/beginner.py")

_, c_dash, _ = st.columns([5, 2, 5])
with c_dash:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        st.switch_page("app.py")