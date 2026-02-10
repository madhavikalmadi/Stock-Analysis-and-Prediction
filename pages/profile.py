import streamlit as st
from mongo_db import watchlist_col
from bson import ObjectId
from theme_manager import get_theme # Keeping get_theme but unused or just remove imports entirely if careful
# Removing apply_theme and render_theme_toggle logic entirely

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="My Profile",
    page_icon="👤",
    layout="wide"
)

# =====================================================
# 🔁 RESTORE SESSION FROM URL (VERY IMPORTANT)
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

# --------------------------------------------------
# CSS STYLING
# --------------------------------------------------
# Static Light Mode Colors
card_bg = "rgba(255,255,255,0.75)"
card_text = "#1e293b"
sub_text = "rgba(0,0,0,0.6)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

body, [data-testid="stAppViewContainer"] {{
    font-family: 'Outfit', sans-serif;
}}
/* ... (CSS continues) ... */


/* ---------- LEFT PROFILE BOX ---------- */
/* ---------- LEFT PROFILE BOX (TARGETING COLUMN 1) ---------- */
/* ---------- LEFT PROFILE BOX (TARGETING CONTAINER) ---------- */
[data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"] {{
    background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.05)) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    backdrop-filter: blur(14px) !important;
}}
/* Center content inside the container */
[data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"] > div {{
    align-items: center;
    text-align: center;
    gap: 1rem;
}}

.profile-avatar {{
    font-size: 4rem;
    background: linear-gradient(135deg, #3b82f6, #9333ea);
    color: white;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}}

.profile-name {{
    font-size: 1.5rem;
    font-weight: 800;
}}

.profile-sub {{
    opacity: 0.75;
    margin-bottom: 1.2rem;
}}

/* ---------- RIGHT SIDE ---------- */
.section-title {{
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
}}

.watchlist-card {{
    background: {card_bg};
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 1.6rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    text-align: center;
    margin-bottom: 20px;
    color: {card_text};
}}

.watchlist-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 18px 45px rgba(59,130,246,0.25);
}}

.stock-ticker {{
    font-size: 1.5rem;
    font-weight: 800;
}}

.stock-sub {{
    font-size: 0.85rem;
    opacity: 0.7;
    color: {sub_text} !important;
}}

.empty-box {{
    text-align: center;
    padding: 3rem;
    border-radius: 22px;
    background: {card_bg};
    box-shadow: 0 8px 25px rgba(0,0,0,0.06);
    color: {card_text};
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FETCH WATCHLIST
# --------------------------------------------------
# --------------------------------------------------
# FETCH WATCHLIST
# --------------------------------------------------
import pymongo
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

watchlist = []
if user_id:
    try:
        watchlist = list(watchlist_col.find({"user_id": user_id}))
    except pymongo.errors.ServerSelectionTimeoutError:
        st.error("⚠️ Connection Error: Unable to connect to the database. Please check your internet connection or try again later.")
        watchlist = [] # Fallback to empty
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")
        watchlist = []

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
c_sidebar, c_content = st.columns([1.1, 3])

# ---------- LEFT COLUMN ----------
with c_sidebar:
    # Use native container for robust boxing
    with st.container(border=True):
        st.markdown('<div class="profile-avatar">👤</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-name">{username or "User"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="profile-sub">Smart Investor Assistant</div>', unsafe_allow_html=True)

        # JOIN DATE
        join_date = "Unknown"
        try:
            join_date = ObjectId(user_id).generation_time.strftime("%b %Y")
        except:
            pass

        st.markdown(f"<p style='opacity:0.75;'>📅 Member since: <b>{join_date}</b></p>", unsafe_allow_html=True)

        st.divider()

        # THEME TOGGLE REMOVED

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.query_params.clear()
            st.switch_page("login.py")

# ---------- RIGHT COLUMN ----------
with c_content:
    st.markdown("<div class='section-title'>⭐ My Watchlist</div>", unsafe_allow_html=True)

    if not watchlist:
        st.markdown("""
        <div class="empty-box">
            <h3>📭 No watchlist items</h3>
            <p>Add stocks to see them here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for idx, item in enumerate(watchlist):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="watchlist-card">
                    <div class="stock-ticker">{item['ticker']}</div>
                    <div class="stock-sub">Saved Stock</div>
                </div>
                """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER & NAVIGATION
# --------------------------------------------------
st.markdown("""
<style>
div.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}
div.stButton > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;
    background: rgba(24, 40, 72, 0.8) !important;
    color: white !important;
    border: none !important;
}
div.stButton > button * {
    color: white !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

if st.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

st.write("---")
st.markdown("<center style='opacity:0.6;'>Smart Investor Assistant</center>", unsafe_allow_html=True)