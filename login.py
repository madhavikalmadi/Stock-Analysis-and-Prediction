import streamlit as st
import auth_utils
import time
from mongo_db import users_col

# 1. PAGE CONFIG
st.set_page_config(page_title="Smart Investor", layout="wide", page_icon="🔐")

# 2. BACKEND PROCESSING
qp = st.query_params
auth_mode = qp.get("mode", "login")

if "__login_user" in qp:
    from urllib.parse import unquote
    u, p = unquote(qp["__login_user"]), unquote(qp["__login_pass"])
    if auth_utils.login_user(u, p):
        st.session_state.authenticated, st.session_state.username = True, u
        doc = users_col.find_one({"$or": [{"username": u}, {"email": u}]})
        if doc: st.session_state.user_id = str(doc["_id"])
        st.success("Redirecting...")
        time.sleep(0.5)
        st.switch_page("pages/dashboard.py")
    else:
        st.error("Invalid credentials")
        time.sleep(2)
        st.rerun()

if "__reg_user" in qp:
    from urllib.parse import unquote
    u, e, m, p = unquote(qp["__reg_user"]), unquote(qp["__reg_email"]), unquote(qp["__reg_mob"]), unquote(qp["__reg_pass"])
    if auth_utils.signup_user(u, p, e, m):
        st.success("Account created!")
        time.sleep(1.5)
        st.query_params["mode"] = "login"
        st.rerun()
    else:
        st.error("Signup failed")
        time.sleep(2)
        st.rerun()

# 3. CONSOLIDATED UI (No indentation to prevent markdown artifacts)
left_title = "Start your journey to<br><em>financial freedom</em>" if auth_mode == "signup" else "Trade smarter,<br>invest with <em>confidence</em>"
left_desc = "Unlock institutional-grade metrics." if auth_mode == "signup" else "Real-time NSE analytics and risk-adjusted scoring."
left_op = "1"

# We build the right side HTML separately to ensure zero indentation
if auth_mode == "login":
    right_inner = (
        '<div class="si-head"><h3>Welcome Back</h3><p>Sign in to your account</p></div>'
        '<form action="/" method="GET" target="_self">'
        '<div class="si-fld"><label>Username</label><input type="text" name="__login_user" placeholder="Username" required /></div>'
        '<div class="si-fld"><label>Password</label><input type="password" name="__login_pass" placeholder="••••••••" required /></div>'
        '<button class="si-btn" type="submit">Sign In →</button>'
        '<div class="si-sw">No account? <a href="?mode=signup" target="_self" class="si-lnk">Create one</a></div>'
        '</form>'
        '<div class="si-sep"><div class="si-sep-l"></div><span class="si-sep-t">ADMIN</span><div class="si-sep-l"></div></div>'
        '<a href="/admin" target="_self" class="si-adm">⚙ Admin Dashboard</a>'
    )
else:
    right_inner = (
        '<div class="si-head"><h3>Join Us</h3><p>Create your new account</p></div>'
        '<form action="/" method="GET" target="_self">'
        '<div class="si-fld"><label>Username</label><input type="text" name="__reg_user" placeholder="Username" required /></div>'
        '<div class="si-fld"><label>Email</label><input type="email" name="__reg_email" placeholder="Email" required /></div>'
        '<div class="si-fld"><label>Mobile</label><input type="tel" name="__reg_mob" placeholder="+91..." required /></div>'
        '<div class="si-fld"><label>Password</label><input type="password" name="__reg_pass" placeholder="••••••••" required /></div>'
        '<button class="si-btn si-btn-s" type="submit">Sign Up →</button>'
        '<div class="si-sw">Have an account? <a href="?mode=login" target="_self" class="si-lnk">Sign in</a></div>'
        '</form>'
    )

