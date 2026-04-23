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

# =====================================================
# NEW UI DESIGN
# =====================================================
st.markdown("""
    <style>
    .login-box {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        background-color: white;
    }
    /* Set page background to something nicer to make the white box pop */
    [data-testid="stAppViewContainer"] {
        background-color: #f7f9fc;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.title("🔐 Smart Investor Login")

email_or_username = st.text_input("Email or Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email_or_username or not password:
        st.error("All fields are required")
    elif auth_utils.login_user(email_or_username, password):
        # Fetch user details to populate session state
        user = users_col.find_one({
            "$or": [
                {"username": {"$regex": f"^{email_or_username}$", "$options": "i"}},
                {"email": {"$regex": f"^{email_or_username}$", "$options": "i"}}
            ]
        })

        if user:
            # ✅ SESSION STATE (SOURCE OF TRUTH)
            st.session_state.authenticated = True
            st.session_state.username = user["username"]
            st.session_state.user_id = str(user["_id"])
            
            # Additional user object for consistency with user's provided snippet
            st.session_state["user"] = user

            # ✅ Navigation Persistence
            st.query_params["user_id"] = st.session_state.user_id
            st.query_params["username"] = user["username"]

            st.success("Login successful!")
            st.switch_page("pages/dashboard.py")
        else:
            st.error("User details not found")
    else:
        st.error("Invalid email or password")

st.markdown('</div>', unsafe_allow_html=True)

# Add a small link or button for Admin Login if needed, 
# but sticking to the user's focus on a "replace"
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🛠 Admin Login", type="secondary"):
        st.session_state.show_admin_login = True
        # In this simplified version, we'll just show the admin fields below or redirect
        # For now, let's just add the old admin login logic back as a small section 
        # to ensure they don't lose access.
        pass

if st.session_state.get("show_admin_login"):
    st.markdown("---")
    st.subheader("🛠 Admin Login")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if admin_user == "admin" and admin_pass == "aprilfool1203":
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
