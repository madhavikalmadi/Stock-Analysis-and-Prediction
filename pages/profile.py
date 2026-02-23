import streamlit as st
import sys
import os
import yfinance as yf
import data_fetch
import metric_calculator
from mongo_db import watchlist_col
from bson import ObjectId
import pandas as pd
# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="My Profile",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (VERY IMPORTANT)
# =====================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# =====================================================
# 🔄 PERSIST SESSION (VERY IMPORTANT)
# =====================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already guarantees authentication

# --------------------------------------------------
# CSS STYLING
# --------------------------------------------------
# Static Light Mode Colors
card_bg = "rgba(255,255,255,0.75)"
card_text = "#1e293b"
sub_text = "rgba(0,0,0,0.6)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

body, [data-testid="stAppViewContainer"] {{
    font-family: 'Outfit', sans-serif;
}}
/* ... (CSS continues) ... */


/* ---------- LEFT PROFILE BOX ---------- */
/* ---------- LEFT PROFILE BOX (TARGETING COLUMN 1) ---------- */
/* ---------- LEFT PROFILE BOX (TARGETING CONTAINER) ---------- */
[data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"] {{
    background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.05)) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    backdrop-filter: blur(14px) !important;
}}
/* Center content inside the container */
[data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"] > div {{
    align-items: center;
    text-align: center;
    gap: 1rem;
}}

.profile-avatar {{
    font-size: 4rem;
    background: linear-gradient(135deg, #3b82f6, #9333ea);
    color: white;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}}

.profile-name {{
    font-size: 1.5rem;
    font-weight: 800;
}}

.profile-sub {{
    opacity: 0.75;
    margin-bottom: 1.2rem;
}}

/* ---------- RIGHT SIDE ---------- */
.section-title {{
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
}}

.watchlist-card {{
    background: {card_bg};
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 1.6rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    text-align: center;
    margin-bottom: 20px;
    color: {card_text};
}}

.watchlist-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 18px 45px rgba(59,130,246,0.25);
}}

.stock-ticker {{
    font-size: 1.5rem;
    font-weight: 800;
}}

.stock-sub {{
    font-size: 0.85rem;
    opacity: 0.7;
    color: {sub_text} !important;
}}

