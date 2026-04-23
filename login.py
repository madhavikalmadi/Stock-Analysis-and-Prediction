import streamlit as st
import auth_utils
import time
import re
from mongo_db import users_col

st.set_page_config(page_title="Smart Investor | Login", layout="centered", page_icon="📈")

# =====================================================
# 🔁 REDIRECT IF ALREADY LOGGED IN
# =====================================================
if st.session_state.get("is_admin"):
    st.switch_page("pages/admin.py")
if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

# =====================================================
# GLOBAL STYLES
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a1020 100%);
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding-top: 2rem !important; max-width: 480px !important; }

/* ── Brand Header ── */
.brand-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.brand-logo {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.4rem;
    color: #f0c040;
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 4px;
}
.brand-tagline {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    color: #5a7090;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    font-weight: 400;
}

/* ── Card ── */
.auth-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 2rem 2.2rem 2.2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 24px 60px rgba(0,0,0,0.5);
}

/* ── Tab Selector ── */
.tab-row {
    display: flex;
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1.8rem;
    gap: 4px;
}
.tab-btn {
    flex: 1;
    text-align: center;
    padding: 0.5rem 0;
    border-radius: 7px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}
.tab-btn.active {
    background: #f0c040;
    color: #0a0e1a;
}
.tab-btn.inactive {
    color: #6080a0;
}

/* ── Form fields ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 9px !important;
    color: #e0eaf8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    padding: 0.65rem 0.9rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f0c040 !important;
    box-shadow: 0 0 0 3px rgba(240,192,64,0.12) !important;
}
.stTextInput > label {
    color: #8aabcc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"],
.stButton > button:first-child {
    background: linear-gradient(135deg, #f0c040 0%, #e8a820 100%) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(240,192,64,0.25) !important;
}
.stButton > button:first-child:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(240,192,64,0.35) !important;
}

/* ── Secondary button (Admin) ── */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #5a7090 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    color: #f0c040 !important;
    border-color: rgba(240,192,64,0.3) !important;
}

/* ── Alerts ── */
.stSuccess > div {
    background: rgba(52,199,89,0.12) !important;
    border: 1px solid rgba(52,199,89,0.25) !important;
    border-radius: 9px !important;
    color: #34c759 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stError > div, .stWarning > div {
    background: rgba(255,59,48,0.1) !important;
    border: 1px solid rgba(255,59,48,0.25) !important;
    border-radius: 9px !important;
    color: #ff6b6b !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stWarning > div {
    background: rgba(255,159,10,0.1) !important;
    border-color: rgba(255,159,10,0.25) !important;
    color: #ff9f0a !important;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #f0c040;
    margin: 1.4rem 0 0.6rem;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(240,192,64,0.12);
}

