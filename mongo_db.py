from pymongo import MongoClient
import os
import streamlit as st
import certifi

MONGO_URI = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI", None)

client = None
db = None
users_col = None
actions_col = None
watchlist_col = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client["stock_market_app"]
        users_col = db["users"]
        actions_col = db["user_actions"]
        watchlist_col = db["watchlist"]
    except Exception as e:
        st.error("Database connection failed")
