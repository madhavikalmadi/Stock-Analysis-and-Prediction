import streamlit as st
from db import execute  # Imports your database connection logic
from sqlalchemy.exc import SQLAlchemyError

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admin Panel", layout="centered")
# from login import login (Removed)

# if not login(): (Removed)
#     st.stop()

# --- SESSION STATE ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# --- NEO-BRUTALIST CSS ---
st.markdown("""
<style>
/* Global background */
[data-testid="stAppViewContainer"] {
    background-color: #f2f2f2 !important;
}

/* Hide default Streamlit UI */
#MainMenu, footer, header { visibility: hidden; }

/* Main Admin Card */
.admin-card {
    width: 720px;
    background: white;
    border: 3px solid black;
    box-shadow: 10px 10px 0 black;
    padding: 40px;
    margin: 80px auto 40px auto;
}

/* Typography */
h1 {
    text-align: center;
    letter-spacing: 2px;
    font-weight: 800;
    margin-bottom: 4px;
    text-transform: uppercase;
}

.sub {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    color: #666;
    margin-bottom: 25px;
    text-transform: uppercase;
}

/* Form Elements */
.stTextInput label {
    font-weight: 700 !important;
    text-transform: uppercase;
}

.stTextInput input {
    background: #f5f5f5 !important;
    border: 2px solid black !important;
    border-radius: 0 !important;
}

/* Buttons */
div.stButton > button {
    width: 100%;
    background: black !important;
    color: white !important;
    border: 2px solid black !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 25px !important;
}

div.stButton > button:hover {
    background: #FFDE59 !important;
    color: black !important;
    box-shadow: 4px 4px 0 black;
}

/* Table styling */
table {
    width: 100% !important;
    border-collapse: collapse !important;
}

thead th {
    background: black;
    color: white;
    padding: 8px;
    border: 2px solid black;
}

tbody td {
    padding: 8px;
    border: 2px solid black;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- CARD WRAPPER START ---
st.markdown('<div class="admin-card">', unsafe_allow_html=True)

# --- LOGIC FLOW ---

if not st.session_state.admin_logged_in:
    # -------------------------
    # ADMIN LOGIN SCREEN
    # -------------------------
    st.markdown("<h1>ADMIN</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>SYSTEM CONTROL PANEL</div>", unsafe_allow_html=True)

    user = st.text_input("ADMIN USER", placeholder="Username")
    password = st.text_input("ADMIN PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("LOGIN"):
        if user == "madhuuu" and password == "1203":
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid Admin Credentials")

    if st.button("← BACK TO LOGIN"):
        st.switch_page("login.py")

else:
    # -------------------------
    # ADMIN DASHBOARD CONTENT
    # -------------------------
    st.markdown("<h1>DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>REGISTERED USER DETAILS</div>", unsafe_allow_html=True)

    try:
        users = execute("SELECT id, name, email FROM users ORDER BY id DESC", fetchall=True)

        if users:
            st.write("### User List")
            st.table(users)
        else:
            st.info("The database is currently empty.")

    except Exception as e:
        st.error(f"Error connecting to Database: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("LOGOUT"):
        st.session_state.admin_logged_in = False
        st.rerun()

# --- CARD WRAPPER END ---
st.markdown('</div>', unsafe_allow_html=True)
