import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="User Profile", page_icon="👤", layout="wide")

# --- CUSTOM CSS (Keeps the same look as your app) ---
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    [data-testid="stSidebar"], .stAppDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* FONT & DESIGN */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    body { font-family: 'Outfit', sans-serif !important; }
    
    /* CARD STYLING */
    .profile-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
        border-top: 5px solid #2563eb;
    }
    .profile-pic {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .user-name { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
    .user-tag { 
        background: #dbeafe; color: #2563eb; 
        padding: 4px 12px; border-radius: 20px; 
        font-size: 0.8rem; font-weight: 600;
    }
    
    /* BUTTON STYLING */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER WITH BACK BUTTON ---
c1, c2 = st.columns([1, 8])
with c1:
    if st.button("⬅ Home"):
        st.switch_page("app.py")

st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>👤 User Profile</h1>", unsafe_allow_html=True)

# --- PROFILE LAYOUT ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("""
    <div class="profile-card">
        <div class="profile-pic">👨‍💻</div>
        <div class="user-name">Guest User</div>
        <span class="user-tag">Beginner Investor</span>
        <hr style="margin: 20px 0; opacity: 0.2;">
        <p style="font-size:0.9rem; color:#64748b;">Member since: Dec 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Account Settings"):
        st.checkbox("Dark Mode (Coming Soon)", disabled=True)
        st.checkbox("Email Notifications", value=True)
        if st.button("Log Out"):
            st.toast("Logged out successfully!")

with col_right:
    st.subheader("📊 My Activity")
    
    # Mock Data for Activity
    tab1, tab2 = st.tabs(["Recent Views", "Saved Stocks"])
    
    with tab1:
        st.info("You recently viewed: **TATA MOTORS**, **RELIANCE**, **HDFCBANK**")
        st.progress(70, text="Profile Completion")
    
    with tab2:
        st.success("You have **0** saved stocks in your watchlist.")
        st.markdown("*Start exploring stocks to add them here!*")

# --- FOOTER ---
st.write("---")
st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>Smart Investor Assistant • v2.0</div>", unsafe_allow_html=True)