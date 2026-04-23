import streamlit as st
import auth_utils
from mongo_db import users_col

st.set_page_config(page_title="Smart Investor | Login", layout="centered", page_icon="📈")

if st.session_state.get("is_admin"):
    st.switch_page("pages/admin.py")
if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

# ── Inject full-page CSS reset ──────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #f0f4f8 !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer,
    [data-testid="stSidebarNav"], #MainMenu { display: none !important; }
    .block-container {
        padding: 2.5rem 1.5rem 2rem !important;
        max-width: 960px !important;
    }

    /* ── Shell ── */
    .si-shell {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 620px;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 24px 64px rgba(15,23,42,0.18);
    }

    /* ═══════════ LEFT PANEL ═══════════ */
    .si-left {
        background: #0f172a;
        padding: 2.8rem 2.4rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .si-brand { display: flex; align-items: center; gap: 11px; }
    .si-badge {
        width: 40px; height: 40px; background: #6366f1;
        border-radius: 11px; display: flex; align-items: center;
        justify-content: center; font-size: 20px; flex-shrink: 0;
    }
    .si-name { color: #f8fafc; font-size: 1.05rem; font-weight: 800; letter-spacing: -0.3px; }

    .si-headline { margin-top: 2.4rem; }
    .si-headline h2 {
        color: #f8fafc; font-size: 1.6rem; font-weight: 900;
        line-height: 1.28; letter-spacing: -0.6px; margin: 0;
    }
    .si-headline h2 em { color: #818cf8; font-style: normal; }
    .si-headline p {
        color: #64748b; font-size: 0.82rem;
        margin-top: 0.75rem; line-height: 1.65;
    }

    .si-tickers {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 10px; margin-top: 2.2rem;
    }
    .si-tk {
        background: #1e293b; border-radius: 12px;
        padding: 0.9rem 1rem; border: 1px solid #334155;
    }
    .si-tk-lbl {
        color: #475569; font-size: 0.62rem; font-weight: 700;
        letter-spacing: 0.7px; text-transform: uppercase;
    }
    .si-tk-val {
        color: #f1f5f9; font-size: 1.15rem; font-weight: 800;
        margin: 4px 0 6px; display: block;
    }
    .si-up {
        color: #10b981; background: rgba(16,185,129,0.12);
        font-size: 0.69rem; font-weight: 700;
        padding: 2px 8px; border-radius: 20px; display: inline-block;
    }
    .si-dn {
        color: #f87171; background: rgba(248,113,113,0.12);
        font-size: 0.69rem; font-weight: 700;
        padding: 2px 8px; border-radius: 20px; display: inline-block;
    }

    .si-left-foot {
        color: #334155; font-size: 0.69rem; line-height: 1.7; margin-top: 2rem;
    }

    /* ═══════════ RIGHT PANEL ═══════════ */
    .si-right {
        background: #ffffff;
        padding: 2.8rem 2.6rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .si-form-head { margin-bottom: 1.8rem; }
    .si-form-head h3 {
        color: #0f172a; font-size: 1.4rem; font-weight: 900;
        letter-spacing: -0.5px; margin: 0;
    }
    .si-form-head p { color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem; }

    /* inputs */
    .si-field { margin-bottom: 1.1rem; }
    .si-field label {
        display: block; font-size: 0.71rem; font-weight: 700;
        color: #64748b; letter-spacing: 0.6px; text-transform: uppercase;
        margin-bottom: 0.38rem;
    }
    .si-field input {
        width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px;
        background: #f8fafc; color: #0f172a; font-size: 0.9rem;
        padding: 0.62rem 0.92rem; outline: none; font-family: inherit;
        transition: border-color 0.18s, box-shadow 0.18s;
        box-sizing: border-box;
    }
    .si-field input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.13);
        background: #fff;
    }
    .si-field input::placeholder { color: #cbd5e1; }

    /* sign-in button */
    .si-btn {
        width: 100%; background: #6366f1; color: #fff;
        border: none; border-radius: 10px; font-size: 0.92rem;
        font-weight: 700; padding: 0.72rem; cursor: pointer;
        margin-top: 0.5rem; letter-spacing: 0.2px;
        font-family: inherit;
        box-shadow: 0 4px 14px rgba(99,102,241,0.32);
        transition: background 0.15s, transform 0.12s;
    }
    .si-btn:hover { background: #4f46e5; transform: translateY(-1px); }
    .si-btn:active { transform: scale(0.99); }

    /* divider */
    .si-divider {
        display: flex; align-items: center; gap: 10px; margin: 1.25rem 0;
    }
    .si-div-line { flex: 1; height: 1px; background: #e2e8f0; }
    .si-div-txt  { color: #cbd5e1; font-size: 0.69rem; letter-spacing: 0.5px; white-space: nowrap; }

    /* admin button */
    .si-admin-btn {
        width: 100%; background: #fff; color: #64748b;
        border: 1.5px solid #e2e8f0; border-radius: 10px;
        font-size: 0.82rem; font-weight: 600; padding: 0.6rem;
        cursor: pointer; font-family: inherit;
        transition: border-color 0.15s, color 0.15s, background 0.15s;
    }
    .si-admin-btn:hover { border-color: #6366f1; color: #6366f1; background: #f5f3ff; }

    /* ── Streamlit widget overrides (inputs inside form) ── */
    div[data-testid="stTextInput"] { display: none !important; }
    div[data-testid="stButton"]    { display: none !important; }
    div[data-testid="stAlert"]     { border-radius: 10px !important; }

    /* ── Admin section ── */
    .si-admin-card {
        max-width: 960px; margin: 1.2rem auto 0;
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 16px; padding: 1.5rem 1.8rem;
    }
    .si-admin-card h4 { color: #92400e; font-size: 0.95rem; font-weight: 700; margin: 0 0 1rem; }
    .si-admin-card .si-field input { background: #fff; }
    .si-admin-row { display: flex; gap: 10px; margin-top: 0.8rem; }
    .si-admin-row button { flex: 1; }
    .si-admin-submit {
        background: #d97706; color: #fff; border: none;
        border-radius: 9px; font-size: 0.85rem; font-weight: 700;
        padding: 0.6rem; cursor: pointer; font-family: inherit;
    }
    .si-admin-submit:hover { background: #b45309; }
    .si-admin-cancel {
        background: #fff; color: #64748b;
        border: 1.5px solid #e2e8f0; border-radius: 9px;
        font-size: 0.85rem; font-weight: 600; padding: 0.6rem;
        cursor: pointer; font-family: inherit;
    }
</style>
""", unsafe_allow_html=True)

# ── Render the entire UI as one HTML block ─────────────────────────
html_ui = """
<div class="si-shell">
<div class="si-left">
<div>
<div class="si-brand">
<div class="si-badge">📈</div>
<span class="si-name">Smart Investor</span>
</div>
<div class="si-headline">
<h2>Trade smarter,<br>invest with <em>confidence</em></h2>
<p>Real-time NSE &amp; BSE analytics, risk-adjusted scoring, and your personalised watchlist — all in one place.</p>
</div>
<div class="si-tickers">
<div class="si-tk">
<div class="si-tk-lbl">Nifty 50</div>
<span class="si-tk-val">24,834</span>
<span class="si-up">▲ 1.2%</span>
</div>
<div class="si-tk">
<div class="si-tk-lbl">Sensex</div>
<span class="si-tk-val">81,562</span>
<span class="si-up">▲ 0.9%</span>
</div>
<div class="si-tk">
<div class="si-tk-lbl">Bank Nifty</div>
<span class="si-tk-val">52,140</span>
<span class="si-dn">▼ 0.3%</span>
</div>
<div class="si-tk">
<div class="si-tk-lbl">Nifty IT</div>
<span class="si-tk-val">38,710</span>
<span class="si-up">▲ 2.1%</span>
</div>
</div>
</div>
<div class="si-left-foot">
Powered by Yahoo Finance · MongoDB · Streamlit<br>
Built for smarter, data-driven investing.
</div>
</div>
<div class="si-right">
<div class="si-form-head">
<h3>Welcome back</h3>
<p>Sign in to access your portfolio &amp; insights</p>
</div>
<form id="loginForm" onsubmit="handleLogin(event)">
<div class="si-field">
<label>Email or Username</label>
<input type="text" id="loginUser" placeholder="you@example.com or username" autocomplete="username" required />
</div>
<div class="si-field">
<label>Password</label>
<input type="password" id="loginPass" placeholder="••••••••" autocomplete="current-password" required />
</div>
<div id="loginMsg" style="font-size:0.82rem;margin:0.5rem 0;min-height:1.2rem;color:#ef4444"></div>
<button class="si-btn" type="submit">Sign In →</button>
</form>
<div class="si-divider">
<div class="si-div-line"></div>
<span class="si-div-txt">ADMIN ACCESS</span>
<div class="si-div-line"></div>
</div>
<button class="si-admin-btn" onclick="toggleAdmin()">⚙ Admin Login</button>
</div>
</div>
<div id="adminPanel" style="display:none;max-width:960px;margin:1.2rem auto 0;background:#fffbeb;border:1px solid #fde68a;border-radius:16px;padding:1.5rem 1.8rem;">
<h4 style="color:#92400e;font-size:0.95rem;font-weight:700;margin:0 0 1rem;">🛡 Admin Authentication</h4>
<form id="adminForm" onsubmit="handleAdmin(event)">
<div class="si-field">
<label>Admin Username</label>
<input type="text" id="adminUser" placeholder="admin" style="background:#fff;border:1.5px solid #e2e8f0;border-radius:10px;padding:0.62rem 0.92rem;width:100%;font-size:0.9rem;outline:none;box-sizing:border-box;" />
</div>
<div class="si-field" style="margin-top:0.8rem;">
<label>Admin Password</label>
<input type="password" id="adminPass" placeholder="••••••••" style="background:#fff;border:1.5px solid #e2e8f0;border-radius:10px;padding:0.62rem 0.92rem;width:100%;font-size:0.9rem;outline:none;box-sizing:border-box;" />
</div>
<div id="adminMsg" style="font-size:0.82rem;margin:0.5rem 0;min-height:1.2rem;color:#ef4444"></div>
<div style="display:flex;gap:10px;margin-top:0.6rem;">
<button type="submit" style="flex:1;background:#d97706;color:#fff;border:none;border-radius:9px;font-size:0.85rem;font-weight:700;padding:0.62rem;cursor:pointer;font-family:inherit;">Login as Admin</button>
<button type="button" onclick="toggleAdmin()" style="flex:1;background:#fff;color:#64748b;border:1.5px solid #e2e8f0;border-radius:9px;font-size:0.85rem;font-weight:600;padding:0.62rem;cursor:pointer;font-family:inherit;">⬅ Cancel</button>
</div>
</form>
</div>
<script>
function toggleAdmin() {
var p = document.getElementById('adminPanel');
p.style.display = p.style.display === 'none' ? 'block' : 'none';
}
function handleLogin(e) {
e.preventDefault();
var u = document.getElementById('loginUser').value.trim();
var p = document.getElementById('loginPass').value;
var msg = document.getElementById('loginMsg');
if (!u || !p) { msg.textContent = '⚠ Please fill in all fields.'; return; }
msg.style.color = '#6366f1';
msg.textContent = 'Signing in…';
var url = new URL(window.location.href);
url.searchParams.set('__login_user', encodeURIComponent(u));
url.searchParams.set('__login_pass', encodeURIComponent(p));
window.location.href = url.toString();
}
function handleAdmin(e) {
e.preventDefault();
var u = document.getElementById('adminUser').value.trim();
var p = document.getElementById('adminPass').value;
var url = new URL(window.location.href);
url.searchParams.set('__admin_user', encodeURIComponent(u));
url.searchParams.set('__admin_pass', encodeURIComponent(p));
window.location.href = url.toString();
}
</script>
"""
st.markdown(html_ui, unsafe_allow_html=True)

# ── Handle query-param based login submissions ─────────────────────
qp = st.query_params

if "__login_user" in qp and "__login_pass" in qp:
    from urllib.parse import unquote
    email_or_username = unquote(qp["__login_user"])
    password          = unquote(qp["__login_pass"])
    # Clear params immediately
    st.query_params.clear()

    if auth_utils.login_user(email_or_username, password):
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

if "__admin_user" in qp and "__admin_pass" in qp:
    from urllib.parse import unquote
    admin_user = unquote(qp["__admin_user"])
    admin_pass = unquote(qp["__admin_pass"])
    st.query_params.clear()

    if admin_user == "admin" and admin_pass == "aprilfool1203":
        st.session_state.is_admin         = True
        st.session_state.authenticated    = False
        st.session_state.show_admin_login = False
        st.success("✅ Admin login successful")
        st.switch_page("pages/admin.py")
    else:
        st.error("❌ Invalid admin credentials.")