# file: app.py
# Main entry point for DataTerminal.
# Run:  streamlit run app.py

import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu

from config import APP_NAME, APP_TAGLINE, ORANGE, ORANGE_DIM, WHITE, FONT_MONO
from utils.styling import apply_theme
from utils.ticker_tape import render_ticker_tape


st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()


if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()


def time_since_refresh():
    delta = datetime.now() - st.session_state.last_refresh
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins == 1:
        return "1 min ago"
    return f"{mins} min ago"


# ---------- HEADER ----------
header_html = f"""
<div style="
    display:flex; justify-content:space-between; align-items:center;
    padding:14px 4px 10px 4px;
    border-bottom:1px solid {ORANGE_DIM};
    font-family:{FONT_MONO};
">
    <div>
        <span style="color:{ORANGE};font-size:22px;font-weight:500;letter-spacing:3px;">{APP_NAME}</span>
        <span style="color:{ORANGE_DIM};font-size:12px;margin-left:14px;letter-spacing:1.5px;">{APP_TAGLINE}</span>
    </div>
    <div style="color:{ORANGE_DIM};font-size:11px;letter-spacing:1.5px;">
        🕒 UPDATED {time_since_refresh().upper()}
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ---------- TICKER TAPE ----------
render_ticker_tape()


# ---------- TABS: single registry ----------
from tabs import home, market_news, sector_data, sector_rotation, macro_data, commodities_crypto

TABS = {
    "Home":               home.render,
    "Commodities/Crypto": commodities_crypto.render,
    "Market News":        market_news.render,
    "Sector Data":        sector_data.render,
    "Sector Rotation":    sector_rotation.render,
    "Macro Data":         macro_data.render,
}


# ---------- TAB NAVIGATION ----------
selected_tab = option_menu(
    menu_title=None,
    options=list(TABS.keys()),
    default_index=0,
    orientation="horizontal",
    styles={
        "container":     {"background-color": "#000000", "padding": "0"},
        "nav-link": {
            "color": WHITE, "font-family": FONT_MONO,
            "font-size": "12px", "letter-spacing": "1px",
            "padding": "10px 16px", "border-radius": "0px", "margin": "0 2px",
        },
        "nav-link-selected": {
            "background-color": ORANGE, "color": "#000000", "font-weight": "500",
        },
    },
)


# ---------- TAB CONTENT ----------
st.markdown("<div style='padding:20px 0;'></div>", unsafe_allow_html=True)
TABS[selected_tab]()