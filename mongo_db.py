from pymongo import MongoClient
import os
import streamlit as st
import certifi

def get_db():
    try:
        # Try environment variable first (best for Cloud/containers)
        MONGO_URI = os.getenv("MONGO_URI")
        
        # Fallback to Streamlit secrets
        if not MONGO_URI:
            try:
                if hasattr(st, "secrets") and "MONGO_URI" in st.secrets:
                    MONGO_URI = st.secrets["MONGO_URI"]
            except Exception as e:
                # Silently fail here, we check for MONGO_URI below
                pass

        if not MONGO_URI:
            st.error("🔒 MONGO_URI secret is missing. Please add it to your Streamlit Cloud secrets.")
            st.stop()

        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        return client["stock_market_app"]
    except Exception as e:
        st.error(f"❌ Database Connection Error: {str(e)}")
        st.stop()

db = get_db()
users_col = db["users"]
actions_col = db["user_actions"]
watchlist_col = db["watchlist"]
