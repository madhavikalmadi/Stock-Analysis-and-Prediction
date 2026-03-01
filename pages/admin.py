import streamlit as st
import pandas as pd
from bson import ObjectId

from mongo_db import users_col, watchlist_col, actions_col

st.set_page_config(page_title="Admin Dashboard", layout="wide")
# =====================================================
# BACK TO LOGIN BUTTON
# =====================================================
col1, col2 = st.columns([8, 2])

with col2:
    if st.button("⬅ Back to Login"):
        st.session_state.clear()
        st.switch_page("login.py")

# Admin auth check removed by user request
# if not st.session_state.get("is_admin"):
#     st.error("Admin access only")
#     st.stop()

# =====================================================
# CUSTOM CSS FOR STUNNING UI
# =====================================================
st.markdown("""
<style>
    /* Sleek gradient background for the main title */
    .admin-title {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    /* Premium Metric Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Make metric labels bolder and lighter */
    div[data-testid="metric-container"] > div {
        font-weight: 600 !important;
        color: #8892b0 !important;
    }
    
    /* Make metric values pop */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #e6f1ff !important;
        font-size: 2.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="admin-title">🛠 Admin Dashboard</h1>', unsafe_allow_html=True)
st.markdown("Monitor user engagement, manage registered accounts, and track platform activity in real-time.")
st.divider()

# =====================================================
# DATA FETCHING
# =====================================================
users = list(users_col.find({}, {"username": 1, "email": 1, "mobile": 1, "password": 1}))

watchlist_pipeline = [
    {
        "$addFields": {
            "user_obj_id": { "$toObjectId": "$user_id" }
        }
    },
    {
        "$lookup": {
            "from": "users",
            "localField": "user_obj_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    { "$unwind": "$user" },
    {
        "$project": {
            "_id": 0,
            "username": "$user.username",
            "ticker": 1
        }
    }
]
watchlist_data = list(watchlist_col.aggregate(watchlist_pipeline))

activity_pipeline = [
    {
        "$addFields": {
            "user_obj_id": { "$toObjectId": "$user_id" }
        }
    },
    {
        "$lookup": {
            "from": "users",
            "localField": "user_obj_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    { "$unwind": "$user" },
    {
        "$project": {
            "_id": 0,
            "username": "$user.username",
            "action": 1,
            "value": 1
        }
    }
]
activity_data = list(actions_col.aggregate(activity_pipeline))

# =====================================================
# KEY METRICS
# =====================================================
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="👥 Total Registered Users", value=len(users))
with col_m2:
    st.metric(label="⭐ Total Watchlist Items", value=len(watchlist_data))
with col_m3:
    st.metric(label="📈 Total Activities Logged", value=len(activity_data))

st.write("") # Spacer
st.write("") # Spacer

# =====================================================
# TABS FOR DATA
# =====================================================
tab1, tab2, tab3 = st.tabs(["👥 Registered Users", "⭐ Watchlists", "📈 User Activity"])

with tab1:
    st.subheader("Registered Users Directory")
    
    def format_password(pwd):
        if isinstance(pwd, (list, tuple)):
            try:
                return "".join(chr(int(i)) for i in pwd)
            except:
                return str(pwd)
        if isinstance(pwd, bytes):
            return pwd.decode('utf-8', errors='ignore')
        return str(pwd)

    if users:
        # Search Filter
        search_user = st.text_input("🔍 Search Users (by Username or Email)", key="search_user").lower()
        
        df_users = pd.DataFrame([
            {
                "User ID": str(u["_id"]), 
                "Username": u["username"],
                "Email": u.get("email", "N/A"),
                "Mobile": u.get("mobile", "N/A"),
                "Password": format_password(u.get("password", "****"))
            }
            for u in users
        ])
        
        # Apply filter
        if search_user:
            df_users = df_users[
                df_users["Username"].str.lower().str.contains(search_user) | 
                df_users["Email"].str.lower().str.contains(search_user)
            ]
            
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Password": st.column_config.TextColumn(
                    "Password",
                    help="Passwords starting with $2b$ are securely encrypted (hashed) and cannot be decrypted.",
                    width="medium"
                ),
                "Email": st.column_config.TextColumn("Email", width="medium"),
            }
        )
    else:
        st.info("No registered users found in the database.")

with tab2:
    st.subheader("User Watchlist Preferences")
    if watchlist_data:
        # Search Filter
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            search_ticker = st.text_input("🔍 Filter by Ticker", key="search_ticker").upper()
        with col_w2:
            search_watch_user = st.text_input("👤 Filter by Username", key="search_w_user").lower()
            
        df_watch = pd.DataFrame(watchlist_data)
        
        # Apply filters
        if search_ticker:
            df_watch = df_watch[df_watch["ticker"].str.contains(search_ticker)]
        if search_watch_user:
            df_watch = df_watch[df_watch["username"].str.lower().str.contains(search_watch_user)]
            
        st.dataframe(df_watch, use_container_width=True, hide_index=True)
    else:
        st.info("No watchlist data has been saved by any users yet.")

with tab3:
    st.subheader("Recent User Interactions")
    if activity_data:
        df_activity = pd.DataFrame(activity_data)
        
        # Search Tool
        search_act_user = st.text_input("👤 Search by Username", key="search_act_user").lower()
            
        # Apply filters
        if search_act_user:
            df_activity = df_activity[df_activity["username"].str.lower().str.contains(search_act_user)]
            
        # Styling Function for Activity Table
        def highlight_actions(val):
            color = ''
            if val == 'Login': color = 'color: #00e676; font-weight: bold;'
            elif val == 'Logout': color = 'color: #ff5252; font-weight: bold;'
            elif 'View' in str(val): color = 'color: #40c4ff;'
            elif 'Predict' in str(val): color = 'color: #e040fb; font-weight: bold;'
            elif 'Watchlist' in str(val): color = 'color: #ffd740;'
            return color

        # Apply styling and show
        styled_df = df_activity.style.applymap(highlight_actions, subset=['action'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No user activity logs have been recorded yet.")