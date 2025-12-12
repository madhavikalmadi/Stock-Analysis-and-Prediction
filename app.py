import streamlit as st
import time
from datetime import datetime
import pytz 
import yfinance as yf 
from theme_manager import get_theme, apply_theme

# =============================================================
# CONFIGURATION
# =============================================================
st.set_page_config(
    page_title="Smart Investor Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)
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
# CSS ENGINE (Ultra-Creative Light Mode)
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

/* --- REMOVE ANCHOR LINKS (Chain Icon) --- */
[data-testid="stMarkdownContainer"] h1 a,
[data-testid="stMarkdownContainer"] h2 a,
[data-testid="stMarkdownContainer"] h3 a,
[data-testid="stMarkdownContainer"] h4 a,
[data-testid="stMarkdownContainer"] h5 a,
[data-testid="stMarkdownContainer"] h6 a {
    display: none !important;
}

/* --- RESET & BASICS --- */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarNav"] {
    display: none !important;
}

body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    font-family: 'Outfit', sans-serif !important;
    color: #334155; 
    overflow-x: hidden;
}

/* --- ANIMATED CLOUD BACKGROUND --- */
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

/* --- MAIN CONTAINER --- */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 5rem !important;
    max-width: 1200px;
    position: relative;
    z-index: 1;
}

/* --- TICKER TAPE CSS --- */
.ticker-wrap {
    width: 100%;
    background-color: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(5px);
    overflow: hidden;
    white-space: nowrap;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.9);
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
    animation: marquee 60s linear infinite; /* Adjusted speed for 25 items */
}
.ticker__item {
    display: inline-block;
    padding: 0 2rem;
    font-size: 0.9rem;
    color: #334155;
    font-weight: 600;
}
@keyframes marquee {
    0% { transform: translate3d(0, 0, 0); }
    100% { transform: translate3d(-50%, 0, 0); }
}

/* --- HERO SECTION --- */
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

/* STATIC SUBTITLE */
.static-subtitle {
    font-size: 1.2rem;
    color: #475569;
    font-weight: 500;
    margin: 0 auto;
}

/* --- GLASSMOPHISM CARDS --- */
.glass-panel {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    transition: all 0.4s ease;
    height: 100%;
    min-height: 250px;
    position: relative;
    overflow: hidden;
    animation: slideUp 0.8s ease-out both; 
}

/* Staggered entrance delays */
.c1 { animation-delay: 0.1s; }
.c2 { animation-delay: 0.3s; }
.c3 { animation-delay: 0.5s; }

.glass-panel:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 20px 40px rgba(37, 99, 235, 0.1);
    background: rgba(255, 255, 255, 0.85);
}

/* --- CARD CONTENT STYLING --- */
.card-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: inline-block;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
    transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.glass-panel:hover .card-icon {
    transform: scale(1.2) rotate(10deg);
}

.card-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.8rem;
}

.card-desc {
    font-size: 0.95rem;
    color: #64748b;
    line-height: 1.6;
}

/* --- PATHWAY CARDS --- */
.path-card {
    background: white;
    border-radius: 24px;
    padding: 2.5rem;
    border: 1px solid #e2e8f0;
    position: relative;
    transition: all 0.4s ease;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    animation: slideUp 0.8s ease-out both;
}

/* Stagger path cards */
.p-left { animation-delay: 0.6s; }
.p-right { animation-delay: 0.8s; }

.path-card:hover {
    border-color: #3b82f6;
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

.path-card:hover::before {
    left: 150%;
    transition: 0.7s ease-in-out;
}

.path-icon {
    background: #eff6ff;
    width: 60px; height: 60px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    color: #2563eb;
    border: 1px solid #dbeafe;
    transition: transform 0.6s ease;
}

.path-card:hover .path-icon {
    transform: rotateY(180deg);
    background: #2563eb;
    color: white;
    border-color: #2563eb;
}

.path-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.5rem;
}

/* Chips */
.chip-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 1.5rem 0;
}

.chip {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #475569;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.3s;
}

.path-card:hover .chip {
    background: #eff6ff;
    color: #1d4ed8;
    border-color: #bfdbfe;
    transform: scale(1.05);
}

