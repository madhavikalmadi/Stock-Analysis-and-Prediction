import sys
import os
import streamlit as st

st.set_page_config(page_title="Smart Investor Dashboard", layout="wide")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import auth_utils
# --- RESTORED IMPORTS ---
import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime


# =====================================================
# 🔁 RESTORE SESSION FROM URL (VERY IMPORTANT)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔐 AUTH GUARD (AFTER RESTORE)
# =====================================================
# Dashboard already guarantees authentication or admin access
if not st.session_state.get("authenticated") and not st.session_state.get("is_admin"):
    # If no session, double check params as a final fallback
    if "user_id" not in params or "username" not in params:
        st.switch_page("login.py")
        st.stop()


# Sync params for navigation persistence
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# =============================================================
# SESSION STATE INIT
# =============================================================
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""


# =============================================================
# CSS ENGINE
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

/* Hide sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Global font */
body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif !important;
    overflow-x: hidden;
}

/* Hide deploy button, menu, spinners */
.stAppDeployButton { display: none !important; }
#MainMenu, footer { visibility: hidden; height: 0; }
[data-testid*="stProgress"],
[data-testid*="stSpinner"],
.stAlert:has(.stSpinner) { display: none !important; }

/* Hide native Streamlit header */
[data-testid="stHeader"] {
    display: none !important;
    visibility: hidden;
    height: 0;
}

