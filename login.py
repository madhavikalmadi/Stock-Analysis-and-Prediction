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

html, body {
    height: 100%;
}

[data-testid="stAppViewContainer"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #F0F2F5 !important;
}

#MainMenu, footer, header {visibility: hidden;}

.block-container {
    width: 440px !important;
    background: white;
    border: 3px solid black;
    box-shadow: 10px 10px 0 black;
    padding: 40px !important;
    margin: auto !important;
}

.auth-header {
    text-align: center;
    margin-bottom: 25px;
}

.auth-header h1 {
    font-weight: 800;
    font-size: 38px;
    text-transform: uppercase;
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
}

div.stButton > button:hover {
    background: #FFDE59 !important;
    color: black !important;
    box-shadow: 4px 4px 0 black;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# UI LOGIC
# -------------------------------------------------

if st.session_state.page == "signup":
    st.markdown('<div class="auth-header"><h1>JOIN US</h1><p>START YOUR JOURNEY TODAY</p></div>', unsafe_allow_html=True)

    name = st.text_input("NAME", placeholder="John Doe")
    email = st.text_input("EMAIL", placeholder="hello@example.com")
    password = st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("CREATE ACCOUNT"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            # FIXED PATH: Points to the file you renamed in your image
            st.switch_page("pages/dashboard.py")

    if st.button("ALREADY HAVE AN ACCOUNT? LOGIN", key="go_login"):
        st.session_state.page = "login"
        st.rerun()

else:
    st.markdown('<div class="auth-header"><h1>LOGIN</h1><p>WELCOME BACK, EXPLORER</p></div>', unsafe_allow_html=True)

    email = st.text_input("EMAIL", placeholder="hello@example.com")
    password = st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("SIGN IN"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            # FIXED PATH: Points to the file you renamed in your image
            st.switch_page("pages/dashboard.py")

    if st.button("NEW HERE? CREATE ACCOUNT", key="go_signup"):
        st.session_state.page = "signup"
        st.rerun()