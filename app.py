import streamlit as st
import time
from datetime import datetime
import pytz 
import yfinance as yf 
import pandas as pd

# --- IMPORT LOCAL MODULES ---
try:
    from theme_manager import get_theme, apply_theme
except ImportError:
    # Fallback if file is missing
    def get_theme(): return "light"
    def apply_theme(t): pass

# =============================================================
# CONFIGURATION
# =============================================================
st.set_page_config(
    page_title="Smart Investor Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Sidebar Navigation
st.markdown("""
<style>
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Theme Application
try:
    theme = get_theme()
    apply_theme(theme)
except:
    pass

# =============================================================
# CSS ENGINE (DEFINITIVE PLACEMENT)
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

/* GLOBAL FONT */
body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    overflow-x: hidden;
}

/* 1. HIDE NATIVE DEPLOY BUTTON */
.stAppDeployButton {
    display: none !important; 
    visibility: hidden !important;
}

/* 2. STYLE THE HEADER BAR (Keep it white) */
[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 1) !important;
    box-shadow: 0 1px 0 rgba(0,0,0,0.1); 
    z-index: 999990;
}

/* --- CUSTOM PROFILE BUTTON STYLES --- */
.profile-badge-link {
    /* Style to match a Streamlit Primary button */
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
    border: none;
    padding: 6px 14px;
    border-radius: 0.5rem; /* 8px */
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    
    /* Flex container for the icon and text */
    display: flex; 
    align-items: center;
    gap: 8px;
}

.profile-badge-link:hover {
    transform: translateY(-1px);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    box-shadow: 0 8px 10px rgba(37, 99, 235, 0.3);
}

.profile-pic {
    color: white; 
    font-size: 1rem;
}

.profile-badge-link span {
    color: white !important;
}

/* 3. INJECTION CONTAINER POSITIONING */
/* Use fixed position on the far top right, placed just to the left of the three dots menu */
#custom-profile-injection {
    position: fixed;
    top: 12px; 
    /* This value is calculated to place the button next to the three dots (which is at right: 20px) */
    right: 55px; 
    z-index: 999999;
    /* Important for responsiveness: if the screen is too narrow, make sure it flows */
    white-space: nowrap; 
}


/* --- REST OF YOUR EXISTING CSS BELOW --- */

/* --- REMOVE ANCHOR LINKS (Chain Icons) --- */
[data-testid="stMarkdownContainer"] h1 a,
[data-testid="stMarkdownContainer"] h2 a,
[data-testid="stMarkdownContainer"] h3 a,
[data-testid="stMarkdownContainer"] h4 a,
[data-testid="stMarkdownContainer"] h5 a,
[data-testid="stMarkdownContainer"] h6 a {
    display: none !important;
}

/* ANIMATED CLOUD BACKGROUND */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.8), transparent 50%),
        radial-gradient(circle at 80% 30%, rgba(219, 234, 254, 0.8), transparent 50%);
    filter: blur(60px);
    z-index: 0;
    animation: cloud-move 20s ease infinite alternate;
    pointer-events: none;
}

@keyframes cloud-move {
    0% { transform: translate(0, 0); }
    100% { transform: translate(30px, 30px); }
}

/* MAIN CONTAINER */
.block-container {
    /* Adjusted padding to account for the sticky header */
    padding-top: 3rem !important; 
    padding-bottom: 5rem !important;
    max-width: 1200px;
    position: relative;
    z-index: 1;
}

/* TICKER TAPE CSS */
.ticker-wrap {
    width: 100%;
    backdrop-filter: blur(5px);
    overflow: hidden;
    white-space: nowrap;
    border-radius: 8px;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.ticker-heading {
    background: #2563eb;
    color: white;
    padding: 8px 15px;
    font-weight: 800;
    font-size: 0.8rem;
    z-index: 10;
    border-radius: 8px 0 0 8px;
}
.ticker {
    display: inline-block;
    /* Fast Animation Speed */
    animation: marquee 25s linear infinite;
    width: 100%;
}
.ticker__item {
    display: inline-block;
    padding: 0 2rem;
    font-size: 0.9rem;
    font-weight: 600;
}
@keyframes marquee {
    0% { transform: translate3d(0, 0, 0); }
    100% { transform: translate3d(-100%, 0, 0); }
}

/* HERO SECTION */
.hero-container {
    text-align: center;
    margin-bottom: 2rem;
    animation: popIn 1s ease-out;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(45deg, #2563eb, #9333ea, #2563eb);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    margin-bottom: 0.5rem;
    animation: gradient-shift 5s ease infinite;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes popIn {
    0% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1); }
}

.static-subtitle {
    font-size: 1.2rem;
    font-weight: 500;
    margin: 0 auto;
    opacity: 0.8;
}

/* CARDS */
.glass-panel {
    backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    transition: all 0.4s ease;
    height: 100%;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    overflow: hidden;
    animation: slideUp 0.8s ease-out both; 
}
.c1 { animation-delay: 0.1s; }
.c2 { animation-delay: 0.3s; }
.c3 { animation-delay: 0.5s; }

.glass-panel:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 20px 40px rgba(37, 99, 235, 0.1);
}

.card-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: inline-block;
    transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.glass-panel:hover .card-icon { transform: scale(1.2) rotate(10deg); }

.card-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 0.8rem; }
.card-desc { font-size: 0.95rem; line-height: 1.6; opacity: 0.8; }

/* PATHWAY CARDS */
.path-card {
    border-radius: 24px;
    padding: 2.5rem;
    position: relative;
    transition: all 0.4s ease;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    animation: slideUp 0.8s ease-out both;
}
.p-left { animation-delay: 0.6s; }
.p-right { animation-delay: 0.8s; }

.path-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.path-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.8), transparent);
    transform: skewX(-25deg);
    transition: 0.5s;
    pointer-events: none;
}
.path-card:hover::before { left: 150%; transition: 0.7s ease-in-out; }

.path-icon {
    width: 60px; height: 60px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    transition: transform 0.6s ease;
    background: rgba(37, 99, 235, 0.1); 
}
.path-card:hover .path-icon {
    transform: rotateY(180deg);
    background: #2563eb;
    color: white !important;
}

.path-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; }

.chip-group { display: flex; flex-wrap: wrap; gap: 8px; margin: 1.5rem 0; }
.chip {
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.1);
}

/* BUTTONS - FIXED COLORS (for internal Streamlit buttons) */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important; 
    border: none;
    padding: 0.8rem;
    font-weight: 600;
    border-radius: 12px;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.9rem;
    box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
}

div.stButton > button * {
    color: white !important;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
}

/* BANNER & FOOTER */
.insight-box {
    border-left: 5px solid #10b981;
    padding: 1.2rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 3rem;
    font-weight: 500;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    animation: slideUp 1s ease-out;
}
@keyframes slideUp { 
    from { opacity: 0; transform: translateY(20px); } 
    to { opacity: 1; transform: translateY(0); } 
}

.faq-header { text-align:center; margin-top:3rem; font-weight: 700; }

.footer-box {
    text-align:center; 
    margin-top: 4rem; 
    padding: 2rem; 
    border-top: 1px solid rgba(255,255,255,0.5);
    border-radius: 20px 20px 0 0;
}
.disclaimer-text {
    font-size: 0.75rem; 
    max-width: 800px;
    margin: 0 auto 1rem auto;
    line-height: 1.5;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)


# =============================================================
# INJECT PROFILE BUTTON
# =============================================================
st.markdown("""
<div id="custom-profile-injection">
    <a class="profile-badge-link" href="/profile" target="_self">
        <div class="profile-pic">👤</div>
        <span>Profile</span>
    </a>
</div>
""", unsafe_allow_html=True)


# =============================================================
# FEATURE 1: EDUCATIONAL TICKER
# =============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_market_data_tape(tickers):
    try:
        data = yf.download(tickers, period="1mo", group_by='ticker', threads=True, progress=False)
        return data
    except Exception:
        return pd.DataFrame()

def format_ticker_item(symbol, name, batch_data):
    stock_data = pd.DataFrame()
    try:
        if batch_data is not None and not batch_data.empty:
            if isinstance(batch_data.columns, pd.MultiIndex):
                if symbol in batch_data.columns.get_level_values(0):
                    stock_data = batch_data.xs(symbol, axis=1, level=0)
            elif symbol in batch_data.columns:
                 stock_data = batch_data[[symbol]]
    except:
        pass

    if stock_data.empty or 'Close' not in stock_data.columns:
        return f"{name}: N/A"

    try:
        valid_history = stock_data['Close'].dropna()
        if valid_history.empty:
            return f"{name}: N/A"

        current_price = valid_history.iloc[-1]
        
        if len(valid_history) >= 2:
            prev_close = valid_history.iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
        else:
            change = 0.0

        arrow = "▲" if change >= 0 else "▼"
        color_style = "color: #16a34a;" if change >= 0 else "color: #dc2626;"
        
        return f"<span style='{color_style}'><b>{arrow} {name}</b>: {current_price:,.2f} ({change:+.2f}%)</span>"
    except:
        return f"{name}: N/A"

@st.fragment(run_every=300) 
def show_auto_ticker():
    universe = {
        "INDICES": { "^NSEI": "NIFTY 50", "^BSESN": "SENSEX" },
        "TYPES": { 
            "RELIANCE.NS": "RELIANCE", 
            "VOLTAS.NS": "VOLTAS", 
            "BAJFINANCE.NS": "BAJAJ FIN", 
            "COALINDIA.NS": "COAL IND", 
            "TATAMOTORS.NS": "TATA MOTORS", 
            "HINDUNILVR.NS": "HUL"
        },
        "SECTORS": { 
            "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC BK", "SUNPHARMA.NS": "SUN PHARMA", 
            "TATASTEEL.NS": "TATA STL", "POWERGRID.NS": "POWERGRID", "MARUTI.NS": "MARUTI"
        }
    }
    
    selected_tickers = []
    symbol_map = {}
    
    for category in universe:
        for symbol, display_name in universe[category].items():
            selected_tickers.append(symbol)
            symbol_map[symbol] = display_name
            
    batch_data = get_market_data_tape(selected_tickers)
    ticker_items = []
    
    for sym in selected_tickers:
        if sym in symbol_map:
            name = symbol_map[sym]
            ticker_items.append(format_ticker_item(sym, name, batch_data))
    
    if not ticker_items:
        ticker_items = ["Loading Data..."]

    content_str = "&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;".join(ticker_items)
    
    st.markdown(f"""
    <div class="ticker-wrap">
    <div class="ticker-heading">LIVE</div>
    <div class="ticker">
        <div class="ticker__item">{content_str} &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; {content_str}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

show_auto_ticker()

# =============================================================
# HEADER & MARKET STATUS
# =============================================================

def get_market_status():
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        is_weekday = now.weekday() < 5
        current_minutes = now.hour * 60 + now.minute
        market_open = 9 * 60 + 15
        market_close = 15 * 60 + 30
        
        if is_weekday and (market_open <= current_minutes <= market_close):
            return "🟢 Market is LIVE", "#ecfccb", "#3f6212" # Green
        else:
            return "🔴 Market is CLOSED", "#fee2e2", "#991b1b" # Red
    except:
        return "Status Unavailable", "#f1f5f9", "#475569"

status_text, bg_color, text_color = get_market_status()

st.markdown(f"""
<div class="hero-container">
<div class="hero-title">Smart Investor Assistant</div>
<div class="static-subtitle">Your personalized dashboard for smarter market decisions.</div>
<div style="display: flex; justify-content: center; margin-top: 1.5rem;">
<div style="background-color: {bg_color}; color: {text_color}; padding: 0.5rem 1.2rem; border-radius: 30px; font-weight: 700; font-size: 0.85rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.5); display: flex; align-items: center; gap: 10px;">
{status_text}
</div>
</div>
</div>
""", unsafe_allow_html=True)

# QUICK INSIGHT
st.markdown("""
<div class="insight-box">
    💡 <b>Market Insight:</b> Diversification isn't just about owning many stocks—it's about owning different <i>types</i> of stocks (Sectors, Caps) to reduce risk.
</div>
""", unsafe_allow_html=True)

# =============================================================
# LEARNING SECTION
# =============================================================
st.markdown("<h3 style='margin-bottom:1.5rem; font-weight:700; animation: slideUp 0.5s ease-out;'>🧠 Learn the Basics</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""<div class="glass-panel c1">
        <div class="card-icon">🍕</div>
        <div class="card-title">What is a Stock?</div>
        <div class="card-desc">Think of a company as a Pizza. Buying a "stock" means buying <b>one slice</b> of that pizza (profits).</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<div class="glass-panel c2">
        <div class="card-icon">🐂</div>
        <div class="card-title">Bull vs Bear</div>
        <div class="card-desc"><b>Bull:</b> Market going UP (Optimism).<br><b>Bear:</b> Market going DOWN (Fear).</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""<div class="glass-panel c3">
        <div class="card-icon">💰</div>
        <div class="card-title">Dividends vs Growth</div>
        <div class="card-desc"><b>Dividend:</b> Pays cash (Rent).<br><b>Growth:</b> Reinvests profit (Expansion).</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# BUTTON: Single line natural flow
if st.button("📚 Go to Knowledge Hub"):
    st.switch_page("pages/stock_details.py")

# =============================================================
# PATHWAYS
# =============================================================
st.markdown("<h3 style='margin-top:3rem; margin-bottom:1.5rem; font-weight:700; animation: slideUp 0.6s ease-out;'>🚀 Choose Your Path</h3>", unsafe_allow_html=True)

col_path1, col_path2 = st.columns(2, gap="large")

with col_path1:
    st.markdown("""<div class="path-card p-left">
        <div class="path-icon">🌱</div>
        <div class="path-title">Beginner</div>
        <div style="opacity:0.8; margin-bottom:1rem;">Safe, steady, and simple. Perfect for your first steps.</div>
        <div class="chip-group">
            <span class="chip">Blue-Chip</span>
            <span class="chip">Large Cap</span>
            <span class="chip">Low Volatility</span>
            <span class="chip">NIFTY 50</span>
        </div>
    </div>""", unsafe_allow_html=True)
    
    st.write("") 
    if st.button("Start Beginner Journey", key="btn_beg"):
        st.switch_page("pages/beginner.py")

with col_path2:
    st.markdown("""<div class="path-card p-right">
        <div class="path-icon">🔁</div>
        <div class="path-title">Reinvestor</div>
        <div style="opacity:0.8; margin-bottom:1rem;">Growth-focused strategies for experienced players.</div>
        <div class="chip-group">
            <span class="chip">Mid Cap</span>
            <span class="chip">Small Cap</span>
            <span class="chip">High Growth</span>
            <span class="chip">Sector Rotation</span>
        </div>
    </div>""", unsafe_allow_html=True)
    
    st.write("") 
    if st.button("Start Reinvestor Journey", key="btn_inv"):
        st.switch_page("pages/reinvestor.py")

# =============================================================
# FOOTER
# =============================================================
st.markdown("<h4 class='faq-header'>Frequently Asked Questions</h4>", unsafe_allow_html=True)

faq1, faq2 = st.columns(2)
with faq1:
    with st.expander("Is this tool free?"):
        st.write("Yes! This project is designed to help democratize stock analysis for educational purposes.")
    with st.expander("What data source is used?"):
        st.write("We use reliable financial APIs (yfinance) to fetch market data.")

with faq2:
    with st.expander("Is the data real-time?"):
        st.write("We fetch new data automatically. Note that exchange feeds via Yahoo Finance may have a small delay.")
    with st.expander("Can I trade directly here?"):
        st.write("No. This is an analysis dashboard. You must use your registered broker to place actual trades.")

st.markdown("""
<div class="footer-box">
    <p class="disclaimer-text">
        <b>DISCLAIMER:</b> This application is for educational purposes only. 
        It does not constitute financial advice, investment recommendations, or solicitation to buy/sell any securities. 
        Stock market investments are subject to market risks. Please consult a SEBI registered financial advisor before trading.
    </p>
    <div style="opacity:0.6; font-size:0.8rem; font-weight:600;">
        Smart Investor Assistant • v2.0 • Powered by Analytics
    </div>
</div>
""", unsafe_allow_html=True)