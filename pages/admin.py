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

st.title("🛠 Admin Dashboard")
st.markdown("Monitor user engagement, manage registered accounts, and track platform activity.")
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
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Password": st.column_config.TextColumn(
                    "Password",
                    help="Passwords starting with $2b$ are securely encrypted (hashed) and cannot be decrypted.",
                    width="medium"
                )
            }
        )
    else:
        st.info("No registered users found in the database.")

with tab2:
    st.subheader("User Watchlist Preferences")
    if watchlist_data:
        df_watch = pd.DataFrame(watchlist_data)
        st.dataframe(df_watch, use_container_width=True, hide_index=True)
    else:
        st.info("No watchlist data has been saved by any users yet.")

with tab3:
    st.subheader("Recent User Interactions")
    if activity_data:
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
    else:
        st.info("No user activity logs have been recorded yet.")