/* REMOVE HEADER ANCHORS */
[data-testid="stMarkdownContainer"] h1 a,
[data-testid="stMarkdownContainer"] h2 a,
[data-testid="stMarkdownContainer"] h3 a,
[data-testid="stMarkdownContainer"] h4 a,
[data-testid="stMarkdownContainer"] h5 a,
[data-testid="stMarkdownContainer"] h6 a {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# DYNAMIC THEME CSS
# Fixed Light Mode Colors
top_bar_bg = '#eff6ff'
top_bar_text = '#1e3a8a'

st.markdown(f"""
<style>
/* ==== CUSTOM FIXED HEADER BAR ==== */
.custom-top-bar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px; /* Taller header */
    background: {top_bar_bg};
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    display: flex;
    align-items: center; /* Ensures vertical centering */
    padding: 0 2rem; 
    z-index: 99990;
}}
.custom-top-bar-title {{
    font-weight: 800;
    font-size: 1.2rem;
    color: {top_bar_text};
    margin: 0 !important; 
}}

/* Container for search and profile buttons */
.nav-buttons-container {{
    margin-left: auto; /* Push buttons to the right */
    display: flex; 
    align-items: center;
    gap: 10px; /* Space between search and profile buttons */
    height: 100%; 
}}

/* ===== SEARCH ICON STYLES (HTML Anchor) ===== */
.search-btn-style {{
    background: none;
    color: #1e3a8a !important;
    padding: 0.5rem 0.8rem; 
    border-radius: 999px;
    font-size: 1.1rem;
    border: 2px solid #3b82f6; /* Subtle blue border */
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    text-decoration: none !important; 
    display: inline-block; 
}}
.search-btn-style:hover {{
    background: #dbeafe; /* Very light blue background on hover */
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2);
}}

/* ===== PROFILE BUTTON STYLES (PURE HTML ANCHOR STYLES) ===== */
.profile-btn-style {{
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
    padding: 0.5rem 1.2rem; 
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    border: none;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    transition: all 0.3s ease;
    text-decoration: none !important; 
    white-space: nowrap;
    /* animation: pulse 2s infinite; REMOVED */
    display: inline-block; 
}}

.profile-btn-style:hover {{
    transform: translateY(-2px); 
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}}

/* Main container (push content below custom bar) */
.block-container {{
    padding-top: 3.5rem !important; /* SIGNIFICANTLY REDUCED to 3.5rem */
    padding-bottom: 5rem !important;
    max-width: 1200px;
    position: relative;
    z-index: 1;
}}
</style>
""", unsafe_allow_html=True)

# STATIC ANIMATION CSS (Must be separate to avoid f-string syntax errors with keyframes)
st.markdown("""
<style>
/* ANIMATION KEYFRAMES (Keeping all existing animations) */
@keyframes cloud-move {
    0% { transform: translate(0, 0); }
    100% { transform: translate(30px, 30px); }
}
@keyframes marquee {
    0% { transform: translate3d(0, 0, 0); } 
    100% { transform: translate3d(-100%, 0, 0); }
}
@keyframes popIn {
    0% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1); }
}
@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes slideUp { 
    from { opacity: 0; transform: translateY(20px); } 
    to { opacity: 1; transform: translateY(0); } 
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
@keyframes fadeInSlideUp { 
    from { opacity: 0; transform: translateY(10px); } 
    to { opacity: 1; transform: translateY(0); } 
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

/* ticker */
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
    animation: marquee 15s linear infinite;
    width: 100%;
}
.ticker__item { 
    display: inline-block;
    padding: 0 2rem;
    font-size: 0.9rem;
    font-weight: 600;
}

/* Hero */
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

/* Cards and Pathways styles (unchanged) */
.glass-panel {
    background: rgba(255, 255, 255, 0.95); /* Increased contrast */
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 1);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
    transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.glass-panel:hover .card-icon { transform: scale(1.2) rotate(10deg); }
.card-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 0.8rem; }
.card-desc { font-size: 0.95rem; line-height: 1.6; opacity: 0.8; }

.path-card {
    background: rgba(255, 255, 255, 0.95); /* Nearly solid white for contrast */
    border: 1px solid rgba(255, 255, 255, 1);
    border-radius: 30px; 
    padding: 3rem 2rem; 
    box-shadow: 0 10px 40px rgba(0,0,0,0.1); 
    text-align: center; 
    height: 100%; 
    min-height: 350px;
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    align-items: center;
    position: relative; 
    overflow: hidden; 
    transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1); 
    z-index: 2; 
    animation: slideUp 0.8s ease-out both; 
}
.p-left { animation-delay: 0.6s; } 
.p-right { animation-delay: 0.8s; } 

.path-description-animated {
    opacity: 0; 
    animation: fadeInSlideUp 0.5s ease-out 1.2s both; 
}
.p-right .path-description-animated {
    animation-delay: 1.4s; 
}


.path-card:hover { 
    transform: translateY(-12px); 
    background: rgba(255, 255, 255, 0.85); 
    box-shadow: 0 20px 50px rgba(0,0,0,0.1); 
    border: 1px solid rgba(255, 255, 255, 1); 
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

/* Buttons */
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
div.stButton > button * { color: white !important; }
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
}

/* Banner & footer */
.insight-box {
    border-left: 5px solid #10b981;
    padding: 1.2rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 3rem;
    font-weight: 500;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    animation: slideUp 1s ease-out;
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
    max-width: 100%; /* Changed from 800px to ensure it fills the center aligned container */
    margin: 0 auto 1rem auto;
    line-height: 1.5;
    opacity: 0.7;
    text-align: center; 
}


/* ============================================= */
/* HEADER BUTTONS OVERLAY (Robust Selector)      */
/* ============================================= */
/* Hide the marker container */
div.element-container:has(#header-ctl-marker) {
    display: none;
}

/* Target the row containing the marker */
div[data-testid="stHorizontalBlock"]:has(#header-ctl-marker) {
    position: fixed;
    top: 12px; /* Vertically aligned in the 70px header */
    right: 2rem;
    width: auto !important;
    height: auto;
    z-index: 999999;
    background: transparent;
    pointer-events: none; /* Allow clicks to pass through empty space */
}

div[data-testid="stHorizontalBlock"]:has(#header-ctl-marker) [data-testid="column"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0;
}

div[data-testid="stHorizontalBlock"]:has(#header-ctl-marker) button {
    pointer-events: auto;
    margin: 0 !important;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.4rem 1rem !important;
    font-weight: 600 !important;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    transition: all 0.3s;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
}
div[data-testid="stHorizontalBlock"]:has(#header-ctl-marker) button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
}
div[data-testid="stHorizontalBlock"]:has(#header-ctl-marker) button p {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# CUSTOM FIXED HEADER BAR (TITLE, SEARCH, AND PROFILE BUTTONS)
# =============================================================
st.markdown("""
<div class="custom-top-bar">
    <div class="custom-top-bar-title">Smart Investor Assistant</div>
</div>
""", unsafe_allow_html=True)

# Buttons positioned by CSS to sit INSIDE the fixed header
# The marker is placed inside the first column so the parent row can be targeted by :has()
bh_col1, bh_col2 = st.columns([1, 1], gap="small")

with bh_col1:
    st.markdown('<span id="header-ctl-marker"></span>', unsafe_allow_html=True)
    if st.button("🔍 Search", key="header_search_btn"):
        # Pre-set params so Search page has them immediately
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/search.py")

with bh_col2:
    if st.button("👤 Profile", key="header_profile_btn"):
        # Pre-set params so Profile page has them immediately
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/profile.py")


# =============================================================
# FEATURE 1: EDUCATIONAL TICKER
# =============================================================

@st.cache_data(ttl=900, show_spinner=False)
def get_market_data_tape(tickers):
    try:
        data = yf.download(tickers, period="2d", group_by='ticker', threads=True, progress=False)
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
    except Exception:
        pass

    if stock_data.empty:
        return f"{name}: N/A"

    try:
        # Handle case where column might be 'Close' or just the ticker itself depending on download
        if 'Close' in stock_data.columns:
            valid_history = stock_data['Close'].dropna()
        else:
             # Fallback if structure is different
            valid_history = stock_data.iloc[:, 0].dropna()
            
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
    except Exception:
        return f"{name}: N/A"

@st.fragment(run_every=300) 
def show_auto_ticker():
    universe = {
        "INDICES": {
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX"
        },
        "BANKING": { "HDFCBANK.NS": "HDFC Bank" },
        "PSU BANK": { "SBIN.NS": "SBI" },
        "IT": { "TCS.NS": "TCS" },
        "AUTO": { "MARUTI.NS": "Maruti" },
        "FMCG": { "HINDUNILVR.NS": "HUL" },
        "ENERGY": { "RELIANCE.NS": "Reliance" },
        "SERVICES": { "INDIGO.NS": "IndiGo" },
        "REALTY": { "DLF.NS": "DLF" },
        "PHARMA": { "SUNPHARMA.NS": "Sun Pharma" },
        "INFRA": { "LT.NS": "Larsen & Toubro" },
        "METAL": { "TATASTEEL.NS": "Tata Steel" },
        "FINANCE": { "BAJFINANCE.NS": "Bajaj Finance" },
        "CONSUMER": { "TITAN.NS": "Titan" },
        "POWER": { "NTPC.NS": "NTPC" },
        "HEALTH": { "APOLLOHOSP.NS": "Apollo Hosp" },
        "DEFENCE": { "HAL.NS": "HAL" },
        "PAINTS": { "ASIANPAINT.NS": "Asian Paints" },
        "TELECOM": { "BHARTIARTL.NS": "Airtel" },
        "MINING": { "COALINDIA.NS": "Coal India" },
        "MEDIA": { "SUNTV.NS": "Sun TV" },
        "CEMENT": { "ULTRACEMCO.NS": "UltraTech" },
        "OIL & GAS": { "ONGC.NS": "ONGC" },
        "DIVERSIFIED": { "ADANIENT.NS": "Adani Ent" },
        "PORTS": { "ADANIPORTS.NS": "Adani Ports" }
    }
        
    selected_tickers = []
    symbol_map = {}
        
    for category in universe:
        for symbol, display_name in universe[category].items():
            selected_tickers.append(symbol)
            symbol_map[symbol] = display_name

    # --- PERFORMANCE OPTIMIZATION: SESSION CACHING ---
    # Store ticker data in session status to ensure INSTANT loading on navigation.
    if 'ticker_cache_data' not in st.session_state:
        st.session_state['ticker_cache_data'] = None
    
    # Try to get data
    batch_data = st.session_state['ticker_cache_data']

    # If empty, fetch immediately (first load might still take a moment, but subsequent navigation is instant)
    if batch_data is None or batch_data.empty:
        batch_data = get_market_data_tape(selected_tickers)
        st.session_state['ticker_cache_data'] = batch_data

    ticker_items = []
    if batch_data is not None and not batch_data.empty:   
        for sym in selected_tickers:
            if sym in symbol_map:
                name = symbol_map[sym]
                ticker_items.append(format_ticker_item(sym, name, batch_data))
        
    if not ticker_items:
        ticker_items = ["Loading Data..."]

    # Duplicate content for seamless marquee effect
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
# HERO & MARKET STATUS
# =============================================================

def get_market_status():
    try:
        # Check Indian Stock Market hours (9:15 AM to 3:30 PM IST, Mon-Fri)
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
st.markdown("<h3 style='margin-bottom:1.5rem; font-weight:700;'>🧠 Learn the Basics</h3>", unsafe_allow_html=True)

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

# BUTTON: Go to Knowledge Hub
if st.button("📚 Go to Knowledge Hub"):
    # Preserve session state in query params
    if "user_id" in st.session_state:
        st.query_params["user_id"] = st.session_state.user_id
    if "username" in st.session_state:
        st.query_params["username"] = st.session_state.username
    st.switch_page("pages/stock_details.py")

# =============================================================
# PATHWAYS (Animation added to inner description text)
# =============================================================
st.markdown("<h3 style='margin-top:3rem; margin-bottom:1.5rem; font-weight:700;'>🚀 Choose Your Path</h3>", unsafe_allow_html=True)

col_path1, col_path2 = st.columns(2, gap="large")

# Get current session details for links
import urllib.parse
user_id = st.session_state.get("user_id", "")
username = st.session_state.get("username", "")
params_str = ""
if user_id and username:
    safe_user = urllib.parse.quote(str(user_id))
    safe_name = urllib.parse.quote(str(username))
    params_str = f"?user_id={safe_user}&username={safe_name}"

with col_path1:
    st.markdown(f"""
    <a href="beginner{params_str}" target="_self" style="text-decoration:none; color:inherit; display:block; height:100%;">
        <div class="path-card p-left">
            <div class="path-icon">🌱</div>
            <div class="path-title">Beginner</div>
            <div class="path-description-animated" style="opacity:0.8; margin-bottom:1rem;">Safe, steady, and simple. Perfect for your first steps.</div>
            <div class="chip-group">
                <span class="chip">Blue-Chip</span>
                <span class="chip">Large Cap</span>
                <span class="chip">Low Volatility</span>
                <span class="chip">NIFTY 50</span>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    st.write("") 
    if st.button("Start Beginner Journey", key="btn_beg"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
        st.switch_page("pages/beginner.py")

with col_path2:
    st.markdown(f"""
    <a href="reinvestor{params_str}" target="_self" style="text-decoration:none; color:inherit; display:block; height:100%;">
        <div class="path-card p-right">
            <div class="path-icon">🔁</div>
            <div class="path-title">Reinvestor</div>
            <div class="path-description-animated" style="opacity:0.8; margin-bottom:1rem;">Growth-focused strategies for experienced players.</div>
            <div class="chip-group">
                <span class="chip">Mid Cap</span>
                <span class="chip">Small Cap</span>
                <span class="chip">High Growth</span>
                <span class="chip">Sector Rotation</span>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    st.write("") 
    if st.button("Start Reinvestor Journey", key="btn_inv"):
        # Preserve session state in query params
        if "user_id" in st.session_state:
            st.query_params["user_id"] = st.session_state.user_id
        if "username" in st.session_state:
            st.query_params["username"] = st.session_state.username
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