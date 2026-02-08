from pymongo import MongoClient
import os
import streamlit as st
import certifi

def get_db():
    MONGO_URI = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI")

    if not MONGO_URI:
        raise Exception("❌ MONGO_URI not found")

    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    return client["stock_market_app"]

db = get_db()

users_col = db["users"]
actions_col = db["user_actions"]
watchlist_col = db["watchlist"]
