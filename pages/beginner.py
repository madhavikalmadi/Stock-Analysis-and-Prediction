import streamlit as st
import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Beginner Advisor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# 🔁 RESTORE SESSION FROM URL (CRITICAL)
# ==================================================
params = st.query_params

if "user_id" in params and "username" in params:
    st.session_state.user_id = params["user_id"]
    st.session_state.username = params["username"]
    st.session_state.authenticated = True

# ==================================================
# 🔄 PERSIST SESSION (VERY IMPORTANT)
# ==================================================
if "user_id" in st.session_state and "username" in st.session_state:
    st.query_params["user_id"] = st.session_state.user_id
    st.query_params["username"] = st.session_state.username

# ❌ NO LOGIN REDIRECT HERE
# Dashboard already guarantees authentication

# --------------------------------------------------
# CSS
# --------------------------------------------------
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
}
.glass-card:hover {
    transform: translateY(-15px) scale(1.02);
    background: rgba(255,255,255,0.85);
    box-shadow: 0 20px 50px rgba(0,0,0,0.15);
    border-color: rgba(255,255,255,0.9);
}

.card-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}
.card-heading {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.5rem;
}
.card-text {
    font-size: 1rem;
    color: #475569;
    margin-bottom: 2rem;
    line-height: 1.6;
}

div.stButton > button {
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
    color: white;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO
# --------------------------------------------------
st.markdown("""
<div style="text-align:center;">
    <div style="font-size:0.9rem; letter-spacing:2px; font-weight:700;">BEGINNER TOOL</div>
    <h1>Beginner Advisor</h1>
    <p>Choose a safe way to start your stock market journey.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------
# ---------------- MAIN CONTENT ----------------
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

    # ---------------- BLUE CHIP ----------------
    with c1:
        st.markdown(f"""
        <a href="bluechip{params_str}" target="_self" style="text-decoration:none; color:inherit;">
            <div class="glass-card">
                <div class="card-icon">💎</div>
                <div class="card-heading">Blue-Chip Advisor</div>
                <div class="card-text">
                    Safest large-cap companies with consistent long-term growth.
                </div>
            </div>
        </a>
        </a>
        """, unsafe_allow_html=True)

        st.write("") # SPACER
        if st.button("🚀 Explore Blue-Chips"):
            if "user_id" in st.session_state and "username" in st.session_state:
                st.query_params["user_id"] = st.session_state.user_id
                st.query_params["username"] = st.session_state.username
            st.switch_page("pages/bluechip.py")

    # ---------------- SECTOR ----------------
    with c2:
        st.markdown(f"""
        <a href="sector{params_str}" target="_self" style="text-decoration:none; color:inherit;">
            <div class="glass-card">
                <div class="card-icon">🏗️</div>
                <div class="card-heading">Sector View</div>
                <div class="card-text">
                    Identify trending sectors like IT, Banking, Auto & more.
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.write("") # SPACER
        if st.button("🚀 Explore Sectors"):
            if "user_id" in st.session_state and "username" in st.session_state:
                st.query_params["user_id"] = st.session_state.user_id
                st.query_params["username"] = st.session_state.username
            st.switch_page("pages/sector.py")

# --------------------------------------------------
# DASHBOARD NAV
# --------------------------------------------------
st.write("")
st.write("---")

if st.button("⬅ Back to Dashboard"):
    if "user_id" in st.session_state and "username" in st.session_state:
        st.query_params["user_id"] = st.session_state.user_id
        st.query_params["username"] = st.session_state.username
    st.switch_page("pages/dashboard.py")
