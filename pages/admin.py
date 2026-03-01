import streamlit as st
import pandas as pd
from bson import ObjectId

from mongo_db import users_col, watchlist_col, actions_col

st.set_page_config(page_title="Admin Dashboard", layout="wide")
# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
with st.sidebar:
    st.markdown("### Administrator Panel")
    st.markdown("Manage users, monitor platform activity, and track key engagement metrics.")
    st.divider()
    if st.button("Logout to Login Page", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.switch_page("login.py")

# =====================================================
# CUSTOM CSS FOR PROFESSIONAL UI
# =====================================================
st.markdown("""
<style>
    /* Clean, professional title */
    .admin-title {
        color: #1f2937;
        font-weight: 700;
        margin-bottom: 0px;
        font-size: 2.2rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 10px;
    }
    
    /* Subtle Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-color: #d1d5db;
    }
    
    /* Professional metric labels */
    div[data-testid="metric-container"] > div {
        font-weight: 500 !important;
        color: #6b7280 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Clean metric values */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #111827 !important;
        font-size: 2.2rem !important;
        margin-top: 5px;
    }
    
    /* Make the app background slightly gray for contrast */
    .stApp {
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="admin-title">System Overview</h1>', unsafe_allow_html=True)
st.write("") # Spacer

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
    st.metric(label="Total Registered Users", value=len(users))
with col_m2:
    st.metric(label="Total Watchlist Items", value=len(watchlist_data))
with col_m3:
    st.metric(label="Total Activities Logged", value=len(activity_data))

st.write("") # Spacer
st.write("") # Spacer

# =====================================================
# TABS FOR DATA
# =====================================================
tab1, tab2, tab3 = st.tabs(["Overview & Charts", "User Directory", "System Logs"])

with tab1:
    st.subheader("Platform Analytics")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**Top Watchlisted Stocks**")
        if watchlist_data:
            df_watch = pd.DataFrame(watchlist_data)
            top_stocks = df_watch['ticker'].value_counts().head(5)
            st.bar_chart(top_stocks, color="#3b82f6")
        else:
            st.info("Insufficient data for Watchlist chart.")
            
    with col_chart2:
        st.markdown("**User Activity Breakdown**")
        if activity_data:
            df_activity = pd.DataFrame(activity_data)
            action_counts = df_activity['action'].value_counts()
            st.bar_chart(action_counts, color="#10b981")
        else:
            st.info("Insufficient data for Activity chart.")

with tab2:
    st.subheader("Registered User Directory")
    
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
        search_user = st.text_input("Search Users (by Username or Email)", key="search_user").lower()
        
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

with tab3:
    st.subheader("Comprehensive System Logs")
    
    # Watchlist Data combined or side-by-side
    col_log1, col_log2 = st.columns(2)
    
    with col_log1:
        st.markdown("**Watchlist Registrations**")
        if watchlist_data:
            df_watch = pd.DataFrame(watchlist_data)
            search_ticker = st.text_input("Filter by Ticker", key="search_ticker").upper()
            if search_ticker:
                df_watch = df_watch[df_watch["ticker"].str.contains(search_ticker)]
            st.dataframe(df_watch, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("No watchlist records.")
            
    with col_log2:
        st.markdown("**User Action Logs**")
        if activity_data:
            df_activity = pd.DataFrame(activity_data)
            search_act_user = st.text_input("Filter by Username", key="search_act_user").lower()
            if search_act_user:
                df_activity = df_activity[df_activity["username"].str.lower().str.contains(search_act_user)]
                
            # Subtle styling instead of rainbow colors
            def highlight_actions(val):
                color = ''
                if val == 'Login': color = 'color: #059669; font-weight: 500;' # subdued green
                elif val == 'Logout': color = 'color: #dc2626; font-weight: 500;' # subdued red
                elif 'View' in str(val): color = 'color: #2563eb;' # subdued blue
                return color

            styled_df = df_activity.style.applymap(highlight_actions, subset=['action'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("No activity records.")