from pymongo import MongoClient
import os
import streamlit as st

MONGO_URI = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not found in environment or Streamlit secrets")

import certifi

# Fix for SSL Handshake Error
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

db = client["stock_market_app"]

users_col = db["users"]
actions_col = db["user_actions"]
watchlist_col = db["watchlist"]