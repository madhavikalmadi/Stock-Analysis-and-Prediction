import streamlit as st
import auth_utils
import time

st.set_page_config(page_title="Smart Investor | Auth", layout="centered", page_icon="🔐")

# --- BACKEND ---
qp = st.query_params
if "__login_user" in qp:
    from urllib.parse import unquote
    u, p = unquote(qp["__login_user"]), unquote(qp["__login_pass"])
    if auth_utils.login_user(u, p):
        st.session_state.authenticated, st.session_state.username = True, u
        from mongo_db import users_col
        doc = users_col.find_one({"$or": [{"username": u}, {"email": u}]})
        if doc: st.session_state.user_id = str(doc["_id"])
        st.success("Redirecting...")
        time.sleep(0.5)
        st.switch_page("pages/dashboard.py")
    else: st.error("Invalid credentials")

if "__reg_user" in qp:
    from urllib.parse import unquote
    u, e, m, p = unquote(qp["__reg_user"]), unquote(qp["__reg_email"]), unquote(qp["__reg_mob"]), unquote(qp["__reg_pass"])
    if auth_utils.signup_user(u, p, e, m):
        st.success("Account created!")
        time.sleep(1.5)
        st.rerun()
    else: st.error("Signup failed")

# --- UI ---
# We define CSS separately for maximum reliability
css = """
<style>
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; overflow: hidden !important; height: 100vh !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer, [data-testid="stSidebarNav"], #MainMenu { display: none !important; }
    .block-container { padding: 0 !important; height: 100vh; display: flex; align-items: center; justify-content: center; max-width: 100vw !important; overflow: hidden !important; }
    
    .si-shell { display: grid; grid-template-columns: 1fr 1fr; width: 900px; height: 580px; background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
    .si-left { background: #0f172a; padding: 2.5rem; display: flex; flex-direction: column; justify-content: space-between; }
    .si-badge { width: 36px; height: 36px; background: #6366f1; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-bottom: 10px; }
    .si-name { color: #fff; font-size: 0.9rem; font-weight: 800; }
    .si-headline h2 { color: #fff; font-size: 1.6rem; font-weight: 900; line-height: 1.25; margin: 10px 0; }
    .si-headline h2 em { color: #818cf8; font-style: normal; }
    .si-desc { color: #94a3b8; font-size: 0.8rem; line-height: 1.6; border-left: 2px solid #6366f1; padding-left: 12px; }
    .si-tickers { margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; opacity: 1; transition: 0.3s; }
    .si-tick { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.7rem; }
    .st-n { color: #64748b; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; }
    .st-v { color: #fff; font-size: 0.95rem; font-weight: 700; margin-top: 2px; }
    .si-foot { color: #334155; font-size: 0.65rem; }

    .si-right { background: #fff; padding: 3rem; display: flex; flex-direction: column; justify-content: center; }
    .si-head h3 { color: #0f172a; font-size: 1.5rem; font-weight: 900; margin: 0; }
    .si-head p { color: #94a3b8; font-size: 0.85rem; margin: 4px 0 20px 0; }
    
    #l-view, #s-view { display: none; }
    .show-view { display: block !important; }

    .si-fld { margin-bottom: 0.9rem; }
    .si-fld label { display: block; font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 0.3rem; }
    .si-fld input { width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; font-size: 0.9rem; padding: 0.65rem; outline: none; box-sizing: border-box; }
    .si-fld input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.08); }
    
    .si-btn { width: 100%; background: #6366f1; color: #fff; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 700; padding: 0.8rem; cursor: pointer; margin-top: 0.4rem; transition: 0.2s; }
    .si-btn:hover { background: #4f46e5; }
    .si-btn-s { background: #10b981; } .si-btn-s:hover { background: #059669; }

    .si-tgl { text-align: center; margin-top: 1.2rem; font-size: 0.85rem; color: #64748b; }
    .si-lnk { color: #6366f1; font-weight: 700; cursor: pointer; text-decoration: none; }
    
    .si-sep { display: flex; align-items: center; gap: 10px; margin: 1.5rem 0; }
    .si-sep-l { flex: 1; height: 1px; background: #f1f5f9; }
    .si-sep-t { color: #cbd5e1; font-size: 0.55rem; font-weight: 800; }
    .si-adm { width: 100%; background: #fff; color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0.6rem; font-size: 0.8rem; font-weight: 700; cursor: pointer; text-decoration: none; display: block; text-align: center; }
    div[data-testid='stTextInput'], div[data-testid='stButton'] { display: none !important; }
</style>
"""