/* ── Password strength bar ── */
.pw-strength-wrap {
    margin-top: -8px;
    margin-bottom: 12px;
}
.pw-bar-bg {
    height: 4px;
    background: rgba(255,255,255,0.07);
    border-radius: 4px;
    overflow: hidden;
}
.pw-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s, background 0.3s;
}
.pw-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Requirement checklist ── */
.req-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 14px;
    margin: 6px 0 14px;
    padding: 0;
    list-style: none;
}
.req-item {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: 5px;
}
.req-ok  { color: #34c759; }
.req-bad { color: #3a5568; }

/* ── Info box ── */
.info-box {
    background: rgba(240,192,64,0.06);
    border: 1px solid rgba(240,192,64,0.12);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin: 1.2rem 0;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    color: #7a9ab8;
    line-height: 1.6;
}
.info-box strong { color: #f0c040; }

/* ── Divider ── */
.styled-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.4rem 0;
}
.styled-divider::before, .styled-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
}
.styled-divider span {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    color: #3a5060;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Admin panel ── */
.admin-panel {
    background: rgba(240,192,64,0.04);
    border: 1px solid rgba(240,192,64,0.15);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
}
.admin-panel-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: #f0c040;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* ── Footer ── */
.login-footer {
    text-align: center;
    margin-top: 2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    color: #2a3848;
    letter-spacing: 0.5px;
}

/* ── Market ticker strip ── */
.ticker-strip {
    background: rgba(240,192,64,0.06);
    border: 1px solid rgba(240,192,64,0.1);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-bottom: 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: #6090b0;
    text-align: center;
    letter-spacing: 0.5px;
}
.ticker-up { color: #34c759; font-weight: 600; }
.ticker-dn { color: #ff6b6b; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# BRAND HEADER
# =====================================================
st.markdown("""
<div class="brand-header">
    <div class="brand-logo">📈 Smart Investor</div>
    <div class="brand-tagline">NSE · BSE · Real-Time Analytics</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MARKET TICKER (decorative)
# =====================================================
st.markdown("""
<div class="ticker-strip">
    NIFTY 50 &nbsp;<span class="ticker-up">▲ 0.42%</span> &nbsp;|&nbsp;
    SENSEX &nbsp;<span class="ticker-up">▲ 0.38%</span> &nbsp;|&nbsp;
    BANK NIFTY &nbsp;<span class="ticker-dn">▼ 0.11%</span> &nbsp;|&nbsp;
    NIFTYBEES &nbsp;<span class="ticker-up">▲ 0.45%</span>
</div>
""", unsafe_allow_html=True)

# =====================================================
# TAB STATE
# =====================================================
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"

# =====================================================
# AUTH CARD
# =====================================================
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

# Tab switcher
col_l, col_r = st.columns(2)
with col_l:
    if st.button("Sign In", key="tab_login", use_container_width=True,
                 type="primary" if st.session_state.auth_tab == "login" else "secondary"):
        st.session_state.auth_tab = "login"
        st.rerun()
with col_r:
    if st.button("Create Account", key="tab_signup", use_container_width=True,
                 type="primary" if st.session_state.auth_tab == "signup" else "secondary"):
        st.session_state.auth_tab = "signup"
        st.rerun()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─────────────────────────────
# LOGIN FORM
# ─────────────────────────────
if st.session_state.auth_tab == "login":
    email_or_username = st.text_input("Email or Username", placeholder="e.g. john@example.com", key="login_id")
    password = st.text_input("Password", type="password", placeholder="Your password", key="login_pw")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("Sign In →", key="login_btn", use_container_width=True):
        if not email_or_username or not password:
            st.error("Please fill in all fields.")
        elif auth_utils.login_user(email_or_username, password):
            user = users_col.find_one({
                "$or": [
                    {"username": {"$regex": f"^{email_or_username}$", "$options": "i"}},
                    {"email": {"$regex": f"^{email_or_username}$", "$options": "i"}}
                ]
            })
            if user:
                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.user_id = str(user["_id"])
                st.session_state["user"] = user
                st.query_params["user_id"] = st.session_state.user_id
                st.query_params["username"] = user["username"]
                st.success(f"Welcome back, {user['username']}! Redirecting…")
                st.switch_page("pages/dashboard.py")
            else:
                st.error("User details not found. Please try again.")
        else:
            st.error("Incorrect email/username or password.")

    st.markdown("""
    <div class="styled-divider"><span>or</span></div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🛠  Admin Access", key="show_admin_btn", type="secondary", use_container_width=True):
            st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)
            st.rerun()

# ─────────────────────────────
# SIGNUP FORM
# ─────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1rem;">
        <div style="font-family:'DM Sans',sans-serif; font-size:0.85rem; color:#5a7090; line-height:1.6;">
            Get access to real-time NSE/BSE data, your personal watchlist,<br>
            and academic-grade risk metrics — completely free.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── ACCOUNT INFO SECTION ──
    st.markdown('<div class="section-label">Account Details</div>', unsafe_allow_html=True)

    new_user = st.text_input("Username", placeholder="e.g. john_trader", key="su_username",
                             help="3–20 characters, letters and numbers only. Used to log in.")
    new_email = st.text_input("Email Address", placeholder="e.g. john@example.com", key="su_email")

    # ── CONTACT SECTION ──
    st.markdown('<div class="section-label">Contact</div>', unsafe_allow_html=True)

    new_mob = st.text_input("Mobile Number", placeholder="e.g. 9876543210", key="su_mobile",
                           help="10-digit Indian mobile number")

    # ── SECURITY SECTION ──
    st.markdown('<div class="section-label">Security</div>', unsafe_allow_html=True)

    new_pass = st.text_input("Password", type="password", placeholder="Min. 8 characters", key="su_pw")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="su_pw2")

    # ── LIVE PASSWORD STRENGTH ──
    def password_strength(pw):
        if not pw:
            return 0, "—", "#2a3848"
        score = 0
        if len(pw) >= 8:  score += 1
        if re.search(r'[A-Z]', pw): score += 1
        if re.search(r'[0-9]', pw): score += 1
        if re.search(r'[^A-Za-z0-9]', pw): score += 1
        labels = ["", "Weak", "Fair", "Good", "Strong"]
        colors = ["", "#ff6b6b", "#ff9f0a", "#34c759", "#00d4aa"]
        return score, labels[score], colors[score]

    if new_pass:
        score, label, color = password_strength(new_pass)
        pct = (score / 4) * 100
        has_upper  = bool(re.search(r'[A-Z]', new_pass))
        has_digit  = bool(re.search(r'[0-9]', new_pass))
        has_symbol = bool(re.search(r'[^A-Za-z0-9]', new_pass))
        has_length = len(new_pass) >= 8

        st.markdown(f"""
        <div class="pw-strength-wrap">
            <div class="pw-bar-bg">
                <div class="pw-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
            <div class="pw-label" style="color:{color};">{label}</div>
            <ul class="req-list">
                <li class="req-item {'req-ok' if has_length else 'req-bad'}">{'✓' if has_length else '○'} 8+ characters</li>
                <li class="req-item {'req-ok' if has_upper else 'req-bad'}">{'✓' if has_upper else '○'} Uppercase letter</li>
                <li class="req-item {'req-ok' if has_digit else 'req-bad'}">{'✓' if has_digit else '○'} Number</li>
                <li class="req-item {'req-ok' if has_symbol else 'req-bad'}">{'✓' if has_symbol else '○'} Special character</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── TERMS ──
    agree = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="su_agree")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── SUBMIT ──
    if st.button("Create My Account →", key="signup_btn", use_container_width=True):
        # Validation
        errors = []
        if not new_user or not new_email or not new_mob or not new_pass or not confirm_password:
            errors.append("All fields are required.")
        if new_user and (len(new_user) < 3 or len(new_user) > 20):
            errors.append("Username must be 3–20 characters.")
        if new_user and not re.match(r'^[a-zA-Z0-9_]+$', new_user):
            errors.append("Username can only contain letters, numbers, and underscores.")
        if new_email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
            errors.append("Please enter a valid email address.")
        if new_mob and not re.match(r'^[6-9]\d{9}$', new_mob):
            errors.append("Enter a valid 10-digit Indian mobile number.")
        if new_pass and len(new_pass) < 8:
            errors.append("Password must be at least 8 characters.")
        if new_pass and confirm_password and new_pass != confirm_password:
            errors.append("Passwords do not match.")
        if not agree:
            errors.append("Please accept the Terms of Service to continue.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            result = auth_utils.signup_user(new_user, new_pass, new_email, new_mob)
            if result:
                st.success(f"🎉 Account created! Welcome, {new_user}. Switching to login...")
                st.balloons()
                time.sleep(1.5)
                st.session_state.auth_tab = "login"
                st.rerun()
            else:
                st.error("Username already taken. Please choose a different one.")

st.markdown('</div>', unsafe_allow_html=True)  # close auth-card

# =====================================================
# ADMIN LOGIN PANEL
# =====================================================
if st.session_state.get("show_admin_login"):
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="admin-panel-title">⚙ Admin Console</div>', unsafe_allow_html=True)

    admin_user = st.text_input("Admin Username", placeholder="admin", key="admin_u")
    admin_pass = st.text_input("Admin Password", type="password", placeholder="••••••••", key="admin_p")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.button("Login as Admin", key="admin_login_btn", use_container_width=True):
            if admin_user == "admin" and admin_pass == "aprilfool1203":
                st.session_state.is_admin = True
                st.session_state.authenticated = False
                st.session_state.show_admin_login = False
                st.success("Admin authenticated.")
                st.switch_page("pages/admin.py")
            else:
                st.error("Invalid admin credentials.")
    with col_b:
        if st.button("Cancel", key="admin_cancel", type="secondary", use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="login-footer">
    Smart Investor Assistant &nbsp;·&nbsp; Indian Equity Markets &nbsp;·&nbsp; Data via Yahoo Finance
</div>
""", unsafe_allow_html=True)