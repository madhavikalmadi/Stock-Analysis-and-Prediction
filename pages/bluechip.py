import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. PAGE CONFIG & CSS ---
st.set_page_config(page_title="Bluechip Explorer", layout="wide")

st.markdown("""
<style>
    /* --- FORCE HIDE HEADER ANCHORS (UPDATED FIX) --- */
    [data-testid="stHeaderActionElements"] { display: none !important; visibility: hidden !important; }
    [data-testid="stHeaderAnchor"] { display: none !important; visibility: hidden !important; }
    h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a { display: none !important; content: none !important; pointer-events: none; color: transparent !important; }
    
    /* --- ANIMATION DEFINITIONS --- */
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
    @keyframes slideInDown { from { opacity: 0; transform: translate3d(0, -100%, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }

    /* --- COMPONENT STYLING --- */
    .main-title { animation: slideInDown 0.8s ease-out; }

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
    .metric-row { font-size: 0.85em; color: #555; margin-top: 10px; display: flex; justify-content: space-between; }
    .metric-item { text-align: center; }
    .section-title { font-size: 1.2em; font-weight: bold; color: #333; margin-top: 30px; margin-bottom: 10px; border-bottom: 2px solid #ddd; padding-bottom: 5px; animation: fadeInUp 1s ease-out; }
    
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: scale(0.95); }
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURATION & DATA ---
START_DATE = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')
RISK_FREE_RATE = 0.05

BLUECHIP = [
    "ADANIENT","ADANIPORTS","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE",
    "BHARTIARTL","BPCL","BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY","EICHERMOT",
    "GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO","HINDUNILVR",
    "ICICIBANK","INDUSINDBK","INFY","ITC","JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI",
    "NESTLEIND","NTPC","ONGC","POWERGRID","RELIANCE","SBILIFE","SBIN","SUNPHARMA",
    "TATACONSUM","TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]

# --- 3. HELPER FUNCTIONS ---

@st.cache_data(show_spinner=False)
def download_adj_close(tickers):
    tickers_ns = [t + ".NS" for t in tickers]
    try:
        raw = yf.download(tickers_ns, start=START_DATE, end=END_DATE, progress=False, group_by="ticker", threads=False)
    except Exception:
        return pd.DataFrame()
        
    adj = pd.DataFrame()
    for t in tickers_ns:
        sym = t.replace(".NS", "")
        try:
            if "Adj Close" in raw[t].columns:
                adj[sym] = raw[t]["Adj Close"]
            elif "Close" in raw[t].columns:
                adj[sym] = raw[t]["Close"]
            else:
                adj[sym] = raw.filter(like=sym).iloc[:, 0]
        except Exception:
            pass
    adj = adj.ffill().bfill()
    adj = adj.dropna(axis=1, thresh=int(0.80 * len(adj)))
    return adj

def compute_cagr(series):
    s = series.dropna()
    if s.empty: return np.nan
    years = (s.index[-1] - s.index[0]).days / 365.25
    return (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1

def downside_std(returns):
    neg = returns[returns < 0]
    return neg.std() if not neg.empty else 0

def rolling_recovery_days(price):
    s = price.dropna()
    if s.empty: return np.nan
    peak, last_peak = s.iloc[0], s.index[0]
    max_days = 0
    for date, val in s.items():
        if val >= peak:
            peak = val
            last_peak = date
        else:
            days_under = (date - last_peak).days
            if days_under > max_days:
                max_days = days_under
    return max_days

@st.cache_data(show_spinner=False)
def calculate_metrics_and_score(adj):
    returns = adj.pct_change().dropna()
    nifty_ref = yf.download("^NSEI", start=START_DATE, end=END_DATE, progress=False)
    
    if "Adj Close" in nifty_ref.columns:
        nifty_series = nifty_ref["Adj Close"]
    elif "Close" in nifty_ref.columns:
        nifty_series = nifty_ref["Close"]
    else:
        nifty_series = nifty_ref.iloc[:, 0]
    nifty_ret = nifty_series.pct_change().dropna()

    results = {}
    for sym in adj.columns:
        px = adj[sym]
        ret = returns[sym]
        if ret.isna().sum() > len(ret) * 0.5: continue

        cagr = compute_cagr(px)
        ann_vol = ret.std() * np.sqrt(252)
        ann_ret = ret.mean() * 252
        sharpe = (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else np.nan
        down = downside_std(ret) * np.sqrt(252)
        sortino = (ann_ret - RISK_FREE_RATE) / down if down > 0 else np.nan
        
        roll_max = px.cummax()
        dd = (px / roll_max) - 1
        max_dd = dd.min()
        calmar = ann_ret / abs(max_dd) if max_dd < 0 else np.nan
        
        common = ret.index.intersection(nifty_ret.index)
        aligned = pd.concat([ret.loc[common], nifty_ret.loc[common]], axis=1).dropna()
        if len(aligned) > 100 and np.var(aligned.iloc[:, 1]) > 0:
            beta = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1] / np.var(aligned.iloc[:, 1])
        else:
            beta = np.nan
            
        rec_days = rolling_recovery_days(px)

        results[sym] = {
            "CAGR_10Y": cagr, "Sharpe": sharpe, "Sortino": sortino, "Calmar": calmar,
            "Volatility": ann_vol, "Max_Drawdown": max_dd, "Beta": beta, "Recovery_Days": rec_days
        }
    
    metrics_df = pd.DataFrame(results).T
    
    weights = {
        "CAGR_10Y": 25, "Sharpe": 15, "Sortino": 10, "Calmar": 10,
        "Volatility": 10, "Max_Drawdown": 10, "Beta": 5, "Recovery_Days": 5
    }
    
    def normalize(v, cap): return max(0, min(v / cap, 1)) if pd.notna(v) else 0
    def inverse(v, cap): return max(0, min(1 - v / cap, 1)) if pd.notna(v) else 0
    def dd_norm(v): return max(0, min(1 - abs(v) / 0.6, 1)) if pd.notna(v) else 0
    def beta_norm(v):
        if pd.isna(v): return 0.5
        v = float(v)
        if v <= 1.2: return 1 - abs(v - 1) / 0.4
        return max(0, 1 - (v - 1.2) / 0.8)

    def score_row(row):
        s = 0
        s += normalize(row["CAGR_10Y"], 0.20) * weights["CAGR_10Y"]
        s += normalize(row["Sharpe"], 1.5) * weights["Sharpe"]
        s += normalize(row["Sortino"], 2.0) * weights["Sortino"]
        s += normalize(row["Calmar"], 1.5) * weights["Calmar"]
        s += inverse(row["Volatility"], 0.35) * weights["Volatility"]
        s += dd_norm(row["Max_Drawdown"]) * weights["Max_Drawdown"]
        s += beta_norm(row["Beta"]) * weights["Beta"]
        s += inverse(row["Recovery_Days"], 800) * weights["Recovery_Days"]
        return (s / sum(weights.values())) * 100

    metrics_df["Decision_Score"] = metrics_df.apply(score_row, axis=1)
    return metrics_df.sort_values("Decision_Score", ascending=False)

# --- 4. MAIN PAGE LAYOUT ---

st.markdown('<h1 class="main-title">🚀 Blue-Chip Explorer</h1>', unsafe_allow_html=True)
st.markdown("### Top 10 Recommendations based on 10-Year History")
st.markdown("---")

with st.spinner("📥 Downloading market data & calculating scores..."):
    try:
        adj_data = download_adj_close(BLUECHIP)
        if adj_data.empty:
            st.error("No data found. Please check your internet connection.")
        else:
            ranked_stocks = calculate_metrics_and_score(adj_data)
            top10 = ranked_stocks.head(10)

            for i in range(0, 10, 5):
                cols = st.columns(5)
                batch = top10.iloc[i:i+5]
                
                for idx, (sym, row) in enumerate(batch.iterrows()):
                    with cols[idx]:
                        # DELAY CALCULATION
                        delay = (i + idx) * 0.1 
                        
                        st.markdown(f"""
                        <div class="stock-card" style="animation-delay: {delay}s;">
                            <h4>#{i + idx + 1} {sym}</h4>
                            <div class="big-score">{row["Decision_Score"]:.1f}</div>
                            <small>Decision Score</small>
                            <hr style="margin: 10px 0; opacity: 0.3;">
                            <div class="metric-row">
                                <div class="metric-item"><b>CAGR</b><br>{row['CAGR_10Y']*100:.1f}%</div>
                                <div class="metric-item"><b>Max DD</b><br>{row['Max_Drawdown']*100:.1f}%</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-item"><b>Sharpe</b><br>{row['Sharpe']:.2f}</div>
                                <div class="metric-item"><b>Vol</b><br>{row['Volatility']*100:.1f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.write("") 

            st.markdown("---")
            
            st.markdown('<div class="section-title" style="animation-delay: 1.2s; animation-fill-mode: backwards;">✅ Interpretation</div>', unsafe_allow_html=True)
            st.info("""
            * **Higher CAGR** = Stronger long-term growth.
            * **Sharpe > 0.5** = Steady, risk-adjusted returns.
            * **Lower Volatility & Drawdown** = Safer investment.
            * **Beta < 1** = Stock moves less than the market (safer).
            * **Lower Recovery Days** = Quicker bounce-back after dips.
            """)

            st.markdown('<div class="section-title">🧾 Explanation of Terms</div>', unsafe_allow_html=True)
            with st.expander("Show Detailed Definitions", expanded=False):
                st.markdown("""
                * **CAGR (Compound Annual Growth Rate):** Average yearly growth of stock price.
                * **Sharpe Ratio:** Measures how much return you earn for the risk you take. Higher = better.
                * **Sortino Ratio:** Like Sharpe, but only counts downside (bad) volatility. Higher = safer returns.
                * **Calmar Ratio:** Compares yearly return vs biggest loss. Higher = strong recovery ability.
                * **Volatility:** How much the stock price moves up or down. Lower = more stable.
                * **Max Drawdown:** Biggest price fall from peak to bottom. Lower = safer.
                * **Beta:** How much the stock moves compared to market (1 = same as market, <1 = safer).
                * **Recovery Days:** Time it takes for stock to recover after big fall. Fewer = better.
                * **Decision Score:** Final 0–100 score combining all metrics for beginner investors.
                """)

            # ==========================================
            # FOOTER
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

    except Exception as e:
        st.error(f"An error occurred: {e}")