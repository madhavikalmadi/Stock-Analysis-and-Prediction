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
    transition: transform 0.3s ease;
}
.glass-card:hover { transform: translateY(-12px); }

div.stButton > button {
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
    color: white;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    font-weight: 600;
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

# -----------------------------------------------------------------------------
# MAIN MENU
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:3rem;">🏢</div>
            <h2>Company Advisor</h2>
            <p>Deep-dive into individual stocks</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Start Company Analysis"):
            st.switch_page("pages/company.py")

    with c2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:3rem;">📈</div>
            <h2>Index Advisor</h2>
            <p>Compare market indices</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Start Index Analysis"):
            st.switch_page("pages/index.py")

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------
st.markdown("---")

_, c_mid, _ = st.columns([4, 2, 4])
with c_mid:
    if st.button("⬅ Dashboard"):
        st.switch_page("pages/dashboard.py")