.empty-box {{
    text-align: center;
    padding: 3rem;
    border-radius: 22px;
    background: {card_bg};
    box-shadow: 0 8px 25px rgba(0,0,0,0.06);
    color: {card_text};
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# ADVISORY LOGIC (COPIED/REUSED)
# --------------------------------------------------
def get_recommendation_text(cagr, sharpe):
    if sharpe > 0.5 and cagr > 0.12:
        return {"verdict": "✅ Strong Buy", "color": "#059669", "bg": "#ecfdf5"}
    elif sharpe > 0.3 and cagr > 0.08:
        return {"verdict": "⚠️ Moderate", "color": "#b45309", "bg": "#fffbeb"}
    else:
        return {"verdict": "❌ Avoid", "color": "#dc2626", "bg": "#fef2f2"}

def get_persona(avg_cagr, avg_sharpe):
    if avg_cagr > 0.15: return "🚀 Growth Seeker", "Focuses on high-speed wealth building."
    if avg_sharpe > 0.6: return "🛡️ Safety First", "Prioritizes steady, low-risk returns."
    return "⚖️ Balanced Builder", "A healthy mix of growth and stability."

user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

# --------------------------------------------------
# FETCH WATCHLIST
# --------------------------------------------------
# --------------------------------------------------
# FETCH WATCHLIST
# --------------------------------------------------
watchlist = []
analyzed_watchlist = []
avg_cagr = 0
avg_sharpe = 0

if user_id:
    try:
        watchlist = list(watchlist_col.find({"user_id": user_id}))
        if watchlist:
            tickers = [item['ticker'] for item in watchlist]
            # Fetch 10y data for all watchlist stocks + Sensex for reference
            full_data = data_fetch.fetch_stock_data(tickers + ["^NSEI"])
            if not full_data.empty:
                metrics = metric_calculator.compute_metrics(full_data, "^NSEI")
                for item in watchlist:
                    m = metrics[metrics["Ticker"] == item['ticker']]
                    if not m.empty:
                        row = m.iloc[0]
                        res = get_recommendation_text(row['CAGR'], row['Sharpe'])
                        analyzed_watchlist.append({
                            "ticker": item['ticker'],
                            "cagr": row['CAGR'],
                            "sharpe": row['Sharpe'],
                            "verdict": res['verdict'],
                            "color": res['color'],
                            "bg": res['bg']
                        })
                
                if analyzed_watchlist:
                    avg_cagr = sum(a['cagr'] for a in analyzed_watchlist) / len(analyzed_watchlist)
                    avg_sharpe = sum(a['sharpe'] for a in analyzed_watchlist) / len(analyzed_watchlist)

    except Exception as e:
        st.error(f"⚠️ Error loading profile data: {e}")

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
c_sidebar, c_content = st.columns([1.1, 3])

# ---------- LEFT COLUMN ----------
with c_sidebar:
    # Use native container for robust boxing
    with st.container(border=True):
        st.markdown('<div class="profile-avatar">👤</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-name">{username or "User"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="profile-sub">Smart Investor Assistant</div>', unsafe_allow_html=True)

        # JOIN DATE
        join_date = "Unknown"
        try:
            join_date = ObjectId(user_id).generation_time.strftime("%b %Y")
        except:
            pass

        st.markdown(f"<p style='opacity:0.75;'>📅 Member since: <b>{join_date}</b></p>", unsafe_allow_html=True)

        st.divider()

        # INVESTOR PERSONA
        if analyzed_watchlist:
            persona, desc = get_persona(avg_cagr, avg_sharpe)
            st.markdown(f"""
            <div style="background:rgba(59,130,246,0.1); padding:15px; border-radius:12px; border:1px solid rgba(59,130,246,0.2); margin-top:10px;">
                <div style="font-size:0.8rem; text-transform:uppercase; font-weight:700; opacity:0.6; margin-bottom:5px;">Investor Persona</div>
                <div style="font-size:1.1rem; font-weight:800; color:#2563eb;">{persona}</div>
                <div style="font-size:0.8rem; opacity:0.8; line-height:1.2; margin-top:5px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Add stocks to your watchlist to see your investor persona!")

        st.divider()

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.query_params.clear()
            st.switch_page("login.py")

# ---------- RIGHT COLUMN ----------
with c_content:
    st.markdown("<div class='section-title'>⭐ My Watchlist</div>", unsafe_allow_html=True)

    if not analyzed_watchlist:
        st.markdown("""
        <div class="empty-box">
            <h3>📭 Your Watchlist is Empty</h3>
            <p>Go to Stock Search or Company Advisor to add stocks and unlock your growth summary.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # GROWTH SUMMARY WIDGET
        st.markdown(f"""
        <div style="background:linear-gradient(90deg, #1e293b 0%, #334155 100%); color:white; padding:25px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.1); margin-bottom:30px; display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div>
                <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; opacity:0.7; margin-bottom:5px;">Avg Wealth Speed</div>
                <div style="font-size:2rem; font-weight:900; color:#10b981;">{avg_cagr*100:.1f}%<span style="font-size:1rem; opacity:0.6;">/year</span></div>
            </div>
            <div style="width:1px; height:50px; background:rgba(255,255,255,0.1);"></div>
            <div>
                <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; opacity:0.7; margin-bottom:5px;">Market Efficiency</div>
                <div style="font-size:2rem; font-weight:900; color:#3b82f6;">{avg_sharpe:.2f}</div>
            </div>
            <div style="width:1px; height:50px; background:rgba(255,255,255,0.1);"></div>
            <div>
                <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; opacity:0.7; margin-bottom:5px;">Saved Assets</div>
                <div style="font-size:2rem; font-weight:900;">{len(analyzed_watchlist)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for idx, item in enumerate(analyzed_watchlist):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="watchlist-card" style="border-top:4px solid {item['color']};">
                    <div style="font-size:0.7rem; font-weight:700; color:{item['color']}; text-transform:uppercase; margin-bottom:8px;">{item['verdict']}</div>
                    <div class="stock-ticker">{item['ticker']}</div>
                    <div style="display:flex; justify-content:center; gap:15px; margin-top:10px; font-weight:600; font-size:0.9rem;">
                        <span style="color:#059669;">📈 {item['cagr']*100:.1f}%</span>
                        <span style="color:#2563eb;">🛡️ {item['sharpe']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER & NAVIGATION
# --------------------------------------------------
st.markdown("""
<style>
div.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}
div.stButton > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important;
    color: white !important;
    border: none !important;
}
div.stButton > button * {
    color: white !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

if st.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

st.write("---")
st.markdown("<center style='opacity:0.6;'>Smart Investor Assistant</center>", unsafe_allow_html=True)