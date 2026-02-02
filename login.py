import streamlit as st
import pandas as pd
import re
import os
import auth_utils  # Import the new auth utility

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Pro Auth", layout="centered")

# AUTO-REDIRECT IF ALREADY LOGGED IN
if auth_utils.check_auth():
    st.switch_page("pages/dashboard.py")

# -------------------------------------------------
# DATA & VALIDATION LOGIC
# -------------------------------------------------
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.csv")

def load_users():
    """Load users from CSV. Returns an empty DataFrame if file doesn't exist."""
    if not os.path.exists(USERS_FILE):
        return pd.DataFrame(columns=["Name", "Password", "Email", "Mobile"])
    try:
        return pd.read_csv(USERS_FILE, dtype=str)
    except Exception:
        return pd.DataFrame(columns=["Name", "Password", "Email", "Mobile"])

def save_user(name, email, password, mobile):
    """Append a new user to the CSV file."""
    df = load_users()
    # Normalize data: lowercase email, strip whitespace
    new_user = pd.DataFrame([{
        "Name": name.strip(), 
        "Password": password.strip(), 
        "Email": email.strip().lower(), 
        "Mobile": mobile.strip()
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

def validate_email(email):
    """Check if email matches a standard pattern."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    """Check if mobile is exactly 10 digits."""
    return mobile.isdigit() and len(mobile) == 10

def validate_password(password):
    """Check if password is at least 8 characters long."""
    return len(password) >= 8

def check_login(email, password):
    """Verify credentials against the CSV."""
    df = load_users()
    if df.empty:
        return False
    
    email = email.strip().lower()
    password = password.strip()
    
    # Filter for user 
    user = df[(df["Email"].str.lower() == email) & (df["Password"] == password)]
    return not user.empty

def check_email_exists(email):
    """Check if email is already registered."""
    df = load_users()
    if df.empty:
        return False
    return email.strip().lower() in df["Email"].str.lower().values

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "signup"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------------------------
# CSS (Neobrutalism Style)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');

html, body { height: 100%; }

[data-testid="stAppViewContainer"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #F0F2F5 !important;
}

#MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }

.block-container {
    width: 440px !important;
    background: white;
    border: 3px solid black;
    box-shadow: 10px 10px 0 black;
    padding: 40px !important;
    margin: auto !important;
}

.auth-header { text-align: center; margin-bottom: 25px; }

.auth-header h1 {
    font-weight: 800;
    font-size: 38px;
    text-transform: uppercase;
}

.auth-header p {
    font-size: 16px;
    color: #666;
    margin: 0;
    font-weight: 500;
}

.stTextInput > div > div > input {
    border: 2px solid black !important;
    border-radius: 0 !important;
}

div.stButton > button {
    width: 100%;
    background: black !important;
    color: white !important;
    border: 2px solid black !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

div.stButton > button:hover {
    background: #FFDE59 !important;
    color: black !important;
    box-shadow: 4px 4px 0 black;
}

/* Admin button */
.admin-btn {
    position: fixed;
    top: 18px;
    right: 18px;
    z-index: 9999;
}

.admin-btn button {
    background: white;
    border: 3px solid black;
    padding: 8px 18px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    box-shadow: 4px 4px 0 black;
    cursor: pointer;
}

.admin-btn button:hover {
    background: #FFDE59;
    box-shadow: 6px 6px 0 black;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# ADMIN BUTTON
# -------------------------------------------------
st.markdown("""
<div class="admin-btn">
    <a href="?go_admin=1" target="_self">
        <button type="button">ADMIN</button>
    </a>
</div>
""", unsafe_allow_html=True)

if st.query_params.get("go_admin") == "1":
    st.switch_page("pages/admin.py")

# -------------------------------------------------
# UI LOGIC
# -------------------------------------------------
if st.session_state.page == "signup":
    st.markdown('<div class="auth-header"><h1>JOIN US</h1><p>ENTER PRECISE DETAILS</p></div>', unsafe_allow_html=True)

    name = st.text_input("NAME", placeholder="John Doe")
    email = st.text_input("EMAIL", placeholder="hello@example.com", help="Check for correct format: name@domain.com")
    mobile = st.text_input("MOBILE", placeholder="9876543210", max_chars=10, help="Enter exactly 10 digits")
    password = st.text_input("PASSWORD", type="password", placeholder="••••••••", help="Must be at least 8 characters")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("CREATE ACCOUNT"):
        # Validation checks
        error_msg = ""
        if not name or not email or not mobile or not password:
            error_msg = "Please fill in all fields."
        elif not validate_email(email):
            error_msg = "Invalid Email Address format."
        elif not validate_mobile(mobile):
            error_msg = "Mobile Number must be exactly 10 digits."
        elif not validate_password(password):
            error_msg = "Password must be at least 8 characters long."
        elif check_email_exists(email):
            error_msg = "An account with this email already exists."

        if error_msg:
            st.error(error_msg)
        else:
            save_user(name, email, password, mobile)
            auth_utils.login_user(email) # Use auth_utils
            st.success("Account created successfully!")
            with st.spinner("Redirecting..."):
                st.switch_page("pages/dashboard.py")

    if st.button("ALREADY HAVE AN ACCOUNT? LOGIN"):
        st.session_state.page = "login"
        st.rerun()

else:
    st.markdown('<div class="auth-header"><h1>LOGIN</h1><p>WELCOME BACK, EXPLORER</p></div>', unsafe_allow_html=True)

    login_email = st.text_input("EMAIL", placeholder="hello@example.com")
    login_password = st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("SIGN IN"):
        # Validation checks for login
        if not login_email or not login_password:
             st.error("Please enter both email and password.")
        elif check_login(login_email, login_password):
            auth_utils.login_user(login_email) # Use auth_utils
            st.success("Login Successful!")
            with st.spinner("Redirecting..."):
                st.switch_page("pages/dashboard.py")
        else:
            st.error("Invalid Email or Password.")

    if st.button("NEW HERE? CREATE ACCOUNT"):
        st.session_state.page = "signup"
        st.rerun()
