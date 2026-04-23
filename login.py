import streamlit as st
import auth_utils
from mongo_db import users_col

st.set_page_config(page_title="Smart Investor | Login", layout="wide", page_icon="📈")

if st.session_state.get("is_admin"):
    st.switch_page("pages/admin.py")
if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #f0f4f8; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    .block-container { padding: 2rem 2rem 1rem !important; max-width: 1000px !important; }

    /* ── Split card wrapper ── */
    .login-shell {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 600px;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 24px 64px rgba(15,23,42,0.16);
        max-width: 900px;
        margin: 0 auto;
    }

    /* ── LEFT panel ── */
    .panel-left {
        background: #0f172a;
        padding: 2.8rem 2.4rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .brand-row { display: flex; align-items: center; gap: 10px; }
    .brand-badge {
        width: 38px; height: 38px; background: #6366f1;
        border-radius: 10px; display: flex; align-items: center;
        justify-content: center; font-size: 18px;
        flex-shrink: 0;
    }
    .brand-name { color: #f8fafc; font-size: 1.05rem; font-weight: 800; letter-spacing: -0.3px; }

    .tagline { margin-top: 2.2rem; }
    .tagline h2 {
        color: #f8fafc; font-size: 1.6rem; font-weight: 800;
        line-height: 1.3; letter-spacing: -0.5px;
    }
    .tagline h2 em { color: #818cf8; font-style: normal; }
    .tagline p { color: #64748b; font-size: 0.82rem; margin-top: 0.7rem; line-height: 1.65; }

    .ticker-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 10px; margin-top: 2rem;
    }
    .tk {
        background: #1e293b; border-radius: 12px;
        padding: 0.9rem 1rem; border: 1px solid #334155;
    }
    .tk-label { color: #475569; font-size: 0.63rem; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; }
    .tk-val   { color: #f1f5f9; font-size: 1.15rem; font-weight: 800; margin: 4px 0 6px; }
    .tk-up    { color: #10b981; background: rgba(16,185,129,0.12); font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; display: inline-block; }
    .tk-dn    { color: #f87171; background: rgba(248,113,113,0.12); font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; display: inline-block; }

    .left-footer { color: #334155; font-size: 0.7rem; line-height: 1.7; margin-top: 2rem; }

    /* ── RIGHT panel ── */
    .panel-right {
        background: #ffffff;
        padding: 2.8rem 2.6rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .form-head { margin-bottom: 1.8rem; }
    .form-head h3 { color: #0f172a; font-size: 1.4rem; font-weight: 800; letter-spacing: -0.4px; }
    .form-head p  { color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem; }

    /* ── Input labels ── */
    div[data-testid="stTextInput"] label {
        color: #64748b !important; font-size: 0.72rem !important;
        font-weight: 700 !important; letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stTextInput"] input {
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important; background: #f8fafc !important;
        color: #0f172a !important; font-size: 0.92rem !important;
        padding: 0.6rem 0.9rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
        background: #fff !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #cbd5e1 !important; }

    /* ── Primary button ── */
    div[data-testid="stButton"] > button:not([kind="secondary"]) {
        background: #6366f1 !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 0.92rem !important; width: 100% !important;
        padding: 0.68rem !important; letter-spacing: 0.2px !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
        transition: background 0.15s, transform 0.1s !important;
    }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover {
        background: #4f46e5 !important;
        transform: translateY(-1px) !important;
    }

    /* ── Secondary (admin) button ── */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #fff !important; color: #64748b !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important; font-size: 0.82rem !important;
        font-weight: 600 !important; width: 100% !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #6366f1 !important; color: #6366f1 !important;
        background: #f5f3ff !important;
    }

    /* ── Divider ── */
    .or-divider { display: flex; align-items: center; gap: 10px; margin: 1.2rem 0; }
    .or-line    { flex: 1; height: 1px; background: #e2e8f0; }
    .or-text    { color: #cbd5e1; font-size: 0.7rem; letter-spacing: 0.5px; white-space: nowrap; }

    /* ── Feature pills ── */
    .feats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 1.5rem; }
    .feat  {
        background: #f8fafc; border: 1px solid #f1f5f9;
        border-radius: 9px; padding: 0.6rem 0.8rem;
        display: flex; align-items: flex-start; gap: 8px;
    }
    .feat-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
    .feat-txt { color: #475569; font-size: 0.72rem; line-height: 1.4; }
    .feat-txt b { color: #0f172a; font-size: 0.74rem; display: block; margin-bottom: 1px; }

    /* ── Secure badge ── */
    .secure {
        display: flex; align-items: center; gap: 8px;
        margin-top: 1.4rem; padding: 0.5rem 0.85rem;
        background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 9px;
    }
    .secure span { color: #15803d; font-size: 0.72rem; font-weight: 500; }

    /* ── Admin card ── */
    .admin-section {
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 14px; padding: 1.4rem 1.6rem; margin-top: 1rem;
        max-width: 900px; margin-left: auto; margin-right: auto;
    }
    .admin-title { color: #92400e; font-size: 0.95rem; font-weight: 700; margin-bottom: 0.8rem; }

    /* ── Alerts ── */
    div[data-testid="stAlert"] { border-radius: 10px !important; font-size: 0.84rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Two-column shell ────────────────────────────────
st.markdown('<div class="login-shell">', unsafe_allow_html=True)

# LEFT
st.markdown("""
<div class="panel-left">
  <div>
    <div class="brand-row">
      <div class="brand-badge">📈</div>
      <span class="brand-name">Smart Investor</span>
    </div>
    <div class="tagline">
      <h2>Trade smarter,<br>invest with <em>confidence</em></h2>
      <p>Real-time NSE &amp; BSE analytics, risk-adjusted scoring, and your personalised watchlist — all in one place.</p>
    </div>
    <div class="ticker-grid">
      <div class="tk"><div class="tk-label">Nifty 50</div><div class="tk-val">24,834</div><span class="tk-up">▲ 1.2%</span></div>
      <div class="tk"><div class="tk-label">Sensex</div><div class="tk-val">81,562</div><span class="tk-up">▲ 0.9%</span></div>
      <div class="tk"><div class="tk-label">Bank Nifty</div><div class="tk-val">52,140</div><span class="tk-dn">▼ 0.3%</span></div>
      <div class="tk"><div class="tk-label">Nifty IT</div><div class="tk-val">38,710</div><span class="tk-up">▲ 2.1%</span></div>
    </div>
  </div>
  <div class="left-footer">Powered by Yahoo Finance · MongoDB · Streamlit<br>Built for smarter, data-driven investing.</div>
</div>
""", unsafe_allow_html=True)

# RIGHT — rendered via Streamlit inside a styled div
st.markdown("""
<div class="panel-right">
  <div class="form-head">
    <h3>Welcome back</h3>
    <p>Sign in to access your portfolio &amp; insights</p>
  </div>
""", unsafe_allow_html=True)

email_or_username = st.text_input("Email or Username", placeholder="you@example.com or username")
password = st.text_input("Password", type="password", placeholder="••••••••")

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

if st.button("Sign In →", use_container_width=True):
    if not email_or_username or not password:
        st.error("⚠️ Please fill in all fields.")
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
            st.error("User not found.")
    else:
        st.error("❌ Invalid credentials. Please try again.")

st.markdown("""
  <div class="or-divider">
    <div class="or-line"></div><span class="or-text">ADMIN ACCESS</span><div class="or-line"></div>
  </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    if st.button("⚙ Admin Login", type="secondary", use_container_width=True):
        st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)

st.markdown("""
  <div class="feats">
    <div class="feat"><div class="feat-dot" style="background:#6366f1"></div><div class="feat-txt"><b>Live Analytics</b>Real-time NSE/BSE data</div></div>
    <div class="feat"><div class="feat-dot" style="background:#10b981"></div><div class="feat-txt"><b>Risk Scoring</b>10-yr adjusted metrics</div></div>
    <div class="feat"><div class="feat-dot" style="background:#f59e0b"></div><div class="feat-txt"><b>Watchlist</b>Saved across devices</div></div>
    <div class="feat"><div class="feat-dot" style="background:#ec4899"></div><div class="feat-txt"><b>Sector Advisor</b>Category comparisons</div></div>
  </div>
  <div class="secure">
    <span>🔒 Secured with MongoDB authentication</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close .login-shell

# ── Admin Section ───────────────────────────────────
if st.session_state.get("show_admin_login"):
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.markdown('<p class="admin-title">🛡 Admin Authentication</p>', unsafe_allow_html=True)

    admin_user = st.text_input("Admin Username", placeholder="admin", key="admin_user_input")
    admin_pass = st.text_input("Admin Password", type="password", placeholder="••••••••", key="admin_pass_input")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Login as Admin", use_container_width=True):
            if admin_user == "admin" and admin_pass == "aprilfool1203":
                st.session_state.is_admin         = True
                st.session_state.authenticated    = False
                st.session_state.show_admin_login = False
                st.success("✅ Admin login successful")
                st.switch_page("pages/admin.py")
            else:
                st.error("Invalid admin credentials.")
    with col_b:
        if st.button("⬅ Cancel", type="secondary", use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)