# The HTML is stripped of spaces to prevent markdown code-block triggers
html_body = """
<div class="si-shell"><div class="si-left"><div><div class="si-badge">📈</div><span class="si-name">Smart Investor</span><div class="si-headline"><h2 id="lh2">Trade smarter,<br>invest with <em>confidence</em></h2></div><div class="si-desc" id="lsh">Real-time NSE & BSE analytics, risk metrics, and personalised watchlists.</div><div class="si-tickers" id="tkb"><div class="si-tick"><div class="st-n">Nifty 50</div><div class="st-v">24,834</div></div><div class="si-tick"><div class="st-n">Sensex</div><div class="st-v">81,562</div></div><div class="si-tick"><div class="st-n">Bank Nifty</div><div class="st-v">52,140</div></div><div class="si-tick"><div class="st-n">IT Index</div><div class="st-v">38,710</div></div></div></div><div class="si-foot">Built for smarter, data-driven investing.</div></div><div class="si-right">
<div id="l-view" class="show-view"><div class="si-head"><h3>Welcome Back</h3><p>Sign in to your portfolio</p></div><form onsubmit="doL(event)"><div class="si-fld"><label>Username</label><input type="text" id="liu" placeholder="Username" required /></div><div class="si-fld"><label>Password</label><input type="password" id="lip" placeholder="••••••••" required /></div><button class="si-btn" type="submit">Sign In →</button></form><div class="si-tgl">No account? <a href="javascript:void(0)" class="si-lnk" onclick="go(1)">Create one</a></div><div class="si-sep"><div class="si-sep-l"></div><span class="si-sep-t">ADMIN</span><div class="si-sep-l"></div></div><a href="/admin" target="_self" class="si-adm">⚙ Admin Dashboard</a></div>
<div id="s-view"><div class="si-head"><h3>Join Us</h3><p>Create your new account</p></div><form onsubmit="doS(event)"><div class="si-fld"><label>Username</label><input type="text" id="siu" placeholder="Choose username" required /></div><div class="si-fld"><label>Email</label><input type="email" id="sie" placeholder="you@example.com" required /></div><div class="si-fld"><label>Mobile</label><input type="tel" id="sim" placeholder="+91..." required /></div><div class="si-fld"><label>Password</label><input type="password" id="sip" placeholder="••••••••" required /></div><button class="si-btn si-btn-s" type="submit">Sign Up →</button></form><div class="si-tgl">Have an account? <a href="javascript:void(0)" class="si-lnk" onclick="go(0)">Sign in</a></div></div>
</div></div>
<script>
function go(s){
  var lv=document.getElementById('l-view'), sv=document.getElementById('s-view'), h2=document.getElementById('lh2'), tb=document.getElementById('tkb');
  if(s){ lv.classList.remove('show-view'); sv.classList.add('show-view'); h2.innerHTML='Start your journey to<br><em>financial freedom</em>'; tb.style.opacity='0.2'; }
  else{ sv.classList.remove('show-view'); lv.classList.add('show-view'); h2.innerHTML='Trade smarter,<br>invest with <em>confidence</em>'; tb.style.opacity='1'; }
}
function doL(e){ e.preventDefault(); var u=document.getElementById('liu').value, p=document.getElementById('lip').value, l=new URL(window.location.href); l.searchParams.set('__login_user',encodeURIComponent(u)); l.searchParams.set('__login_pass',encodeURIComponent(p)); window.location.href=l.toString(); }
function doS(e){ e.preventDefault(); var u=document.getElementById('siu').value, em=document.getElementById('sie').value, m=document.getElementById('sim').value, p=document.getElementById('sip').value, l=new URL(window.location.href); l.searchParams.set('__reg_user',encodeURIComponent(u)); l.searchParams.set('__reg_email',encodeURIComponent(em)); l.searchParams.set('__reg_mob',encodeURIComponent(m)); l.searchParams.set('__reg_pass',encodeURIComponent(p)); window.location.href=l.toString(); }
</script>
"""

st.markdown(css, unsafe_allow_html=True)
st.markdown(html_body, unsafe_allow_html=True)
