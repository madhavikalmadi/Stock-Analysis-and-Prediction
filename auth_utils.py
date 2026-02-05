import streamlit as st
from mongo_db import users_col

def check_auth():
    return st.session_state.get("authenticated", False)

def login_user(username, password):
    # Case-insensitive search
    user = users_col.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})

    if user and user["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user_id = str(user["_id"])   # ✅ THIS IS THE FIX
        st.session_state.username = user["username"]  # optional but useful
        return True

    return False

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_welcome_email(user_email, username):
    """Sends a welcome email to the new user."""
    # Try to get secrets, gracefully fade if not set
    try:
        smtp_server = st.secrets["smtp"]["server"]
        smtp_port = st.secrets["smtp"]["port"]
        sender_email = st.secrets["smtp"]["email"]
        sender_password = st.secrets["smtp"]["password"]
    except Exception:
        print("⚠️ SMTP Secrets not found. Mocking email send.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "Welcome to Smart Investor Assistant! 🚀"

        body = f"""
        Hi {username},

        Welcome to Smart Investor Assistant! 
        
        Your account has been successfully created. We are excited to have you on board.
        Start exploring the dashboard and manage your portfolio like a pro.

        Best Regards,
        The Smart Investor Team
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✅ Welcome email sent to {user_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def signup_user(username, password, email, mobile):
    # Check if user exists (case-insensitive)
    if users_col.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}}):
        return False

    users_col.insert_one({
        "username": username, # Store as entered (preserves preference)
        "password": password,
        "email": email,
        "mobile": mobile
    })
    
    # Send Welcome Email (Non-blocking ideally, but simple here)
    send_welcome_email(email, username)
    return True

def logout_user():
    st.session_state.clear()