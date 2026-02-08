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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Hide sidebar components */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Global Background */
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #eef2f3 0%, #8e9eab 100%) !important;
    font-family: 'Outfit', sans-serif !important;
    color: #1e293b;
    overflow-x: hidden;
}

/* Container Spacing */
.block-container {
    padding-top: 4rem !important;
    max-width: 1200px;
}

/* Glass Card Styling */
.glass-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 3rem 2rem;
    height: 380px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.4s ease;
    border: 1px solid rgba(255,255,255,0.4);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.glass-card:hover {
    transform: translateY(-10px);
    background: rgba(255,255,255,0.9);
    box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    border-color: rgba(255,255,255,0.8);
}

.card-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    background: rgba(37, 99, 235, 0.1);
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
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

/* Premium Gradient Buttons */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.8rem 1.5rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4) !important;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
}

/* Footer Button (Secondary) */
div.stButton:last-of-type > button {
    background: rgba(30, 41, 59, 0.9) !important;
    font-size: 0.9rem !important;
    margin-top: 1rem;
}
div.stButton:last-of-type > button:hover {
    background: #0f172a !important;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.3) !important;
}

/* Typography */
h1 { font-weight: 900 !important; color: #1e293b; }
p { font-size: 1.1rem; color: #64748b; }
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
