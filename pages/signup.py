import streamlit as st
import auth_utils
import time
from mongo_db import users_col

st.set_page_config(page_title="Smart Investor | Join", layout="centered", page_icon="📈")

# If already logged in, go to dashboard
if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

# ── Inject full-page CSS reset ──
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #f0f4f8 !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer,
    [data-testid="stSidebarNav"], #MainMenu { display: none !important; }
    .block-container { padding: 2.5rem 1.5rem 2rem !important; max-width: 960px !important; }
    .si-shell { display: grid; grid-template-columns: 1fr 1fr; min-height: 650px; border-radius: 22px; overflow: hidden; box-shadow: 0 24px 64px rgba(15,23,42,0.18); }
    .si-left { background: #0f172a; padding: 2.8rem 2.4rem; display: flex; flex-direction: column; justify-content: space-between; }
    .si-brand { display: flex; align-items: center; gap: 11px; }
    .si-badge { width: 40px; height: 40px; background: #10b981; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
    .si-name { color: #f8fafc; font-size: 1.05rem; font-weight: 800; letter-spacing: -0.3px; }
    .si-headline { margin-top: 2.4rem; }
    .si-headline h2 { color: #f8fafc; font-size: 1.6rem; font-weight: 900; line-height: 1.28; letter-spacing: -0.6px; margin: 0; }
    .si-headline h2 em { color: #34d399; font-style: normal; }
    .si-headline p { color: #94a3b8; font-size: 0.82rem; margin-top: 0.75rem; line-height: 1.65; border-left: 2px solid #10b981; padding-left: 12px; }
    .si-steps { margin-top: 2.2rem; }
    .si-step { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 1.2rem; }
    .si-step-num { width: 20px; height: 20px; border-radius: 50%; background: #1e293b; color: #10b981; font-size: 0.7rem; font-weight: 800; display: flex; align-items: center; justify-content: center; border: 1px solid #10b981; flex-shrink: 0; }
    .si-step-txt { color: #cbd5e1; font-size: 0.82rem; font-weight: 500; }
    .si-left-foot { color: #334155; font-size: 0.69rem; line-height: 1.7; margin-top: 2rem; }
    .si-right { background: #ffffff; padding: 2.5rem 2.6rem; display: flex; flex-direction: column; justify-content: center; }
    .si-form-head { margin-bottom: 1.5rem; }
    .si-form-head h3 { color: #0f172a; font-size: 1.4rem; font-weight: 900; letter-spacing: -0.5px; margin: 0; }
    .si-form-head p { color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem; }
    .si-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .si-field { margin-bottom: 0.9rem; }
    .si-field label { display: block; font-size: 0.71rem; font-weight: 700; color: #64748b; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 0.35rem; }
    .si-field input { width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; color: #0f172a; font-size: 0.9rem; padding: 0.58rem 0.92rem; outline: none; transition: border-color 0.18s, box-shadow 0.18s; box-sizing: border-box; }
    .si-field input:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.13); background: #fff; }
    .si-btn { width: 100%; background: #10b981; color: #fff; border: none; border-radius: 10px; font-size: 0.92rem; font-weight: 700; padding: 0.72rem; cursor: pointer; margin-top: 0.5rem; letter-spacing: 0.2px; box-shadow: 0 4px 14px rgba(16,185,129,0.32); transition: background 0.15s, transform 0.12s; }
    .si-btn:hover { background: #059669; transform: translateY(-1px); }
    .si-back { text-align: center; margin-top: 1.2rem; font-size: 0.85rem; color: #64748b; }
    .si-back-link { color: #10b981; font-weight: 700; cursor: pointer; text-decoration: none; }
    .si-back-link:hover { text-decoration: underline; }
    div[data-testid="stTextInput"], div[data-testid="stButton"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

html_ui = """
<div class="si-shell">
  <div class="si-left">
    <div>
      <div class="si-brand"><div class="si-badge">🆕</div><span class="si-name">Join Smart Investor</span></div>
      <div class="si-headline"><h2>Start your journey to <em>financial freedom</em></h2><p>Create an account to track indices and leverage institutional-grade risk metrics.</p></div>
      <div class="si-steps">
        <div class="si-step"><div class="si-step-num">1</div><div class="si-step-txt">Create your profile with basic details</div></div>
        <div class="si-step"><div class="si-step-num">2</div><div class="si-step-txt">Connect to real-time market data</div></div>
        <div class="si-step"><div class="si-step-num">3</div><div class="si-step-txt">Build and analyze your portfolio</div></div>
      </div>
    </div>
    <div class="si-left-foot">Join 5,000+ investors making data-driven decisions every day.</div>
  </div>
  <div class="si-right">
    <div class="si-form-head"><h3>Create Account</h3><p>Get started with your free account today</p></div>
    <form id="signupForm" onsubmit="handleSignup(event)">
      <div class="si-field"><label>Username</label><input type="text" id="regUser" placeholder="Choose a username" required /></div>
      <div class="si-field"><label>Email Address</label><input type="email" id="regEmail" placeholder="you@example.com" required /></div>
      <div class="si-field"><label>Mobile Number</label><input type="tel" id="regMob" placeholder="Enter mobile number" required /></div>
      <div class="si-row">
        <div class="si-field"><label>Password</label><input type="password" id="regPass" placeholder="••••••••" required /></div>
        <div class="si-field"><label>Confirm</label><input type="password" id="regConf" placeholder="••••••••" required /></div>
      </div>
      <div id="signUpMsg" style="font-size:0.82rem;margin:0.5rem 0;min-height:1.2rem;color:#ef4444"></div>
      <button class="si-btn" type="submit">Create Account →</button>
    </form>
    <div class="si-back">Already have an account? <a href="/" target="_self" class="si-back-link">Sign in</a></div>
  </div>
</div>
<script>
function handleSignup(e) {
  e.preventDefault();
  var u = document.getElementById('regUser').value.trim();
  var eVal = document.getElementById('regEmail').value.trim();
  var m = document.getElementById('regMob').value.trim();
  var p = document.getElementById('regPass').value;
  var c = document.getElementById('regConf').value;
  var msg = document.getElementById('signUpMsg');
  if (p !== c) { msg.textContent = '⚠ Passwords do not match.'; return; }
  if (p.length < 8) { msg.textContent = '⚠ Password must be at least 8 characters.'; return; }
  msg.style.color = '#10b981';
  msg.textContent = 'Creating account...';
  var url = new URL(window.location.href);
  url.searchParams.set('__reg_user', encodeURIComponent(u));
  url.searchParams.set('__reg_email', encodeURIComponent(eVal));
  url.searchParams.set('__reg_mob', encodeURIComponent(m));
  url.searchParams.set('__reg_pass', encodeURIComponent(p));
  window.location.href = url.toString();
}
</script>
"""
st.markdown(html_ui, unsafe_allow_html=True)

# ── Handle queryparams ──
qp = st.query_params
if "__reg_user" in qp:
    from urllib.parse import unquote
    u = unquote(qp["__reg_user"])
    e = unquote(qp["__reg_email"])
    m = unquote(qp["__reg_mob"])
    p = unquote(qp["__reg_pass"])
    st.query_params.clear()
    if auth_utils.signup_user(u, p, e, m):
        st.success(f"✅ Account created successfully for {u}!")
        time.sleep(2)
        st.switch_page("login.py")
    else:
        st.error("❌ Failed to create account. Username might already exist.")
