import streamlit as st
import sys

import os

# Add parent directory to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import auth_utils

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Reinvestor | Smart Investor", 
    page_icon="🔁", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Auth check removed
# if not auth_utils.check_auth():
#     st.warning("You must log in to access this page.")
#     st.switch_page("login.py")

# =============================================================
# HANDLE SUB-PAGE REDIRECTS (Persistence)
# =============================================================
if "page" in st.query_params:
    page_name = st.query_params["page"]
    if page_name == "company":
        st.switch_page("pages/company.py") 
    elif page_name == "index":
        st.switch_page("pages/index.py")
    st.query_params.clear()

# -----------------------------------------------------------------------------
# CSS STYLING & ANIMATION
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;900&display=swap');
    [data-testid="stSidebar"] { display: none; }
    
    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%);
        font-family: 'Outfit', sans-serif !important;
        overflow-x: hidden;
    }

    /* --- ANIMATED BACKGROUND START --- */
    .area { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; overflow: hidden; }
    .circles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; margin: 0; padding: 0; }
    .circles li { position: absolute; display: block; list-style: none; width: 20px; height: 20px; background: rgba(255, 255, 255, 0.4); animation: animate 25s linear infinite; bottom: -150px; border-radius: 20%; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
    .circles li:nth-child(1){ left: 25%; width: 80px; height: 80px; animation-delay: 0s; }
    .circles li:nth-child(2){ left: 10%; width: 20px; height: 20px; animation-delay: 2s; animation-duration: 12s; }
    .circles li:nth-child(3){ left: 70%; width: 20px; height: 20px; animation-delay: 4s; }
    .circles li:nth-child(4){ left: 40%; width: 60px; height: 60px; animation-delay: 0s; animation-duration: 18s; }
    .circles li:nth-child(5){ left: 65%; width: 20px; height: 20px; animation-delay: 0s; }
    .circles li:nth-child(6){ left: 75%; width: 110px; height: 110px; animation-delay: 3s; }
    .circles li:nth-child(7){ left: 35%; width: 150px; height: 150px; animation-delay: 7s; }
    .circles li:nth-child(8){ left: 50%; width: 25px; height: 25px; animation-delay: 15s; animation-duration: 45s; }
    .circles li:nth-child(9){ left: 20%; width: 15px; height: 15px; animation-delay: 2s; animation-duration: 35s; }
    .circles li:nth-child(10){ left: 85%; width: 150px; height: 150px; animation-delay: 0s; animation-duration: 11s; }
    @keyframes animate { 0%{ transform: translateY(0) rotate(0deg); opacity: 1; border-radius: 0; } 100%{ transform: translateY(-1000px) rotate(720deg); opacity: 0; border-radius: 50%; } }
    /* --- ANIMATED BACKGROUND END --- */

    /* Ensure content sits on top of animation */
    .block-container { position: relative; z-index: 1; padding-top: 4rem !important; }

    /* CARD STYLES */
    .glass-card { 
        background: rgba(255, 255, 255, 0.55); 
        backdrop-filter: blur(16px) saturate(180%); 
        border: 1px solid rgba(255, 255, 255, 0.6); 
        border-radius: 30px; 
        padding: 3rem 2rem; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); 
        text-align: center; 
        height: 350px; 
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        transition: transform 0.3s ease;
        position: relative; z-index: 2; 
        cursor: pointer;
    }
    .glass-card:hover { transform: translateY(-12px); background: rgba(255, 255, 255, 0.85); box-shadow: 0 20px 50px rgba(0,0,0,0.1); border: 1px solid rgba(255, 255, 255, 1); }
    .card-icon { font-size: 4rem; margin-bottom: 1rem; filter: drop-shadow(0 8px 15px rgba(0,0,0,0.1)); transition: transform 0.5s ease; }
    .glass-card:hover .card-icon { transform: scale(1.15) rotate(5deg); }
    .card-heading { font-size: 1.8rem; font-weight: 800; color: #1e293b; margin-bottom: 0.5rem; }
    .card-text { color: #64748b; font-size: 1rem; line-height: 1.6; margin-bottom: 2rem; }

    /* HERO STYLES */
    .hero-container { text-align: center; padding: 2rem 1rem; animation: fadeInDown 1s ease-out; }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }

    .hero-badge { background: rgba(255,255,255,0.8); color: #2563eb; padding: 8px 24px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; display: inline-block; margin-bottom: 1.5rem; box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); animation: pulse-blue 2s infinite; backdrop-filter: blur(5px); }
    @keyframes pulse-blue { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); } 70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(37, 99, 235, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); } }

    .hero-title { font-size: 4.5rem; font-weight: 900; background: linear-gradient(to right, #30CFD0 0%, #330867 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: gradientText 5s ease infinite; background-size: 200% auto; }
    @keyframes gradientText { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .hero-subtitle { font-size: 1.3rem; color: #4b5563; max-width: 650px; margin: 0 auto 3rem auto; font-weight: 300; line-height: 1.6; }
    
    /* --- BUTTON STYLING (Matched to Beginner Advisor) --- */
    div.stButton > button { 
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); 
        color: white; 
        border-radius: 12px; 
        border: none; 
        padding: 0.8rem 1.5rem; 
        font-weight: 600; 
        letter-spacing: 0.5px; 
        transition: all 0.3s ease; 
        width: 100%; 
        box-shadow: 0 4px 15px rgba(24, 40, 72, 0.2); 
        position: relative; 
        z-index: 6; 
        overflow: hidden; 
    }
    div.stButton > button:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 8px 25px rgba(24, 40, 72, 0.3); 
        background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%); 
    }
</style>

<div class="area" >
    <ul class="circles">
        <li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li><li></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HERO SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class='hero-container'>
    <div class='hero-badge'>Advisor Tool</div>
    <div class='hero-title'>Reinvestor Advisor</div>
    <div class='hero-subtitle'>
        Where should your next investment go?<br>
        Advanced analysis for experienced players.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: HOME MENU
# -----------------------------------------------------------------------------
session_token = st.query_params.get("session", "")

col1, col2, col3 = st.columns([1, 10, 1]) 
with col2:
    card_c1, card_c2 = st.columns(2, gap="large")

    # CARD 1: COMPANY ADVISOR
    with card_c1:
        st.markdown(f"""
        <a href="company" target="_self" style="text-decoration:none; color:inherit;">
        <div class='glass-card'>
            <div class='card-content'>
                <div class='card-icon'>🏢</div>
                <div class='card-heading'>Company Advisor</div>
                <div class='card-text'>
                    Deep Dive. Analyze metrics like Sharpe Ratio, Sortino, and Volatility to find the best compounding machines.
                </div>
            </div>
        </div>
        </a>
        """, unsafe_allow_html=True)
        st.write("") 
        
        # Redirect to company.py
        if st.button("🚀 Start Company Analysis", key="btn_company"):
            st.switch_page("pages/company.py")
        

    # CARD 2: INDEX ADVISOR
    with card_c2:
        st.markdown(f"""
        <a href="index" target="_self" style="text-decoration:none; color:inherit;">
        <div class='glass-card'>
            <div class='card-content'>
                <div class='card-icon'>📈</div>
                <div class='card-heading'>Index Advisor</div>
                <div class='card-text'>
                      Macro View. Compare NIFTY 50 vs BANK vs IT to decide where to allocate your capital this month.
                </div>
            </div>
        </div>
        </a>
        """, unsafe_allow_html=True)
        st.write("") 
        
        # Redirect to index.py
        if st.button("🚀 Start Index Analysis", key="btn_index"):
                st.switch_page("pages/index.py")


# -----------------------------------------------------------------------------
# NAV (Dashboard Button)
# -----------------------------------------------------------------------------
st.write("")
st.write("---")
st.markdown("""
<style>
/* Specific style for the Back button */
div.stButton:last-of-type > button {
    padding: 0.4rem 1rem !important; 
    font-size: 0.8rem !important; 
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important; 
    box-shadow: none !important; 
    width: auto !important; 
    margin: 0 auto;
    white-space: nowrap !important;
}
div.stButton:last-of-type > button:hover { background: #2563eb !important; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([5, 2, 5])
with c2:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        st.switch_page("dashboard.py")