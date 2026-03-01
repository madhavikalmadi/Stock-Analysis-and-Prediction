import streamlit as st
import pandas as pd

from mongo_db import users_col, watchlist_col, actions_col

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Admin Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# NAVIGATION
# =====================================================
col_main, col_nav = st.columns([8, 2])
with col_nav:
    if st.button("⬅ Back to Login", use_container_width=True):
        st.session_state.clear()
        st.switch_page("login.py")

# =====================================================
# CUSTOM PROFESSIONAL UI
# =====================================================
st.markdown("""
<style>
    .admin-title {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: 1px;
    }

    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 22px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: all 0.25s ease-in-out;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.55);
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        color: #eaf2ff !important;
    }

    div[data-testid="metric-container"] label {
        font-weight: 600;
        color: #9aa7c7;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown('<h1 class="admin-title">🛠 Admin Dashboard</h1>', unsafe_allow_html=True)
st.caption("Central control panel to monitor users, watchlists, and activity logs.")
st.divider()

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def safe_password_display(pwd):
    """Safely format stored password (hashed / legacy formats)."""
    if isinstance(pwd, (list, tuple)):
        try:
            return "".join(chr(int(i)) for i in pwd)
        except:
            return "Encrypted"
    if isinstance(pwd, bytes):
        return pwd.decode("utf-8", errors="ignore")
    return str(pwd)

# =====================================================
# DATA FETCHING
# =====================================================
users = list(users_col.find({}, {"username": 1, "email": 1, "mobile": 1, "password": 1}))

watchlist_data = list(watchlist_col.aggregate([
    {"$addFields": {"user_obj_id": {"$toObjectId": "$user_id"}}},
    {"$lookup": {
        "from": "users",
        "localField": "user_obj_id",
        "foreignField": "_id",
        "as": "user"
    }},
    {"$unwind": "$user"},
    {"$project": {"_id": 0, "username": "$user.username", "ticker": 1}}
]))

activity_data = list(actions_col.aggregate([
    {"$addFields": {"user_obj_id": {"$toObjectId": "$user_id"}}},
    {"$lookup": {
        "from": "users",
        "localField": "user_obj_id",
        "foreignField": "_id",
        "as": "user"
    }},
    {"$unwind": "$user"},
    {"$project": {"_id": 0, "username": "$user.username", "action": 1, "value": 1}}
]))

# =====================================================
# KEY METRICS
# =====================================================
m1, m2, m3 = st.columns(3)
m1.metric("👥 Total Users", len(users))
m2.metric("⭐ Watchlist Entries", len(watchlist_data))
m3.metric("📈 Activity Logs", len(activity_data))

st.write("")

# =====================================================
# MAIN TABS
# =====================================================
tab_users, tab_watchlist, tab_activity = st.tabs([
    "👥 Users",
    "⭐ Watchlists",
    "📈 Activity Logs"
])

# =====================================================
# USERS TAB
# =====================================================
with tab_users:
    st.subheader("Registered Users")

    if not users:
        st.info("No users registered yet.")
    else:
        search = st.text_input("🔍 Search by Username or Email").lower()

        df_users = pd.DataFrame([
            {
                "User ID": str(u["_id"]),
                "Username": u["username"],
                "Email": u.get("email", "N/A"),
                "Mobile": u.get("mobile", "N/A"),
                "Password": safe_password_display(u.get("password"))
            }
            for u in users
        ])

        if search:
            df_users = df_users[
                df_users["Username"].str.lower().str.contains(search) |
                df_users["Email"].str.lower().str.contains(search)
            ]

        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Password": st.column_config.TextColumn(
                    help="Passwords are stored securely (hashed)."
                )
            }
        )

# =====================================================
# WATCHLIST TAB
# =====================================================
with tab_watchlist:
    st.subheader("User Watchlists")

    if not watchlist_data:
        st.info("No watchlist entries found.")
    else:
        col1, col2 = st.columns(2)
        ticker = col1.text_input("🔍 Filter by Ticker").upper()
        user = col2.text_input("👤 Filter by Username").lower()

        df_watch = pd.DataFrame(watchlist_data)

        if ticker:
            df_watch = df_watch[df_watch["ticker"].str.contains(ticker)]
        if user:
            df_watch = df_watch[df_watch["username"].str.lower().str.contains(user)]

        st.dataframe(df_watch, use_container_width=True, hide_index=True)

# =====================================================
# ACTIVITY TAB
# =====================================================
with tab_activity:
    st.subheader("User Activity Logs")

    if not activity_data:
        st.info("No activity logs recorded.")
    else:
        search_user = st.text_input("👤 Search by Username").lower()
        df_activity = pd.DataFrame(activity_data)

        if search_user:
            df_activity = df_activity[
                df_activity["username"].str.lower().str.contains(search_user)
            ]

        def style_action(val):
            colors = {
                "Login": "#00e676",
                "Logout": "#ff5252"
            }
            for key, color in colors.items():
                if key in str(val):
                    return f"color:{color}; font-weight:700;"
            return ""

        st.dataframe(
            df_activity.style.applymap(style_action, subset=["action"]),
            use_container_width=True,
            hide_index=True
        )