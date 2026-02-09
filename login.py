import streamlit as st
import auth_utils
from mongo_db import users_col

st.set_page_config(page_title="Login", layout="centered")

# =====================================================
# 🔁 REDIRECT IF ALREADY LOGGED IN
# =====================================================
if st.session_state.get("is_admin"):
    st.switch_page("pages/admin.py")

if st.session_state.get("authenticated"):
    st.switch_page("pages/dashboard.py")

st.title("🔐 Smart Investor Assistant")

# =====================================================
# SESSION STATE INIT
# =====================================================
if "show_admin_login" not in st.session_state:
    st.session_state.show_admin_login = False

# =====================================================
# ADMIN LOGIN BUTTON
# =====================================================
if not st.session_state.show_admin_login:
    col1, col2, col3 = st.columns([6, 3, 3])
    with col3:
        if st.button("🛠 Admin Login"):
            st.session_state.show_admin_login = True
            st.rerun()

# =====================================================
# USER LOGIN & SIGNUP
# =====================================================
if not st.session_state.show_admin_login:
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    # ---------------- USER LOGIN ----------------
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not username or not password:
                st.error("All fields are required")
            elif auth_utils.login_user(username, password):
                user = users_col.find_one({
                    "username": {"$regex": f"^{username}$", "$options": "i"}
                })

                if not user:
                    st.error("User not found")
                else:
                    # ✅ SESSION STATE (SOURCE OF TRUTH)
                    st.session_state.authenticated = True
                    st.session_state.username = user["username"] # Use DB case
                    st.session_state.user_id = str(user["_id"])

                    # ✅ OPTIONAL (persistence only)
                    st.query_params["user_id"] = st.session_state.user_id
                    st.query_params["username"] = username

                    st.success("Login successful")
                    st.switch_page("pages/dashboard.py")
            else:
                st.error("Invalid username or password")

    # ---------------- USER SIGNUP ----------------
    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("Username")
            new_email = st.text_input("Email ID")
            new_mobile = st.text_input("Mobile Number")
            new_pass = st.text_input("Password (Min 8 chars)", type="password")

            submitted = st.form_submit_button("Create Account")

            if submitted:
                if not all([new_user, new_email, new_mobile, new_pass]):
                    st.error("All fields are required!")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif len(new_mobile) < 10:
                    st.error("Please enter a valid mobile number.")
                elif auth_utils.signup_user(new_user, new_pass, new_email, new_mobile):
                    st.success("Account created! Please login.")
                    st.balloons()
                else:
                    st.error("Username already exists.")

# =====================================================
# ADMIN LOGIN
# =====================================================
if st.session_state.show_admin_login:
    st.subheader("🛠 Admin Login")

    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")

    if st.button("Login as Admin"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.session_state.is_admin = True
            st.session_state.authenticated = False
            st.session_state.show_admin_login = False

            st.success("Admin login successful")
            st.switch_page("pages/admin.py")
        else:
            st.error("Invalid admin credentials")

    if st.button("⬅ Back"):
        st.session_state.show_admin_login = False
        st.rerun()