ui_markup = f"""
<style>
[data-testid="stAppViewContainer"] {{ background: #f1f5f9 !important; overflow: hidden !important; height: 100vh !important; }}
[data-testid="stHeader"], [data-testid="stToolbar"], footer, [data-testid="stSidebarNav"], #MainMenu {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100vw !important; margin: 0 !important; }}
.si-bd {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #f1f5f9; display: flex; align-items: center; justify-content: center; z-index: 999; }}
.si-sh {{ display: grid; grid-template-columns: 1fr 1.1fr; width: 880px; min-height: 550px; height: auto; background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
.si-l {{ background: #0f172a; padding: 2.2rem; display: flex; flex-direction: column; justify-content: space-between; }}
.si-bdg {{ width: 34px; height: 34px; background: #6366f1; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 18px; }}
.si-tag {{ color: #fff; font-size:0.9rem; font-weight:800; margin-top:8px; display:block; }}
.si-h2 h2 {{ color: #fff; font-size: 1.5rem; font-weight: 900; line-height: 1.25; margin: 12px 0; }}
.si-h2 h2 em {{ color: #818cf8; font-style: normal; }}
.si-p {{ color: #94a3b8; font-size: 0.8rem; line-height: 1.6; border-left: 2px solid #6366f1; padding-left: 10px; }}
.si-st {{ margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; opacity: {left_op}; }}
.si-ti {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.7rem; }}
.si-ti div:first-child {{ color: #64748b; font-size: 0.52rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
.si-ti div:last-child {{ color: #fff; font-size: 0.82rem; font-weight: 700; }}
.si-r {{ background: #fff; padding: 2.5rem; display: flex; flex-direction: column; justify-content: center; }}
.si-head h3 {{ color: #0f172a; font-size: 1.4rem; font-weight: 900; margin: 0; }}
.si-head p {{ color: #94a3b8; font-size: 0.82rem; margin: 4px 0 18px 0; }}
.si-fld {{ margin-bottom: 0.9rem; }}
.si-fld label {{ display: block; font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 0.35rem; }}
.si-fld input {{ width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; font-size: 0.9rem; padding: 0.65rem 0.8rem; outline: none; box-sizing: border-box; }}
.si-btn {{ width: 100%; background: #6366f1; color: #fff; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 700; padding: 0.8rem; cursor: pointer; margin-top: 0.4rem; display: block; text-align: center; text-decoration: none; }}
.si-btn:hover {{ background: #4f46e5; }}
.si-btn-s {{ background: #10b981; }}
.si-sw {{ text-align: center; margin-top: 1.2rem; font-size: 0.85rem; color: #64748b; }}
.si-lnk {{ color: #6366f1; font-weight: 700; text-decoration: none; }}
.si-sep {{ display: flex; align-items: center; gap: 10px; margin: 1.5rem 0; }}
.si-sep-l {{ flex: 1; height: 1px; background: #f1f5f9; }}
.si-sep-t {{ color: #cbd5e1; font-size: 0.55rem; font-weight: 800; }}
.si-adm {{ width: 100%; background: #fff; color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0.6rem; font-size: 0.8rem; font-weight: 700; text-decoration: none; display: block; text-align: center; }}
</style>
<div class="si-bd"><div class="si-sh"><div class="si-l"><div><div class="si-bdg">📈</div><span class="si-tag">Smart Investor</span><div class="si-h2"><h2>{left_title}</h2></div><div class="si-p">{left_desc}</div><div class="si-st"><div class="si-ti"><div>NIFTY 50</div><div>24,834</div></div><div class="si-ti"><div>SENSEX</div><div>81,562</div></div><div class="si-ti"><div>NIFTY BANK</div><div>51,280</div></div><div class="si-ti"><div>NIFTY IT</div><div>38,415</div></div></div></div><div style="color:#334155; font-size:0.6rem;">Precision stock analysis for India.</div></div><div class="si-r">{right_inner}</div></div></div>
"""

st.markdown(ui_markup, unsafe_allow_html=True)
