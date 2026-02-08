from pymongo import MongoClient
import os
import streamlit as st
import certifi

# Try to read MongoDB URI from environment or Streamlit secrets
MONGO_URI = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI", None)

# -------------------------------------------------
# SAFE MODE: MongoDB is OPTIONAL
# -------------------------------------------------
if not MONGO_URI:
    # Demo / No-DB mode
    client = None
    db = None
    users_col = None
    actions_col = None
    watchlist_col = None

else:
    # Production / DB mode
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["stock_market_app"]

    users_col = db["users"]
    actions_col = db["user_actions"]
    watchlist_col = db["watchlist"]