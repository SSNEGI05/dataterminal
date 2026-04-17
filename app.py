# file: app.py
# Main entry point for DataTerminal.
# Run:  streamlit run app.py

import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu

from config import APP_NAME, APP_TAGLINE, ORANGE, ORANGE_DIM, WHITE, FONT_MONO
from utils.styling import apply_theme
from utils.ticker_tape import render_ticker_tape


# ---------- page config (must be first Streamlit call) ----------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",               # 🔧 change: emoji shown in browser tab
    layout="wide",                # 🔧 'wide' uses full width, 'centered' is narrower
    initial_sidebar_state="collapsed",
)

# ---------- apply Bloomberg theme ----------
apply_theme()


# ---------- track when data was last refreshed ----------
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()


def time_since_refresh():
    """Return 'Xm ago' string since last data refresh."""
    delta = datetime.now() - st.session_state.last_refresh
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins == 1:
        return "1 min ago"
    return f"{mins} min ago"


# ---------- HEADER: app name + tagline + last updated ----------
header_html = f"""
<div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:14px 4px 10px 4px;
    border-bottom:1px solid {ORANGE_DIM};
    font-family:{FONT_MONO};
">
    <div>
        <span style="color:{ORANGE};font-size:22px;font-weight:500;letter-spacing:3px;">
            {APP_NAME}
        </span>
        <span style="color:{ORANGE_DIM};font-size:12px;margin-left:14px;letter-spacing:1.5px;">
            {APP_TAGLINE}
        </span>
    </div>
    <div style="color:{ORANGE_DIM};font-size:11px;letter-spacing:1.5px;">
        🕒 UPDATED {time_since_refresh().upper()}
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ---------- TICKER TAPE (scrolling stocks) ----------
render_ticker_tape()


# ---------- TAB NAVIGATION ----------
TAB_NAMES = [
    "Home",
    "Gainers/Losers",
    "52W High/Low",
    "All-Time Highs",
    "Market News",
    "Sector Data",
    "Sector Rotation",
    "Macro Data",
]

selected_tab = option_menu(
    menu_title=None,
    options=TAB_NAMES,
    default_index=0,
    orientation="horizontal",
    styles={
        "container":     {"background-color": "#000000", "padding": "0"},
        "nav-link":      {
            "color": WHITE,
            "font-family": FONT_MONO,
            "font-size": "12px",
            "letter-spacing": "1px",
            "padding": "10px 16px",
            "border-radius": "0px",
            "margin": "0 2px",
        },
        "nav-link-selected": {
            "background-color": ORANGE,
            "color": "#000000",
            "font-weight": "500",
        },
    },
)


# ---------- TAB CONTENT (placeholders for now) ----------
st.markdown(f"<div style='padding:30px 0;'></div>", unsafe_allow_html=True)

if selected_tab == "Home":
    from tabs import home
    home.render()
    
elif selected_tab == "Gainers/Losers":
    st.markdown(f"<h2>TOP GAINERS & LOSERS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "52W High/Low":
    st.markdown(f"<h2>52-WEEK HIGH / LOW</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "All-Time Highs":
    st.markdown(f"<h2>ALL-TIME HIGHS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "Market News":
    st.markdown(f"<h2>MARKET NEWS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "Sector Data":
    st.markdown(f"<h2>SECTOR DATA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "Sector Rotation":
    st.markdown(f"<h2>SECTOR ROTATION</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)
elif selected_tab == "Macro Data":
    st.markdown(f"<h2>MACRO DATA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Coming soon.</p>", unsafe_allow_html=True)