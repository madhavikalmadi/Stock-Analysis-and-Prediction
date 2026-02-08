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

[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none;
}

body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%);
    font-family: 'Outfit', sans-serif !important;
    overflow-x: hidden;
}

.block-container {
    padding-top: 4rem !important;
}

.glass-card {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(16px);
    border-radius: 30px;
    padding: 3rem 2rem;
    height: 350px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.05);
    text-align: center;
    transition: 0.4s ease;
}

.glass-card:hover {
    transform: translateY(-10px);
    background: rgba(255,255,255,0.85);
}

.card-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.card-heading {
    font-size: 1.8rem;
    font-weight: 800;
}

.card-text {
    font-size: 1rem;
    opacity: 0.7;
    margin-bottom: 1.5rem;
}

div.stButton > button {
    width: 100%;
    border-radius: 14px;
    padding: 0.8rem;
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
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    c1, c2 = st.columns(2, gap="large")

    # ---------------- BLUE CHIP ----------------
    with c1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">💎</div>
            <div class="card-heading">Blue-Chip Advisor</div>
            <div class="card-text">
                Safest large-cap companies with consistent long-term growth.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Explore Blue-Chips"):
            if "user_id" in st.session_state and "username" in st.session_state:
                st.query_params["user_id"] = st.session_state.user_id
                st.query_params["username"] = st.session_state.username
            st.switch_page("pages/bluechip.py")

    # ---------------- SECTOR ----------------
    with c2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🏗️</div>
            <div class="card-heading">Sector View</div>
            <div class="card-text">
                Identify trending sectors like IT, Banking, Auto & more.
            </div>
        </div>
        """, unsafe_allow_html=True)

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