/* --- BUTTONS --- */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
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

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px rgba(37, 99, 235, 0.3);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

/* QUICK INSIGHT BANNER */
.insight-box {
    background: #ffffff;
    border-left: 5px solid #10b981;
    color: #1e293b;
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

/* FAQ & FOOTER STYLES */
.faq-header {
    text-align:center; 
    color:#1e293b; 
    margin-top:3rem; 
    font-weight: 700;
}

.footer-box {
    text-align:center; 
    margin-top: 4rem; 
    padding: 2rem; 
    border-top: 1px solid rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.3);
    border-radius: 20px 20px 0 0;
}

.disclaimer-text {
    font-size: 0.75rem; 
    color: #64748b; 
    max-width: 800px;
    margin: 0 auto 1rem auto;
    line-height: 1.5;
}

</style>
""", unsafe_allow_html=True)

# =============================================================
# FEATURE 1: EDUCATIONAL TICKER (Indices + 7 Types + Sector Pairs)
# =============================================================

def format_ticker_item(symbol, name, data_frame):
    try:
        try:
            stock_data = data_frame.xs(symbol, axis=1, level=1)
        except:
            stock_data = data_frame[symbol]
        
        stock_data = stock_data.ffill()

        if stock_data.empty or stock_data['Close'].isnull().all():
            return f"{name}: No Data"

        current_price = stock_data['Close'].dropna().iloc[-1]
        open_price = stock_data['Open'].dropna().iloc[0]
        
        if open_price == 0 or str(open_price) == 'nan': 
            return f"{name}: N/A"

        change = ((current_price - open_price) / open_price) * 100
        arrow = "▲" if change >= 0 else "▼"
        color_style = "color: #16a34a;" if change >= 0 else "color: #dc2626;"
        
        # Display Format: ▲ NAME: 1,200.00 (+1.2%)
        return f"<span style='{color_style}'><b>{arrow} {name}</b>: {current_price:,.2f} ({change:+.2f}%)</span>"
    except:
        return f"{name}: ..."

@st.fragment(run_every=60)
def show_auto_ticker():
    # 1. DEFINE THE EDUCATIONAL UNIVERSE (Total 25 Items)
    universe = {
        # A. The Market Thermometers (2)
        "INDICES": {
            "^NSEI": "NIFTY 50", 
            "^BSESN": "SENSEX"
        },
        
        # B. The 7 Educational Types (7)
        "TYPES": {
            "RELIANCE.NS": "RELIANCE (L.Cap)",
            "VOLTAS.NS": "VOLTAS (Mid)",
            "HAPPSTMNDS.NS": "HAPPY MINDS (Small)",
            "ZOMATO.NS": "ZOMATO (Growth)",
            "COALINDIA.NS": "COAL IND (Div)",
            "TATAMOTORS.NS": "TATA MOTORS (Cyc)",
            "HINDUNILVR.NS": "HUL (Def)"
        },

        # C. Sector Representatives (16 Stocks / 8 Sectors)
        "IT": { "TCS.NS": "TCS", "INFY.NS": "INFY" },
        "BANKING": { "HDFCBANK.NS": "HDFC BANK", "ICICIBANK.NS": "ICICI BANK" },
        "PHARMA": { "SUNPHARMA.NS": "SUN PHARMA", "CIPLA.NS": "CIPLA" },
        "METAL": { "TATASTEEL.NS": "TATA STEEL", "JINDALSTEL.NS": "JINDAL STEEL" },
        "POWER": { "POWERGRID.NS": "POWERGRID", "NTPC.NS": "NTPC" },
        "AUTO": { "MARUTI.NS": "MARUTI", "M&M.NS": "M&M" },
        "FMCG": { "NESTLEIND.NS": "NESTLE", "BRITANNIA.NS": "BRITANNIA" },
        "INFRA": { "DLF.NS": "DLF", "LT.NS": "L&T" } # Added to reach 25
    }
    
    # 2. FLATTEN THE LIST FOR DOWNLOADING
    selected_tickers = []
    symbol_map = {}
    
    for category in universe:
        for symbol, display_name in universe[category].items():
            selected_tickers.append(symbol)
            symbol_map[symbol] = display_name
            
    # 3. FETCH DATA 
    try:
        batch_data = yf.download(selected_tickers, period="1d", interval="1m", group_by='ticker', threads=True, progress=False)
    except:
        batch_data = None

    # 4. FORMAT DATA FOR DISPLAY
    ticker_items = []
    
    if batch_data is not None and not batch_data.empty:
        for sym in selected_tickers:
            if sym in symbol_map:
                name = symbol_map[sym]
                ticker_items.append(format_ticker_item(sym, name, batch_data))
    else:
        ticker_items = ["Loading Market Data..."]

    # 5. RENDER HTML
    ticker_html_content = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(ticker_items)
    
    st.markdown(f"""
    <div class="ticker-wrap">
    <div class="ticker-heading">MARKET WATCH</div>
    <div class="ticker">
        <div class="ticker__item">{ticker_html_content}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# Execute the fragment
