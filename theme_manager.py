# ======================================================
# Theme Manager
# ======================================================

import streamlit as st

THEMES = {
    "light": {
        "background": "#ffffff",
        "text": "#000000",
        "accent": "#4CAF50"
    },
    "dark": {
        "background": "#0f0f0f",
        "text": "#f5f5f5",
        "accent": "#33a1ff"
    }
}

def get_theme():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    return THEMES[st.session_state["theme"]]

def apply_theme(theme):
    st.markdown(
        f"""
        <style>
        body {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
