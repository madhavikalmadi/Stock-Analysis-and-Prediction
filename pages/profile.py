import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="User Profile",
    page_icon="👤",
    layout="wide"
)

# =============================================================
# SESSION STATE
# =============================================================
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

# =============================================================
# CUSTOM CSS (UNCHANGED + WHITE DASHBOARD BUTTON)
# =============================================================
st.markdown("""
<style>
/* Hide default Streamlit elements */
[data-testid="stSidebar"],
.stAppDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
body {
    font-family: 'Outfit', sans-serif !important;
}

/* Profile card */
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

.user-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
}

.user-tag {
    background: #dbeafe;
    color: #2563eb;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Buttons */
div.stButton > button {
    width: 100%;
    border-radius: 8px;
    font-weight: 600;
}

/* Clear button */
.stClearButton > button {
    width: auto !important;
    background: #ef4444 !important;
    color: white !important;
    padding: 0.5rem 1rem;
    margin-top: 1rem;
    font-size: 0.9rem;
    border: none;
    transition: all 0.3s;
}

.stClearButton > button:hover {
    background: #dc2626 !important;
    transform: translateY(-1px);
}

/* ================================
   WHITE DASHBOARD BUTTON (SAME STYLE)
   ================================ */
div.stButton:last-of-type > button {
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 50px !important;

    background: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #e5e7eb !important;

    box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
    width: auto !important;
    margin: 0 auto;
    white-space: nowrap !important;
}

div.stButton:last-of-type > button:hover {
    background: #f8fafc !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# PAGE TITLE
# =============================================================
st.markdown(
    "<h1 style='text-align:center; margin-bottom:30px;'>👤 User Profile</h1>",
    unsafe_allow_html=True
)

# =============================================================
# PROFILE LAYOUT
# =============================================================
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("""
    <div class="profile-card">
        <div class="profile-pic">👨‍💻</div>
        <div class="user-name">Guest User</div>
        <span class="user-tag">Beginner Investor</span>
        <hr style="margin:20px 0; opacity:0.2;">
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

    tab1, tab2 = st.tabs(["Recent Views", "Saved Stocks"])

    with tab1:
        st.info("You recently viewed: **TATA MOTORS**, **RELIANCE**, **HDFCBANK**")

    with tab2:
        watchlist = st.session_state.watchlist
        count = len(watchlist)

        st.success(f"You have **{count}** saved stocks in your watchlist.")

        if count > 0:
            st.write("---")
            st.markdown(f"**Your Watchlist ({count} items):**")
            st.markdown("\n".join([f"* **{stock}**" for stock in watchlist]))

            if st.button("🗑️ Clear Watchlist", key="clear_wl"):
                st.session_state.watchlist = []
                st.toast("Watchlist cleared!")
                st.rerun()
        else:
            st.markdown("*Start exploring stocks to add them here!*")

# =============================================================
# DASHBOARD NAVIGATION (SAME PLACE, WHITE)
# =============================================================
st.write("")
st.write("---")

c1, c2, c3 = st.columns([5, 2, 5])
with c2:
    if st.button("⬅ Dashboard", key="btn_home_nav"):
        st.switch_page("pages/dashboard.py")

# =============================================================
# FOOTER
# =============================================================
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.8rem;'>"
    "Smart Investor Assistant • v2.0"
    "</div>",
    unsafe_allow_html=True
)