show_auto_ticker()

# =============================================================
# HEADER & FEATURE 2: MARKET STATUS INDICATOR
# =============================================================

# Logic for Market Status
def get_market_status():
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
# LEARNING SECTION (3 Floating Cards)
# =============================================================
st.markdown("<h3 style='margin-bottom:1.5rem; font-weight:700; color:#1e293b; animation: slideUp 0.5s ease-out;'>🧠 Learn the Basics</h3>", unsafe_allow_html=True)

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
col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("📚 Go to Learning Center"):
        st.switch_page("pages/stock_details.py")

# =============================================================
# FEATURE 3: HELP ME DECIDE (EXPANDER)
# =============================================================
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

with st.container():
    with st.expander("🤔 Not sure which path to choose? Click here for a quick check."):
        st.markdown("##### How do you handle market drops?")
        risk_level = st.select_slider(
            "",
            options=["I panic easily", "I can handle small drops", "I love volatility for profit"],
            label_visibility="collapsed"
        )
        
        st.write("---")
        
        if risk_level == "I panic easily":
            st.info("💡 **Recommendation: Beginner.** Focus on stable Blue-chip stocks like those in the NIFTY 50.")
        elif risk_level == "I can handle small drops":
            st.success("💡 **Recommendation: Mixed.** You can start with Beginner but explore Reinvestor strategies soon.")
        else:
            st.warning("🔥 **Recommendation: Reinvestor.** You are ready for Small Caps, Sector Rotation, and high-growth bets.")

# =============================================================
# PATHWAYS (Side-by-Side Dashboard Cards)
# =============================================================
st.markdown("<h3 style='margin-top:3rem; margin-bottom:1.5rem; font-weight:700; color:#1e293b; animation: slideUp 0.6s ease-out;'>🚀 Choose Your Path</h3>", unsafe_allow_html=True)

col_path1, col_path2 = st.columns(2, gap="large")

with col_path1:
    st.markdown("""<div class="path-card p-left">
        <div class="path-icon">🌱</div>
        <div class="path-title">Beginner</div>
        <div style="color:#64748b; margin-bottom:1rem;">Safe, steady, and simple. Perfect for your first steps.</div>
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
        <div style="color:#64748b; margin-bottom:1rem;">Growth-focused strategies for experienced players.</div>
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
# FEATURE 4: FAQ SECTION
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
        st.write("We fetch new data automatically every minute. Note that exchange feeds via Yahoo Finance may still have a small delay.")
    with st.expander("Can I trade directly here?"):
        st.write("No. This is an analysis dashboard. You must use your registered broker (Zerodha, Groww, etc.) to place actual trades.")

# =============================================================
# FEATURE 5: FOOTER & LEGAL DISCLAIMER
# =============================================================
st.markdown("""
<div class="footer-box">
    <p class="disclaimer-text">
        <b>DISCLAIMER:</b> This application is for educational purposes only. 
        It does not constitute financial advice, investment recommendations, or solicitation to buy/sell any securities. 
        Stock market investments are subject to market risks. Please consult a SEBI registered financial advisor before trading.
    </p>
    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">
        Smart Investor Assistant • v2.0 • Powered by Analytics
    </div>
</div>
""", unsafe_allow_html=True)