import streamlit as st
import base64

def get_token(email):
    """Generate a simple session token from the email."""
    # In a production app, use use a secure, signed token (e.g., JWT).
    # For now, base64 encoding serves as a simple persistence mechanism.
    return base64.b64encode(email.encode()).decode()

def verify_token(token):
    """Decode the token back to an email."""
    try:
        return base64.b64decode(token.encode()).decode()
    except:
        return None

def login_user(email):
    """Log the user in and set the session persistence parameter."""
    st.session_state.logged_in = True
    st.session_state.user_email = email
    
    # Set the session token in the URL
    token = get_token(email)
    st.query_params["session"] = token

def check_auth():
    """
    Check if the user is authenticated.
    If not in session_state, check the URL query parameter and restore session if valid.
    Returns True if authenticated, False otherwise.
    """
    # 1. Check active session
    if st.session_state.get("logged_in"):
        # Ensure URL persistence: If logged in but URL param missing, set it.
        # This handles cases where switch_page might have cleared params.
        if "session" not in st.query_params:
            email = st.session_state.get("user_email")
            if email:
                token = get_token(email)
                st.query_params["session"] = token
        return True

    # 2. Check URL for session token (Persistence)
    query_params = st.query_params
    token = query_params.get("session")

    if token:
        email = verify_token(token)
        if email:
            # Restore session
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True
    
    return False

def logout_user():
    """Clear session state and query parameters."""
    st.session_state.logged_in = False
    if "user_email" in st.session_state:
        del st.session_state["user_email"]
    
    # Remove session token specifically
    if "session" in st.query_params:
        del st.query_params["session"]
