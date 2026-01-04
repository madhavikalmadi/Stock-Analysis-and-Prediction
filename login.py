import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Pro Auth", layout="centered")

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
    st.markdown('<div class="auth-header"><h1>JOIN US</h1><p>START YOUR JOURNEY TODAY</p></div>', unsafe_allow_html=True)

    st.text_input("NAME", placeholder="John Doe")
    st.text_input("EMAIL", placeholder="hello@example.com")
    st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("CREATE ACCOUNT"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            st.switch_page("pages/dashboard.py")

    if st.button("ALREADY HAVE AN ACCOUNT? LOGIN"):
        st.session_state.page = "login"
        st.rerun()

else:
    st.markdown('<div class="auth-header"><h1>LOGIN</h1><p>WELCOME BACK, EXPLORER</p></div>', unsafe_allow_html=True)

    st.text_input("EMAIL", placeholder="hello@example.com")
    st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("SIGN IN"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            st.switch_page("pages/dashboard.py")

    if st.button("NEW HERE? CREATE ACCOUNT"):
        st.session_state.page = "signup"
        st.rerun()
