import streamlit as st
from mongo_db import users_col, watchlist_col, actions_col
from datetime import datetime, timezone
import pandas as pd

st.set_page_config(page_title="Smart Investor | Admin", layout="wide", page_icon="⚙️")

# =====================================================
# AUTH GUARD
# =====================================================
if not st.session_state.get("is_admin"):
    qp = st.query_params
    if "__a_u" in qp:
        from urllib.parse import unquote
        u = unquote(qp["__a_u"])
        p = unquote(qp["__a_p"])
        if u == "admin" and p == "aprilfool1203":
            st.session_state.is_admin = True
            st.query_params.clear()
            st.rerun()
        else:
            import time
            st.error("Invalid credentials.")
            time.sleep(1.5)
            st.query_params.clear()
            st.rerun()

    right_inner = (
        '<div class="si-head"><h3>Admin Console</h3><p>Restricted access area</p></div>'
        '<form action="" method="GET" target="_self">'
        '<div class="si-fld"><label>Admin Username</label><input type="text" name="__a_u" placeholder="Admin username" required /></div>'
        '<div class="si-fld"><label>Admin Password</label><input type="password" name="__a_p" placeholder="••••••••" required /></div>'
        '<button class="si-btn" type="submit">Authenticate →</button>'
        '<div class="si-sep"><div class="si-sep-l"></div><span class="si-sep-t">RETURN</span><div class="si-sep-l"></div></div>'
        '<a href="/" target="_self" class="si-adm">⬅ Back to Application</a>'
        '</form>'
    )
    ui_markup = """
    <style>
    [data-testid="stAppViewContainer"] { background: #f1f5f9 !important; overflow: hidden !important; height: 100vh !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer, [data-testid="stSidebarNav"], #MainMenu { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100vw !important; margin: 0 !important; }
    .si-bd { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #f1f5f9; display: flex; align-items: center; justify-content: center; z-index: 999; }
    .si-sh { display: grid; grid-template-columns: 1fr 1.1fr; width: 880px; min-height: 550px; height: auto; background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
    .si-l { background: #0f172a; padding: 2.2rem; display: flex; flex-direction: column; justify-content: space-between; }
    .si-bdg { width: 34px; height: 34px; background: #f0c040; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .si-tag { color: #fff; font-size:0.9rem; font-weight:800; margin-top:8px; display:block; }
    .si-h2 h2 { color: #fff; font-size: 1.5rem; font-weight: 900; line-height: 1.25; margin: 12px 0; }
    .si-h2 h2 em { color: #f0c040; font-style: normal; }
    .si-p { color: #94a3b8; font-size: 0.8rem; line-height: 1.6; border-left: 2px solid #f0c040; padding-left: 10px; }
    .si-st { margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; opacity: 1; }
    .si-ti { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.7rem; }
    .si-ti div:first-child { color: #64748b; font-size: 0.55rem; font-weight: 800; }
    .si-ti div:last-child { color: #fff; font-size: 0.9rem; font-weight: 700; }
    .si-r { background: #fff; padding: 2.5rem; display: flex; flex-direction: column; justify-content: center; }
    .si-head h3 { color: #0f172a; font-size: 1.4rem; font-weight: 900; margin: 0; }
    .si-head p { color: #94a3b8; font-size: 0.82rem; margin: 4px 0 18px 0; }
    .si-fld { margin-bottom: 0.9rem; }
    .si-fld label { display: block; font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 0.35rem; }
    .si-fld input { width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; font-size: 0.9rem; padding: 0.65rem 0.8rem; outline: none; box-sizing: border-box; }
    .si-btn { width: 100%; background: #0f172a; color: #fff; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 700; padding: 0.8rem; cursor: pointer; margin-top: 0.4rem; display: block; text-align: center; text-decoration: none; }
    .si-btn:hover { background: #1e293b; }
    .si-sw { text-align: center; margin-top: 1.2rem; font-size: 0.85rem; color: #64748b; }
    .si-lnk { color: #f0c040; font-weight: 700; text-decoration: none; }
    .si-sep { display: flex; align-items: center; gap: 10px; margin: 1.5rem 0; }
    .si-sep-l { flex: 1; height: 1px; background: #e2e8f0; }
    .si-sep-t { color: #94a3b8; font-size: 0.55rem; font-weight: 800; }
    .si-adm { width: 100%; background: #fff; color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0.6rem; font-size: 0.8rem; font-weight: 700; text-decoration: none; display: block; text-align: center; }
    </style>
    <div class="si-bd">
        <div class="si-sh">
            <div class="si-l">
                <div>
                    <div class="si-bdg">⚙</div>
                    <span class="si-tag">System Admin</span>
                    <div class="si-h2"><h2>System<br><em>Control Panel</em></h2></div>
                    <div class="si-p">Manage users, adjust platform settings, and monitor activities.</div>
                    <div class="si-st">
                        <div class="si-ti"><div>STATUS</div><div style="color:#34c759">ONLINE</div></div>
                        <div class="si-ti"><div>DB LINK</div><div style="color:#34c759">SECURE</div></div>
                    </div>
                </div>
                <div style="color:#334155; font-size:0.6rem;">Smart Investor Administrative Hub.</div>
            </div>
            <div class="si-r">""" + right_inner + """</div>
        </div>
    </div>
    """
    st.markdown(ui_markup, unsafe_allow_html=True)
    st.stop()

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #ffffff 0%, #f1f5f9 60%, #e2e8f0 100%);
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b14 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(15,23,42,0.15) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* ── Main area ── */
.block-container { padding: 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Top bar ── */
.admin-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.5rem 0; border-bottom: 2px solid rgba(15, 23, 42, 0.05); margin-bottom: 2.5rem;
}
.admin-brand { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.8rem; background: linear-gradient(135deg, #0f172a, #4338ca); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.admin-brand span { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; letter-spacing: 2.5px; text-transform: uppercase; display: block; margin-top: 0px; -webkit-text-fill-color: #64748b; font-weight: 700; }
.admin-badge { background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 20px; padding: 4px 14px; font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #4338ca; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; box-shadow: 0 0 10px rgba(99,102,241,0.1); }

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 2.5rem; }
.stat-card {
    background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 16px; padding: 1.6rem 1.8rem;
    position: relative; overflow: hidden; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 8px 32px rgba(15, 23, 42, 0.03), inset 0 2px 4px rgba(255,255,255,0.7);
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06), inset 0 2px 4px rgba(255,255,255,1); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent, #6366f1), transparent); opacity: 0.8; }
.stat-icon { font-size: 1.6rem; margin-bottom: 0.8rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.stat-value { font-family: 'DM Serif Display', Georgia, serif; font-size: 2.2rem; color: #0f172a; line-height: 1; margin-bottom: 4px; }
.stat-label { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.stat-sub { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; margin-top: 6px; font-weight: 600; }
.stat-up { color: #10b981; } .stat-dn { color: #ef4444; }

/* ── Section headers ── */
.section-hdr { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; font-weight: 800; letter-spacing: 2.5px; text-transform: uppercase; color: #334155; padding-bottom: 12px; border-bottom: 2px solid rgba(15, 23, 42, 0.04); margin-bottom: 1.5rem; }

/* ── Table override ── */
.stDataFrame, [data-testid="stDataFrame"] { background: rgba(255, 255, 255, 0.5) !important; backdrop-filter: blur(10px) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.6) !important; overflow: hidden !important; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.02) !important; }
[data-testid="stDataFrame"] * { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; color: #334155 !important; }
[data-testid="stDataFrame"] th { background: rgba(255, 255, 255, 0.8) !important; color: #1e293b !important; font-size: 0.72rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; border-bottom: 1px solid rgba(15, 23, 42, 0.05) !important; font-weight: 800 !important; }

/* ── Panel card ── */
.panel-card { background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 16px; padding: 1.8rem 2rem; margin-bottom: 1.2rem; box-shadow: 0 8px 32px rgba(15, 23, 42, 0.03), inset 0 2px 4px rgba(255,255,255,0.7); }

/* ── Buttons ── */
.stButton > button:first-child { background: linear-gradient(135deg, #1e293b, #0f172a) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 700 !important; padding: 0.6rem 1.4rem !important; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15), inset 0 1px 1px rgba(255,255,255,0.1) !important; transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important; }
.stButton > button:first-child:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 16px rgba(15, 23, 42, 0.2) !important; }
.stButton > button[kind="secondary"] { background: rgba(239, 68, 68, 0.08) !important; backdrop-filter: blur(5px) !important; color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; font-weight: 700 !important; box-shadow: none !important;}
.stButton > button[kind="secondary"]:hover { background: rgba(239, 68, 68, 0.15) !important; transform: translateY(-1px) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div { background: rgba(255, 255, 255, 0.8) !important; border: 1px solid rgba(15, 23, 42, 0.08) !important; border-radius: 10px !important; color: #0f172a !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; transition: all 0.2s !important; padding: 0.65rem 0.8rem !important; }
.stTextInput > div > div > input:focus { border-color: #6366f1 !important; background: #ffffff !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15), inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; }
.stTextInput > label, .stSelectbox > label { color: #475569 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; margin-bottom: 0.4rem !important; }

/* ── Alerts ── */
.stSuccess > div { background: rgba(220, 252, 231, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(134, 239, 172, 0.5) !important; border-radius: 12px !important; color: #166534 !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05) !important; font-weight: 600 !important; }
.stError > div { background: rgba(254, 226, 226, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(252, 165, 165, 0.5) !important; border-radius: 12px !important; color: #991b1b !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(153, 27, 27, 0.05) !important; font-weight: 600 !important; }
.stWarning > div { background: rgba(254, 249, 195, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(253, 224, 71, 0.5) !important; border-radius: 12px !important; color: #854d0e !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(133, 77, 14, 0.05) !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: rgba(226, 232, 240, 0.6) !important; backdrop-filter: blur(10px) !important; border-radius: 14px !important; padding: 6px !important; border: 1px solid rgba(255, 255, 255, 0.5) !important; gap: 4px !important; box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.02) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #64748b !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; font-weight: 600 !important; border-radius: 10px !important; padding: 0.5rem 1.4rem !important; border: none !important; transition: all 0.2s !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #0f172a !important; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important; font-weight: 700 !important; }

/* ── Search / filter ── */
.filter-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 1rem; }

/* ── User row card ── */
.user-row { display: flex; align-items: center; justify-content: space-between; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px; padding: 1.2rem 1.6rem; margin-bottom: 12px; transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02); }
.user-row:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); border-color: #cbd5e1; background: #ffffff; }
.user-avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #e0e7ff, #c7d2fe); border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center; font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 800; color: #4338ca; flex-shrink: 0; margin-right: 16px; box-shadow: 0 2px 6px rgba(67, 56, 202, 0.15); }
.user-info { flex: 1; }
.user-name { font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 800; color: #0f172a; }
.user-meta { font-family: 'DM Sans', sans-serif; font-size: 0.78rem; color: #64748b; margin-top: 4px; }
.user-mono { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; }

/* ── Log/Activity (if any) ── */
.log-row { display: flex; gap: 12px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# TOP BAR
# =====================================================
st.markdown("""
<div class="admin-topbar">
    <div class="admin-brand">
        ⚙ Admin Console
        <span>Smart Investor · Restricted Access</span>
    </div>
    <div class="admin-badge">● Live</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FETCH DATA
# =====================================================
def get_stats():
    try:
        total_users = users_col.count_documents({}) if users_col is not None else 0
        watchlist_entries = watchlist_col.count_documents({}) if watchlist_col is not None else 0
        action_count = actions_col.count_documents({}) if actions_col is not None else 0
        return total_users, watchlist_entries, action_count
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 0, 0, 0

def get_all_users():
    try:
        if users_col is not None:
             users = list(users_col.find({}, {"_id": 1, "username": 1, "email": 1, "mobile": 1, "password": 1}))
             return users
        return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []



total_users, watchlist_entries, action_count = get_stats()
all_users = get_all_users()

# =====================================================
# STAT CARDS
# =====================================================
st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card" style="--accent:#f0c040;">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{total_users}</div>
        <div class="stat-label">Total Users</div>
        <div class="stat-sub stat-up">Registered accounts</div>
    </div>
    <div class="stat-card" style="--accent:#34c759;">
        <div class="stat-icon">⭐</div>
        <div class="stat-value">{watchlist_entries}</div>
        <div class="stat-label">Watchlist Entries</div>
        <div class="stat-sub stat-up">Across all users</div>
    </div>
    <div class="stat-card" style="--accent:#0a84ff;">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">{action_count}</div>
        <div class="stat-label">User Actions</div>
        <div class="stat-sub" style="color:#4a7090;">Logged interactions</div>
    </div>
    <div class="stat-card" style="--accent:#bf5af2;">
        <div class="stat-icon">🏦</div>
        <div class="stat-value">NSE</div>
        <div class="stat-label">Primary Exchange</div>
        <div class="stat-sub" style="color:#4a5070;">NIFTYBEES benchmark</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MAIN TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(["👥  User Management", "➕  Add User", "🔑  Reset Password", "📋  System Info"])

# ─────────────────────────────
# TAB 1: USER MANAGEMENT
# ─────────────────────────────
with tab1:
    st.markdown('<div class="section-hdr">All Registered Users</div>', unsafe_allow_html=True)

    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_q = st.text_input("Search users", placeholder="Search by username or email…", key="search_users",
                                  label_visibility="collapsed")
    with col_sort:
        sort_by = st.selectbox("Sort", ["Username A–Z", "Username Z–A", "Email"], label_visibility="collapsed")

    if all_users:
        filtered = all_users
        if search_q:
            sq = search_q.lower()
            filtered = [u for u in filtered if sq in u.get("username","").lower() or sq in u.get("email","").lower()]

        if sort_by == "Username A–Z":
            filtered = sorted(filtered, key=lambda u: u.get("username","").lower())
        elif sort_by == "Username Z–A":
            filtered = sorted(filtered, key=lambda u: u.get("username","").lower(), reverse=True)
        elif sort_by == "Email":
            filtered = sorted(filtered, key=lambda u: u.get("email","").lower())

        st.markdown(f"<div style='font-family:DM Sans,sans-serif;font-size:0.78rem;color:#1e293b;margin-bottom:12px;'>Showing {len(filtered)} of {len(all_users)} users</div>", unsafe_allow_html=True)

        # Render user rows
        for user in filtered:
            uid = str(user.get("_id", ""))
            uname = user.get("username", "—")
            uemail = user.get("email", "—")
            umobile = user.get("mobile", "—")
            upass = user.get("password", "—")
            avatar_letter = uname[0].upper() if uname else "?"

            col_info, col_actions = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="user-row">
                    <div class="user-avatar">{avatar_letter}</div>
                    <div class="user-info">
                        <div class="user-name">{uname}</div>
                        <div class="user-meta">✉ {uemail} &nbsp;·&nbsp; 📱 {umobile}</div>
                        <div class="user-mono">ID: {uid[:24]}…</div>
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#2a4868;background:rgba(240,192,64,0.06);padding:4px 10px;border-radius:6px;border:1px solid rgba(240,192,64,0.1);">
                        pw: {upass[:16]}{'…' if len(upass) > 16 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_actions:
                if st.button("🗑 Delete", key=f"del_{uid}", type="secondary"):
                    st.session_state[f"confirm_del_{uid}"] = True

            if st.session_state.get(f"confirm_del_{uid}"):
                st.warning(f"⚠ Delete **{uname}**? This cannot be undone.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirm Delete", key=f"confirm_yes_{uid}"):
                        users_col.delete_one({"_id": user["_id"]})
                        st.success(f"User '{uname}' deleted.")
                        st.session_state.pop(f"confirm_del_{uid}", None)
                        st.cache_data.clear()
                        st.rerun()
                with c2:
                    if st.button("✗ Cancel", key=f"confirm_no_{uid}"):
                        st.session_state.pop(f"confirm_del_{uid}", None)
                        st.rerun()

        # Downloadable CSV
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if filtered:
            df = pd.DataFrame([{
                "Username": u.get("username",""),
                "Email": u.get("email",""),
                "Mobile": u.get("mobile",""),
                "ID": str(u.get("_id",""))
            } for u in filtered])
            csv = df.to_csv(index=False)
            st.download_button("⬇ Export CSV", csv, "users.csv", "text/csv", use_container_width=False)
    else:
        st.info("No users found in the database.")

# ─────────────────────────────
# TAB 2: ADD USER
# ─────────────────────────────
with tab2:
    st.markdown('<div class="section-hdr">Create New User Account</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        new_username = st.text_input("Username", placeholder="e.g. investor_raj", key="au_user")
        new_email    = st.text_input("Email Address", placeholder="raj@example.com", key="au_email")
    with col_b:
        new_mobile   = st.text_input("Mobile Number", placeholder="9876543210", key="au_mobile")
        new_password = st.text_input("Password", type="password", placeholder="Min. 8 characters", key="au_pw")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Create Account", key="add_user_btn", use_container_width=False):
        if not all([new_username, new_email, new_mobile, new_password]):
            st.error("All fields are required.")
        elif len(new_password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            import auth_utils
            result = auth_utils.signup_user(new_username, new_password, new_email, new_mobile)
            if result:
                st.success(f"Account created for '{new_username}' successfully.")
                st.cache_data.clear()
            else:
                st.error("Username already exists. Choose a different one.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────
# TAB 3: RESET PASSWORD
# ─────────────────────────────
with tab3:
    st.markdown('<div class="section-hdr">Reset User Password</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        target_user = st.text_input("Username to Reset", placeholder="Enter exact username", key="rp_user")
    with col_r2:
        new_pw      = st.text_input("New Password", type="password", placeholder="Min. 8 characters", key="rp_newpw")
        confirm_pw  = st.text_input("Confirm New Password", type="password", placeholder="Repeat password", key="rp_confirmpw")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Reset Password", key="reset_pw_btn"):
        if not target_user or not new_pw or not confirm_pw:
            st.error("All fields are required.")
        elif len(new_pw) < 8:
            st.error("Password must be at least 8 characters.")
        elif new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            result = users_col.update_one(
                {"username": {"$regex": f"^{target_user}$", "$options": "i"}},
                {"$set": {"password": new_pw}}
            )
            if result.matched_count:
                st.success(f"Password reset for '{target_user}'.")
            else:
                st.error(f"User '{target_user}' not found.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────
# TAB 4: SYSTEM INFO
# ─────────────────────────────
with tab4:
    st.markdown('<div class="section-hdr">System Overview</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="panel-card">
            <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#1e293b;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:12px;">Application</div>
            <table style="width:100%;font-family:'DM Sans',sans-serif;font-size:0.83rem;border-collapse:collapse;">
                <tr><td style="color:#1e293b;padding:5px 0;width:40%;">Framework</td><td style="color:#1e293b;">Streamlit (Python)</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Database</td><td style="color:#1e293b;">MongoDB Atlas</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Market Data</td><td style="color:#1e293b;">Yahoo Finance (yfinance)</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Benchmark</td><td style="color:#1e293b;">NIFTYBEES.NS</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Exchange</td><td style="color:#1e293b;">NSE / BSE (India)</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Timezone</td><td style="color:#1e293b;">IST (UTC+5:30)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div class="panel-card">
            <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#1e293b;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:12px;">Analytics Engine</div>
            <table style="width:100%;font-family:'DM Sans',sans-serif;font-size:0.83rem;border-collapse:collapse;">
                <tr><td style="color:#1e293b;padding:5px 0;">Compounded Annual Growth - CAGR</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Risk-adjusted return - Sharpe Ratio</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Downside deviation - Sortino Ratio</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Peak-to-trough - Max Drawdown</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">Drawdown recovery - Recovery Days</td></tr>
                <tr><td style="color:#1e293b;padding:5px 0;">10-year rolling - Score Window</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel-card" style="margin-top:0;">
        <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#1e293b;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:10px;">Collections</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <div style="background:rgba(240,192,64,0.06);border:1px solid rgba(240,192,64,0.12);border-radius:8px;padding:6px 14px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#8aabcc;">users</div>
            <div style="background:rgba(240,192,64,0.06);border:1px solid rgba(240,192,64,0.12);border-radius:8px;padding:6px 14px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#8aabcc;">watchlist</div>
            <div style="background:rgba(240,192,64,0.06);border:1px solid rgba(240,192,64,0.12);border-radius:8px;padding:6px 14px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#8aabcc;">user_actions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 0.5rem;">
        <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#1e293b;margin-bottom:4px;">⚙ Admin</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#2a3848;letter-spacing:1.5px;text-transform:uppercase;">Control Panel</div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.06);margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#4a6680;margin-bottom:0.4rem;">
        <strong style="color:#8aabcc;">Users</strong><br>
        <span style="font-size:1.3rem;color:#1e293b;font-family:'DM Serif Display',serif;">{total_users}</span> registered
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#4a6680;margin-bottom:1rem;">
        <strong style="color:#8aabcc;">Watchlist</strong><br>
        <span style="font-size:1.3rem;color:#34c759;font-family:'DM Serif Display',serif;">{watchlist_entries}</span> entries
    </div>
    <hr style="border-color:rgba(255,255,255,0.06);margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("⬅ Back to App", use_container_width=True, key="admin_back"):
        st.session_state.is_admin = False
        st.switch_page("login.py")

    st.markdown("""
    <div style="position:absolute;bottom:1.5rem;left:1.2rem;right:1.2rem;font-family:'DM Sans',sans-serif;font-size:0.7rem;color:#1a2838;text-align:center;letter-spacing:0.5px;">
        Smart Investor Admin<br>Restricted Access Only
    </div>
    """, unsafe_allow_html=True)