import streamlit as st
import sys
import os

# Add parent directory to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Reinvestor | Smart Investor", 
    page_icon="🔁", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (SOURCE OF TRUTH)
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

/* Animated background */
.area { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
.circles { position: absolute; width: 100%; height: 100%; }
.circles li { position: absolute; list-style: none; width: 20px; height: 20px; background: rgba(255,255,255,0.4); animation: animate 25s linear infinite; bottom: -150px; border-radius: 20%; }
@keyframes animate {
    0% { transform: translateY(0) rotate(0deg); opacity: 1; }
    100% { transform: translateY(-1000px) rotate(720deg); opacity: 0; }
}

.block-container { position: relative; z-index: 1; padding-top: 4rem !important; }

.glass-card {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(16px);
    border-radius: 30px;
    padding: 3rem 2rem;
    height: 350px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: all 0.4s ease;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden; /* For shine effect */
}
.glass-card:hover { 
    transform: translateY(-12px);
    background: rgba(255,255,255,0.85);
    box-shadow: 0 20px 50px rgba(0,0,0,0.1);
    border: 1px solid rgba(255, 255, 255, 1);
}

/* Shine Effect */
.glass-card::before {
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
.glass-card:hover::before { left: 150%; transition: 0.7s ease-in-out; }

.card-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    transition: transform 0.6s ease;
}
.glass-card:hover .card-icon {
    transform: rotateY(180deg);
}

div.stButton, div[data-testid="stButton"] {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
div.stButton > button, div[data-testid="stButton"] > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important;
    color: white !important;
    border: none !important;
}
div.stButton > button *, div[data-testid="stButton"] > button * {
    color: white !important;
}
div.stButton > button:hover, div[data-testid="stButton"] > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}
</style>

<div class="area">
<ul class="circles">
<li></li><li></li><li></li><li></li><li></li>
<li></li><li></li><li></li><li></li><li></li>
</ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HERO SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div style="text-align:center;">
    <div style="font-size:4rem; font-weight:900;">Reinvestor Advisor</div>
    <div style="font-size:1.2rem; opacity:0.7;">
        Advanced analysis for experienced investors
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")
st.write("")

# -----------------------------------------------------------------------------
# MAIN MENU
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 10, 1])

# PREPARE PARAMS
import urllib.parse
user_id = st.session_state.get("user_id", "")
username = st.session_state.get("username", "")
params_str = ""
if user_id and username:
    safe_user = urllib.parse.quote(str(user_id))
    safe_name = urllib.parse.quote(str(username))
    params_str = f"?user_id={safe_user}&username={safe_name}"

with col2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f"""
        <a href="company{params_str}" target="_self" style="text-decoration:none; color:inherit;">
            <div class="glass-card">
                <div class="card-icon">🏢</div>
                <h2>Company Advisor</h2>
                <p>Company insights. Smarter analysis. Better investments.</p>
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.write("") # SPACER
        if st.button("🚀 Start Company Analysis"):
            st.switch_page("pages/company.py")

    with c2:
        st.markdown(f"""
        <a href="index{params_str}" target="_self" style="text-decoration:none; color:inherit;">
            <div class="glass-card">
                <div class="card-icon">📈</div>
                <h2>Index Advisor</h2>
                <p>Compare indices like Nifty 50, Sensex, and Bank Nifty to find balanced long-term investment options.</p>
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.write("") # SPACER
        if st.button("🚀 Start Index Analysis"):
            st.switch_page("pages/index.py")

st.markdown("---")
if st.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

st.markdown("<div style='text-align:center; color:gray; font-size:0.7rem;'>v2.0 - Centered UI</div>", unsafe_allow_html=True)
