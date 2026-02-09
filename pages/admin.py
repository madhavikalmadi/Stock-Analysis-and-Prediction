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

# =====================================================
# REGISTERED USERS
# =====================================================
st.subheader("👤 Registered Users")

users = list(users_col.find({}, {"username": 1, "email": 1, "mobile": 1, "password": 1}))

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
        column_config={
            "Password": st.column_config.TextColumn(
                "Password",
                help="Passwords starting with $2b$ are securely encrypted (hashed) and cannot be decrypted.",
                width="medium"
            )
        }
    )
else:
    st.info("No users found")

st.divider()

# =====================================================
# WATCHLIST (USER → STOCK)
# =====================================================
st.subheader("⭐ Watchlist (User → Stock)")

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

if watchlist_data:
    st.dataframe(pd.DataFrame(watchlist_data), use_container_width=True)
else:
    st.info("No watchlist data found.")

st.divider()

# =====================================================
# USER ACTIVITY
# =====================================================
st.subheader("🔍 User Activity")

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

if activity_data:
    st.dataframe(pd.DataFrame(activity_data), use_container_width=True)
else:
    st.info("No user activity found.")