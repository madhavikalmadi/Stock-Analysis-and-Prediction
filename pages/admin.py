import streamlit as st
from mongo_db import users_col, watchlist_col, actions_col, db
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
.block-container { padding: 2.5rem 3rem !important; max-width: 100% !important; }

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
.stButton > button { background: linear-gradient(135deg, #1e293b, #0f172a) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 700 !important; padding: 0.6rem 1.4rem !important; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15), inset 0 1px 1px rgba(255,255,255,0.1) !important; transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 16px rgba(15, 23, 42, 0.2) !important; }
.stButton > button[kind="secondary"]:hover { transform: translateY(-1px) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div { background: rgba(255, 255, 255, 0.8) !important; border: 1px solid rgba(15, 23, 42, 0.08) !important; border-radius: 10px !important; color: #0f172a !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; transition: all 0.2s !important; padding: 0.65rem 0.8rem !important; }
.stTextInput > div > div > input:focus { border-color: #6366f1 !important; background: #ffffff !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15), inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; }
.stTextInput > label, .stSelectbox > label { color: #475569 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; margin-bottom: 0.4rem !important; }

/* ── Alerts ── */
.stSuccess > div { background: rgba(220, 252, 231, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(134, 239, 172, 0.5) !important; border-radius: 12px !important; color: #166534 !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05) !important; font-weight: 600 !important; }
.stError > div { background: rgba(254, 226, 226, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(252, 165, 165, 0.5) !important; border-radius: 12px !important; color: #991b1b !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(153, 27, 27, 0.05) !important; font-weight: 600 !important; }
.stWarning > div { background: rgba(254, 249, 195, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(253, 224, 71, 0.5) !important; border-radius: 12px !important; color: #854d0e !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(133, 77, 14, 0.05) !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; padding: 0 !important; border: none !important; gap: 24px !important; box-shadow: none !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #475569 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 600 !important; padding: 8px 0 !important; border: none !important; transition: all 0.2s !important; border-bottom: 2px solid transparent !important; }
.stTabs [aria-selected="true"] { color: #0f172a !important; font-weight: 800 !important; border-bottom: 2px solid #0f172a !important; }

/* ── User ID Card (Portrait) ── */
.user-card {
    background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 24px; padding: 0; margin-bottom: 25px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
    overflow: hidden; display: flex; flex-direction: column; height: 100%;
}
.user-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(15, 23, 42, 0.1); border-color: #cbd5e1; }
.card-banner { height: 80px; background: linear-gradient(135deg, #0f172a, #1e293b); position: relative; }
.card-avatar-wrap { position: absolute; top: 40px; left: 50%; transform: translateX(-50%); }
.card-avatar {
    width: 80px; height: 80px; border-radius: 22px; background: #ffffff;
    border: 4px solid #ffffff; box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: #0f172a;
}
.card-content { padding: 50px 1.5rem 1.5rem 1.5rem; text-align: center; flex: 1; }
.card-name { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.4rem; color: #0f172a; margin-bottom: 6px; }
.card-email { font-family: 'DM Sans', sans-serif; font-size: 0.85rem; color: #64748b; margin-bottom: 12px; }
.card-meta-grid { display: grid; grid-template-columns: 1fr; gap: 8px; margin: 15px 0; padding: 12px 0; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; }
.card-meta-item { display: flex; align-items: center; justify-content: center; gap: 8px; font-family: 'DM Sans', sans-serif; font-size: 0.8rem; color: #475569; font-weight: 500; }
.card-meta-item span { opacity: 0.6; font-size: 0.9rem; }
.card-actions { padding: 1rem 1.5rem 1.8rem 1.5rem; }

/* ── Danger Button (Soft) ── */
.del-btn-wrapper .stButton > button {
    background: rgba(239, 68, 68, 0.04) !important;
    color: #ef4444 !important;
    border: 1px solid rgba(239, 68, 68, 0.15) !important;
    box-shadow: none !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
    font-size: 0.75rem !important;
}
.del-btn-wrapper .stButton > button:hover {
    background: rgba(239, 68, 68, 0.1) !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
    transform: none !important;
}

/* ── Credential tag ── */
.credential-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600;
    color: #475569; background: #f1f5f9; padding: 6px 14px; border-radius: 8px;
    border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 8px;
}
.credential-tag span { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

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
def get_activity_feed(limit=50):
    try:
        if actions_col is not None:
             # Sort by _id descending to get latest actions (if no timestamp field)
             actions = list(actions_col.find().sort("_id", -1).limit(limit))
             return actions
        return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []

def get_pop_stock():
    try:
        if watchlist_col is not None:
            pipeline = [
                {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1}
            ]
            result = list(watchlist_col.aggregate(pipeline))
            if result:
                return result[0]["_id"], result[0]["count"]
        return "None", 0
    except Exception as e:
        return "None", 0

def get_active_users_count():
    try:
        if actions_col is not None:
            return len(actions_col.distinct("user_id"))
        return 0
    except:
        return 0

def get_broadcast_message():
    try:
        # Using a new collection 'admin_settings' for global config
        settings_col = db["admin_settings"]
        doc = settings_col.find_one({"key": "broadcast_message"})
        if doc and doc.get("active"):
            return doc.get("message", "")
        return ""
    except:
        return ""

def set_broadcast_message(msg, active=True):
    try:
        settings_col = db["admin_settings"]
        settings_col.update_one(
            {"key": "broadcast_message"},
            {"$set": {"message": msg, "active": active}},
            upsert=True
        )
        return True
    except:
        return False



def get_stats():
    try:
        total_users = users_col.count_documents({}) if users_col is not None else 0
        watchlist_entries = watchlist_col.count_documents({}) if watchlist_col is not None else 0
        action_count = actions_col.count_documents({}) if actions_col is not None else 0
        return total_users, watchlist_entries, action_count
    except Exception as e:
        return 0, 0, 0

def get_all_users():
    try:
        if users_col is not None:
             users = list(users_col.find({}, {"_id": 1, "username": 1, "email": 1, "mobile": 1, "password": 1}))
             return users
        return []
    except:
        return []

total_users, watchlist_entries, action_count = get_stats()
all_users = get_all_users()
pop_stock, pop_count = get_pop_stock()
active_users = get_active_users_count()

# =====================================================
# STAT CARDS
# =====================================================
st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card" style="--accent:#f0c040;">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{total_users}</div>
        <div class="stat-label">Total Users</div>
        <div class="stat-sub stat-up">{active_users} active in session</div>
    </div>
    <div class="stat-card" style="--accent:#34c759;">
        <div class="stat-icon">🔥</div>
        <div class="stat-value">{pop_stock}</div>
        <div class="stat-label">Trending Stock</div>
        <div class="stat-sub stat-up">In {pop_count} watchlists</div>
    </div>
    <div class="stat-card" style="--accent:#0a84ff;">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">{action_count}</div>
        <div class="stat-label">User Actions</div>
        <div class="stat-sub" style="color:#4a7090;">Logged interactions</div>
    </div>
    <div class="stat-card" style="--accent:#bf5af2;">
        <div class="stat-icon">⭐</div>
        <div class="stat-value">{watchlist_entries}</div>
        <div class="stat-label">Total Saves</div>
        <div class="stat-sub" style="color:#4a5070;">Across all users</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MAIN TABS
# =====================================================
tab1, tab_activity, tab3, tab4 = st.tabs(["👥  User Management", "📡  Activity Feed", "🔑  Reset Password", "📋  System Info"])

# ─────────────────────────────
# TAB 2: ACTIVITY FEED
# ─────────────────────────────
with tab_activity:
    st.markdown('<div class="section-hdr">Live Activity Log</div>', unsafe_allow_html=True)
    activity = get_activity_feed()
    if activity:
        # Create a formatted list of activities
        for act in activity:
            user_id = str(act.get("user_id", "Unknown"))
            action_type = act.get("action", "unknown").upper()
            val = act.get("value", "—")
            
            # Simple color mapping for actions
            color = "#6366f1" # Default Indigo
            if action_type == "SEARCH": color = "#0a84ff"
            elif action_type == "WATCHLIST": color = "#34c759"
            
            st.markdown(f"""
            <div class="panel-card" style="padding: 1rem 1.5rem; margin-bottom: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="background: {color}; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.5px;">{action_type}</div>
                    <div>
                        <div style="font-family: 'DM Sans', sans-serif; font-size: 0.9rem; font-weight: 700; color: #0f172a;">{val}</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #64748b;">USER: {user_id}</div>
                    </div>
                </div>
                <div style="font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #94a3b8;">Recently</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity recorded yet.")

# ─────────────────────────────
# TAB 1: USER MANAGEMENT
# ─────────────────────────────
with tab1:
    st.markdown('<div class="section-hdr">All Registered Users</div>', unsafe_allow_html=True)

    st.markdown('<div class="filter-row">', unsafe_allow_html=True)
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_q = st.text_input("QUERY", placeholder="Search by name, email, or credential…", key="search_users",
                                  label_visibility="collapsed")
    with col_sort:
        sort_by = st.selectbox("ORDER", ["Username A–Z", "Username Z–A", "Email"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

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

        # Render user grid
        cols_per_row = 3
        rows = [filtered[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]
        
        for row_count, user_batch in enumerate(rows):
            grid_cols = st.columns(cols_per_row)
            for i, user in enumerate(user_batch):
                uid = str(user.get("_id", ""))
                uname = user.get("username", "—")
                uemail = user.get("email", "—")
                umobile = user.get("mobile", "—")
                upass = user.get("password", "—")
                avatar_letter = uname[0].upper() if uname else "?"

                with grid_cols[i]:
                    st.markdown(f"""
                    <div class="user-card">
                        <div class="card-banner">
                            <div class="card-avatar-wrap">
                                <div class="card-avatar">{avatar_letter}</div>
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="card-name">{uname}</div>
                            <div class="card-email">{uemail}</div>
                            <div class="card-meta-grid">
                                <div class="card-meta-item"><span>📱</span> {umobile}</div>
                                <div class="card-meta-item"><span>🔑</span> {upass[:12]}{'…' if len(upass) > 12 else ''}</div>
                            </div>
                            <div class="user-mono">ID: {uid[:20]}…</div>
                        </div>
                        <div class="card-actions">
                            <div class="del-btn-wrapper">
                                <div class="stButton">""" # Marker for styling
                    , unsafe_allow_html=True)
                    
                    if st.button("🗑 DELETE SESSION", key=f"del_grid_{uid}", use_container_width=True):
                        st.session_state[f"confirm_del_{uid}"] = True
                    
                    st.markdown("""</div></div></div>""", unsafe_allow_html=True)

                if st.session_state.get(f"confirm_del_{uid}"):
                    with st.container():
                        st.warning(f"⚠ Delete **{uname}**? (ID: {uid[:8]})")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Confirm", key=f"confirm_yes_{uid}"):
                                users_col.delete_one({"_id": user["_id"]})
                                st.success(f"Deleted {uname}")
                                st.session_state.pop(f"confirm_del_{uid}", None)
                                st.rerun()
                        with c2:
                            if st.button("Cancel", key=f"confirm_no_{uid}"):
                                st.session_state.pop(f"confirm_del_{uid}", None)
                                st.rerun()

        # Downloadable CSV
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        if filtered:
            df = pd.DataFrame([{
                "Username": u.get("username",""),
                "Email": u.get("email",""),
                "Mobile": u.get("mobile",""),
                "ID": str(u.get("_id",""))
            } for u in filtered])
            csv = df.to_csv(index=False)
            _, exp_col = st.columns([4, 1])
            with exp_col:
                st.download_button("⬇ EXPORT DATABASE", csv, "users_export.csv", "text/csv", use_container_width=True)
    else:
        st.info("No users found in the database.")



# ─────────────────────────────
# TAB 3: RESET PASSWORD
# ─────────────────────────────
with tab3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 16px 16px 0 0; padding: 1.8rem 2.2rem; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
        <div style="display:flex; align-items:center; gap:15px;">
            <div style="width:48px; height:48px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">🛡️</div>
            <div>
                <div style="font-family:'DM Serif Display', serif; font-size:1.4rem; color:#ffffff; line-height:1.1;">Account Security</div>
                <div style="font-family:'DM Sans', sans-serif; font-size:0.8rem; color:#94a3b8; margin-top:4px;">Secure administrative control for credential overrides.</div>
            </div>
        </div>
    </div>
    <div class="panel-card" style="border-top:none; border-radius: 0 0 16px 16px; padding-top:2rem;">
    """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns([1, 1.2])
    with col_r1:
        target_user = st.text_input("Username", placeholder="e.g. admin_user", key="rp_user")
    with col_r2:
        cp1, cp2 = st.columns(2)
        with cp1:
            new_pw = st.text_input("New Password", type="password", placeholder="••••••••", key="rp_newpw")
        with cp2:
            confirm_pw = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="rp_confirmpw")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Precise CSS targeting for the Reset Password button
    st.markdown('<div class="reset-btn-marker"></div>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .reset-btn-marker + div .stButton > button {
        background: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 0.6rem 2.5rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    .reset-btn-marker + div .stButton > button:hover {
        background: #334155 !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, btn_center, _ = st.columns([1, 0.6, 1])
    with btn_center:
        if st.button("Reset Password", key="reset_pw_btn", use_container_width=True):
            if not target_user or not new_pw or not confirm_pw:
                st.error("Please fill all fields.")
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
                    st.success(f"Success: Password updated for '{target_user}'.")
                else:
                    st.error(f"Error: User '{target_user}' not found.")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────
# TAB 4: SYSTEM INFO
# ─────────────────────────────
with tab4:
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 2px solid rgba(15, 23, 42, 0.05); padding-bottom:12px;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:#0f172a;">Control Deck</div>
        <div style="font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#64748b; font-weight:700; letter-spacing:1px; text-transform:uppercase;">v2.4.0-build.784</div>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="panel-card" style="border-top: 4px solid #0f172a;">
            <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#64748b;letter-spacing:1.5px;text-transform:uppercase;font-weight:800;margin-bottom:18px;">Application Architecture</div>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">💻</span>ENGINE</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#4338ca;font-weight:600;">Streamlit Core</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">🗄️</span>STORAGE</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#4338ca;font-weight:600;">MongoDB Atlas</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">📡</span>API LINK</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#4338ca;font-weight:600;">Yahoo Finance</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">📊</span>B-MARK</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#4338ca;font-weight:600;">NIFTYBEES.NS</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">🌍</span>LOCALE</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#4338ca;font-weight:600;">IST (UTC+5:30)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown("""
        <div class="panel-card" style="border-top: 4px solid #f0c040;">
            <div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;color:#64748b;letter-spacing:1.5px;text-transform:uppercase;font-weight:800;margin-bottom:18px;">Analytics Engine</div>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">📈</span>CAGR</span>
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#1e293b;font-weight:500;">Compounded Growth</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">🎯</span>SHARPE</span>
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#1e293b;font-weight:500;">Risk-Adjusted Rtn</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">⚖️</span>SORTINO</span>
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#1e293b;font-weight:500;">Downside Dev.</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">📉</span>MAX DD</span>
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#1e293b;font-weight:500;">Peak Impact (%)</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.03);">
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#1e293b;"><span style="margin-right:10px;">🕒</span>WINDOW</span>
                    <span style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#1e293b;font-weight:500;">10YR Rolling Series</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel-card" style="border-top: 4px solid #3b82f6; margin-top: 20px;">
        <div style="font-family:'DM Sans',sans-serif;font-size:0.75rem;color:#64748b;letter-spacing:1.5px;text-transform:uppercase;font-weight:800;margin-bottom:18px;">System Broadcast</div>
        <p style="font-size: 0.8rem; color: #475569; margin-bottom: 1.5rem;">Set a global announcement for all user dashboards.</p>
    </div>
    """, unsafe_allow_html=True)

    current_msg = get_broadcast_message()
    broadcast_text = st.text_area("Broadcast Message", value=current_msg, height=100, placeholder="Enter announcement text...", label_visibility="collapsed")
    
    bc_c1, bc_c2 = st.columns([1, 1])
    with bc_c1:
        if st.button("📢 Update Broadcast", use_container_width=True, key="update_bc"):
            if set_broadcast_message(broadcast_text, active=True):
                st.success("Broadcast updated!")
                import time
                time.sleep(1)
                st.rerun()
    with bc_c2:
        if st.button("❌ Stop Broadcast", use_container_width=True, key="stop_bc"):
            if set_broadcast_message("", active=False):
                st.warning("Broadcast stopped.")
                import time
                time.sleep(1)
                st.rerun()

