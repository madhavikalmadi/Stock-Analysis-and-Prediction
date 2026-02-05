import streamlit as st

# ======================================================
# Theme Configuration
# ======================================================

THEMES = {
    "light": {
        "name": "light",
        "background_gradient": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "background_color": "#ffffff",
        "text_color": "#334155",
        "card_bg": "rgba(255, 255, 255, 0.65)",
        "card_border": "rgba(255, 255, 255, 0.9)",
        "sidebar_bg": "#f8fafc"
    },
    "dark": {
        "name": "dark",
        "background_gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "background_color": "#0f172a",
        "text_color": "#f1f5f9",
        "card_bg": "rgba(30, 41, 59, 0.7)",
        "card_border": "rgba(148, 163, 184, 0.2)",
        "sidebar_bg": "#020617"
    }
}

# ======================================================
# Functions
# ======================================================

def get_theme():
    """
    Returns the current theme NAME ('light' or 'dark').
    """
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    return st.session_state["theme"]

def toggle_theme():
    """
    Callback function to switch between light and dark modes.
    """
    current = get_theme()
    new_theme = "dark" if current == "light" else "light"
    st.session_state["theme"] = new_theme

def render_theme_toggle():
    """
    Renders a button to switch themes. 
    Can be placed in the sidebar or top corner.
    """
    current = get_theme()
    btn_text = "🌙 Dark Mode" if current == "light" else "☀️ Light Mode"
    st.button(btn_text, on_click=toggle_theme, key="theme_toggle_btn")

def apply_theme(theme_name):
    """
    Injects the CSS for the selected theme.
    """
    # Fallback to light if invalid theme name provided
    theme_data = THEMES.get(theme_name, THEMES["light"])
    
    css = f"""
    <style>
        /* Main Background */
        [data-testid="stAppViewContainer"] {{
            background: {theme_data['background_gradient']};
            color: {theme_data['text_color']};
        }}
        
        /* Sidebar Background */
        [data-testid="stSidebar"] {{
            background-color: {theme_data['sidebar_bg']};
        }}

        /* Text Colors */
        h1, h2, h3, h4, h5, h6, p, li {{
            color: {theme_data['text_color']} !important;
        }}
        
        /* Card / Glassmorphism Overrides */
        .glass-panel, .path-card, .insight-box {{
            background: {theme_data['card_bg']} !important;
            border: 1px solid {theme_data['card_border']} !important;
        }}
        
        /* Specific override for ticker in Dark Mode */
        .ticker-wrap {{
            background-color: {theme_data['card_bg']} !important;
            border: 1px solid {theme_data['card_border']} !important;
        }}
        
        .ticker__item {{
            color: {theme_data['text_color']} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)