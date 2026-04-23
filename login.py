import streamlit as st
import auth_utils
from mongo_db import users_col

st.set_page_config(page_title="Smart Investor | Login", layout="centered", page_icon="📈")

# =====================================================
# REDIRECT IF ALREADY LOGGED IN
# =====================================================

if st.session_state.get("is_admin"):
    st.switch_page("pages/admin.py")

if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

# =====================================================
# PREMIUM UI DESIGN
# =====================================================

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%);
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding-top: 4rem !important; max-width: 480px !important; }

    .brand-wrapper { text-align: center; margin-bottom: 2.5rem; }
    .brand-icon {
        font-size: 3rem; display: block; margin-bottom: 0.4rem;
        filter: drop-shadow(0 0 18px rgba(0, 212, 170, 0.6));
        animation: pulse 2.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { filter: drop-shadow(0 0 14px rgba(0, 212, 170, 0.5)); }
        50%       { filter: drop-shadow(0 0 28px rgba(0, 212, 170, 0.9)); }
    }
    .brand-title {
        font-size: 1.9rem; font-weight: 800;
        background: linear-gradient(90deg, #00d4aa, #00aaff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; letter-spacing: -0.5px; margin: 0;
    }
    .brand-sub {
        color: #6b7fa3; font-size: 0.85rem; margin-top: 0.3rem;
        letter-spacing: 0.8px; text-transform: uppercase;
    }

    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px; padding: 2.2rem 2.4rem 2rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 40px rgba(0,0,0,0.45), 0 0 0 1px rgba(0, 212, 170, 0.06) inset;
    }
    .card-title { color: #e2e8f0; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.25rem; }
    .card-sub   { color: #4a5568; font-size: 0.8rem; margin-bottom: 1.6rem; }

    div[data-testid="stTextInput"] label {
        color: #94a3b8 !important; font-size: 0.8rem !important;
        font-weight: 500 !important; letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important; color: #e2e8f0 !important;
        padding: 0.65rem 1rem !important; font-size: 0.95rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.15) !important;
        background: rgba(0, 212, 170, 0.04) !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #3a4a60 !important; }

    div[data-testid="stButton"] > button:not([kind="secondary"]) {
        background: linear-gradient(135deg, #00d4aa, #00aaff) !important;
        color: #0a0f1e !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 0.95rem !important; width: 100% !important;
        box-shadow: 0 4px 18px rgba(0, 212, 170, 0.3) !important;
    }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover {
        opacity: 0.9 !important; transform: translateY(-1px) !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        background: transparent !important; color: #6b7fa3 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important; font-size: 0.82rem !important; width: 100% !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        color: #e2e8f0 !important; border-color: rgba(255,255,255,0.25) !important;
        background: rgba(255,255,255,0.05) !important;
    }

    .divider {
        display: flex; align-items: center; gap: 0.8rem; margin: 1.5rem 0 1.2rem;
    }
    .divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.08); }
    .divider-text { color: #3a4a60; font-size: 0.75rem; letter-spacing: 0.5px; }

    div[data-testid="stAlert"] { border-radius: 10px !important; font-size: 0.85rem !important; }

    .admin-card {
        background: rgba(255,150,50,0.05); border: 1px solid rgba(255,150,50,0.15);
        border-radius: 14px; padding: 1.5rem 1.8rem; margin-top: 1.2rem;
    }
    .admin-card-title { color: #f6ad55; font-size: 1rem; font-weight: 600; margin-bottom: 1rem; }

    .login-footer { text-align: center; margin-top: 2rem; color: #2d3748; font-size: 0.75rem; line-height: 1.7; }

    .ticker-strip {
        display: flex; justify-content: center; gap: 1rem;
        margin-bottom: 2.5rem; flex-wrap: wrap;
    }
    .ticker-item {
        display: flex; flex-direction: column; align-items: center;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px; padding: 0.5rem 0.9rem; min-width: 80px;
    }
    .ticker-name { color: #6b7fa3; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; }
    .ticker-val  { color: #e2e8f0; font-size: 0.95rem; font-weight: 700; margin: 0.1rem 0; }
    .ticker-up   { color: #00d4aa; font-size: 0.72rem; font-weight: 600; }
    .ticker-dn   { color: #fc8181; font-size: 0.72rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Brand
st.markdown("""
<div class="brand-wrapper">
    <span class="brand-icon">📈</span>
    <p class="brand-title">Smart Investor</p>
    <p class="brand-sub">NSE · BSE · Real-time Analytics</p>
</div>
""", unsafe_allow_html=True)

# Ticker strip (static decorative values)
st.markdown("""
<div class="ticker-strip">
    <div class="ticker-item">
        <span class="ticker-name">NIFTY 50</span>
        <span class="ticker-val">24,834</span>
        <span class="ticker-up">▲ 1.2%</span>
    </div>
    <div class="ticker-item">
        <span class="ticker-name">SENSEX</span>
        <span class="ticker-val">81,562</span>
        <span class="ticker-up">▲ 0.9%</span>
    </div>
    <div class="ticker-item">
        <span class="ticker-name">BANK NIFTY</span>
        <span class="ticker-val">52,140</span>
        <span class="ticker-dn">▼ 0.3%</span>
    </div>
    <div class="ticker-item">
        <span class="ticker-name">NIFTY IT</span>
        <span class="ticker-val">38,710</span>
        <span class="ticker-up">▲ 2.1%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Login Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<p class="card-title">Welcome back 👋</p>', unsafe_allow_html=True)
st.markdown('<p class="card-sub">Sign in to access your portfolio & insights</p>', unsafe_allow_html=True)

email_or_username = st.text_input("Email or Username", placeholder="you@example.com or username")
password = st.text_input("Password", type="password", placeholder="••••••••")

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

if st.button("Sign In →", use_container_width=True):
    if not email_or_username or not password:
        st.error("⚠️ All fields are required.")
    elif auth_utils.login_user(email_or_username, password):
        user = users_col.find_one({
            "$or": [
                {"username": {"$regex": f"^{email_or_username}$", "$options": "i"}},
                {"email":    {"$regex": f"^{email_or_username}$", "$options": "i"}}
            ]
        })
        if user:
            st.session_state.authenticated = True
            st.session_state.username      = user["username"]
            st.session_state.user_id       = str(user["_id"])
            st.session_state["user"]       = user
            st.query_params["user_id"]  = st.session_state.user_id
            st.query_params["username"] = user["username"]
            st.success(f"✅ Welcome back, {user['username']}!")
            st.switch_page("pages/dashboard.py")
        else:
            st.error("User details not found.")
    else:
        st.error("❌ Invalid email/username or password.")

# Admin divider
st.markdown("""
<div class="divider">
    <div class="divider-line"></div>
    <span class="divider-text">ADMIN ACCESS</span>
    <div class="divider-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🛠 Admin Login", type="secondary", use_container_width=True):
        st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)

st.markdown('</div>', unsafe_allow_html=True)  # close .card

# Admin Login Section
if st.session_state.get("show_admin_login"):
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<p class="admin-card-title">🛡 Admin Authentication</p>', unsafe_allow_html=True)

    admin_user = st.text_input("Admin Username", placeholder="admin", key="admin_user_input")
    admin_pass = st.text_input("Admin Password", type="password", placeholder="••••••••", key="admin_pass_input")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Login as Admin", use_container_width=True):
            if admin_user == "admin" and admin_pass == "aprilfool1203":
                st.session_state.is_admin         = True
                st.session_state.authenticated    = False
                st.session_state.show_admin_login = False
                st.success("Admin login successful ✅")
                st.switch_page("pages/admin.py")
            else:
                st.error("Invalid admin credentials.")
    with col_b:
        if st.button("⬅ Cancel", type="secondary", use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="login-footer">
    Powered by Yahoo Finance · MongoDB · Streamlit<br>
    <span style="color:#1a2535">Built for smarter, data-driven investing.</span>
</div>
""", unsafe_allow_html=True)