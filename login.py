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
# CSS
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');

html, body {
    height: 100%;
    overflow: hidden;
}

[data-testid="stAppViewContainer"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #F0F2F5 !important;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Hide Streamlit UI */
#MainMenu, footer, header {visibility: hidden;}

/* Auth Card */
.block-container {
    width: 440px !important;
    background: white;
    border: 3px solid black;
    box-shadow: 10px 10px 0 black;
    padding: 40px !important;
    box-sizing: border-box;
    margin: auto !important;
    animation: cardEnter 0.6s ease-out;
}

@keyframes cardEnter {
    from { opacity: 0; transform: translateY(25px); }
    to   { opacity: 1; transform: translateY(0); }
}

.login-enter {
    animation: loginSlide 0.5s ease-out;
}

@keyframes loginSlide {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
}

.auth-header {
    text-align: center;
    margin-bottom: 25px;
}

.auth-header h1 {
    font-weight: 800;
    font-size: 38px;
    margin-bottom: 0;
    text-transform: uppercase;
}

/* Inputs */
.stTextInput > div > div > input {
    border: 2px solid black !important;
    border-radius: 0 !important;
    padding: 12px !important;
}

/* Buttons */
div.stButton > button {
    width: 100%;
    background: black !important;
    color: white !important;
    border: 2px solid black !important;
    border-radius: 0 !important;
    padding: 14px 0 !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

div.stButton > button:hover {
    background: #FFDE59 !important;
    color: black !important;
    transform: translate(-2px, -2px);
    box-shadow: 4px 4px 0 black;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# UI
# -------------------------------------------------

if st.session_state.page == "signup":
    st.markdown("""
    <div class="auth-header">
        <h1>JOIN US</h1>
        <p>START YOUR JOURNEY TODAY</p>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input("NAME", placeholder="John Doe")
    email = st.text_input("EMAIL", placeholder="hello@example.com")
    password = st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("CREATE ACCOUNT"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            st.switch_page("pages/app.py")

    if st.button("ALREADY HAVE AN ACCOUNT? LOGIN", key="go_login"):
        st.session_state.page = "login"
        st.rerun()

else:
    st.markdown('<div class="login-enter">', unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-header">
        <h1>LOGIN</h1>
        <p>WELCOME BACK, EXPLORER</p>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("EMAIL", placeholder="hello@example.com")
    password = st.text_input("PASSWORD", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("SIGN IN"):
        st.session_state.logged_in = True
        with st.spinner("Redirecting..."):
            st.switch_page("pages/app.py")

    if st.button("NEW HERE? CREATE ACCOUNT", key="go_signup"):
        st.session_state.page = "signup"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
