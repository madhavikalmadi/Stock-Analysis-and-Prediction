import streamlit as st
import pandas as pd
import yfinance as yf
import pytz
import time
from datetime import datetime

# =============================================================
# PAGE CONFIG
# =============================================================
st.set_page_config(
    page_title="Smart Investor Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================
# SESSION STATE INIT (NO AUTH)
# =============================================================
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# =============================================================
# GLOBAL CSS
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    overflow-x: hidden;
}

#MainMenu, footer, header {
    visibility: hidden;
    height: 0;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# CUSTOM HEADER
# =============================================================
st.markdown("""
<div style="
position:fixed;
top:0;
left:0;
right:0;
height:70px;
background:#eff6ff;
display:flex;
align-items:center;
padding:0 2rem;
z-index:9999;
box-shadow:0 2px 6px rgba(0,0,0,0.08);
">
<h3 style="margin:0;color:#1e3a8a;font-weight:800;">
Smart Investor Assistant
</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

# =============================================================
# MARKET STATUS
# =============================================================
def get_market_status():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    is_weekday = now.weekday() < 5
    minutes = now.hour * 60 + now.minute
    if is_weekday and 555 <= minutes <= 930:
        return "🟢 Market is LIVE", "#dcfce7", "#166534"
    return "🔴 Market is CLOSED", "#fee2e2", "#991b1b"

status_text, bg, fg = get_market_status()

st.markdown(f"""
<div style="text-align:center;margin-bottom:2rem;">
<h1 style="font-size:3rem;font-weight:800;
background:linear-gradient(45deg,#2563eb,#9333ea,#2563eb);
-webkit-background-clip:text;
color:transparent;">
Smart Investor Assistant
</h1>

<div style="
display:inline-block;
background:{bg};
color:{fg};
padding:8px 18px;
border-radius:999px;
font-weight:700;
">
{status_text}
</div>
</div>
""", unsafe_allow_html=True)

# =============================================================
# TICKER
# =============================================================
@st.cache_data(ttl=900)
def get_ticker_data(tickers):
    return yf.download(tickers, period="2d", group_by="ticker", progress=False)

tickers = {
    "^NSEI": "NIFTY 50",
    "^BSESN": "SENSEX",
    "RELIANCE.NS": "Reliance",
    "TCS.NS": "TCS",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys"
}

data = get_ticker_data(list(tickers.keys()))

ticker_items = []
for symbol, name in tickers.items():
    try:
        close = data[symbol]['Close'].dropna()
        price = close.iloc[-1]
        prev = close.iloc[-2]
        change = ((price - prev) / prev) * 100
        arrow = "▲" if change >= 0 else "▼"
        color = "#16a34a" if change >= 0 else "#dc2626"
        ticker_items.append(
            f"<span style='color:{color};font-weight:700'>{arrow} {name}: {price:.2f} ({change:+.2f}%)</span>"
        )
    except:
        pass

ticker_html = " &nbsp; | &nbsp; ".join(ticker_items)

st.markdown(f"""
<div style="
white-space:nowrap;
overflow:hidden;
padding:10px;
background:white;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.05);
margin-bottom:2rem;">
{ticker_html}
</div>
""", unsafe_allow_html=True)

# =============================================================
# INSIGHT
# =============================================================
st.info(
    "💡 Diversification is not about owning many stocks — it’s about owning different types of stocks."
)

# =============================================================
# LEARNING SECTION
# =============================================================
st.subheader("🧠 Learn the Basics")

c1, c2, c3 = st.columns(3)

with c1:
    st.success("🍕 **What is a Stock?**\n\nOwning a stock means owning a slice of a company.")
with c2:
    st.warning("🐂 **Bull vs Bear**\n\nBull = Market Up\nBear = Market Down")
with c3:
    st.info("💰 **Dividend vs Growth**\n\nDividend pays cash\nGrowth reinvests profit")

# =============================================================
# PATHWAYS
# =============================================================
st.subheader("🚀 Choose Your Path")

p1, p2 = st.columns(2)

with p1:
    st.markdown("""
    ### 🌱 Beginner
    Safe, stable, low-risk investing.
    """)
    if st.button("Start Beginner Journey"):
        st.switch_page("pages/beginner.py")

with p2:
    st.markdown("""
    ### 🔁 Reinvestor
    Growth-focused, higher risk strategies.
    """)
    if st.button("Start Reinvestor Journey"):
        st.switch_page("pages/reinvestor.py")

# =============================================================
# FOOTER
# =============================================================
st.markdown("""
<hr>
<p style="text-align:center;font-size:0.8rem;opacity:0.7;">
<b>DISCLAIMER:</b> Educational purpose only. Not financial advice.<br>
Smart Investor Assistant • Streamlit Demo
</p>
""", unsafe_allow_html=True)