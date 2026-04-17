# file: utils/styling.py
# Injects Bloomberg-terminal CSS into Streamlit.
# One function: apply_theme() — called once from app.py at startup.

import streamlit as st
from config import (
    BG_BLACK, BG_PANEL, ORANGE, ORANGE_DIM, WHITE, GREY_TEXT,
    GREEN_UP, RED_DOWN, BORDER, FONT_MONO,
)


def apply_theme():
    """Inject Bloomberg CSS into the Streamlit app."""

    css = f"""
    <style>
    /* ---------- main app background ---------- */
 .stApp {{
    background-color: {BG_BLACK};
    color: {ORANGE};
    font-family: {FONT_MONO};
 }}

  /* ---------- kill Streamlit's default top padding (stronger) ---------- */
 .main .block-container,
 .block-container,
 [data-testid="stAppViewContainer"] > .main > .block-container,
 section.main > div.block-container {{
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
 }}

 /* kill the toolbar/decoration bar above content */
 [data-testid="stHeader"] {{
    height: 0 !important;
    background: transparent !important;
 }}
 [data-testid="stToolbar"] {{
    display: none !important;
 }}
 [data-testid="stDecoration"] {{
    display: none !important;
 }}

 /* pull the whole app view up */
 [data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
 }}

    /* ---------- hide Streamlit default chrome ---------- */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* ---------- headings ---------- */
    h1, h2, h3, h4, h5, h6 {{
        color: {ORANGE} !important;
        font-family: {FONT_MONO};
        letter-spacing: 1px;
    }}

    /* ---------- body text ---------- */
    p, span, label, div {{
        color: {WHITE};
        font-family: {FONT_MONO};
    }}

    /* ---------- tables ---------- */
    .stDataFrame, .stTable {{
        background-color: {BG_PANEL};
        color: {WHITE};
        border: 1px solid {BORDER};
    }}

    /* ---------- buttons ---------- */
    .stButton > button {{
        background-color: {BG_PANEL};
        color: {ORANGE};
        border: 1px solid {ORANGE_DIM};
        border-radius: 0px;
        font-family: {FONT_MONO};
    }}
    .stButton > button:hover {{
        background-color: {ORANGE};
        color: {BG_BLACK};
        border: 1px solid {ORANGE};
    }}

    /* ---------- select/input boxes ---------- */
    .stSelectbox, .stTextInput, .stNumberInput {{
        background-color: {BG_PANEL};
        color: {WHITE};
    }}

    /* ---------- metric cards (st.metric) ---------- */
    [data-testid="stMetricValue"] {{
        color: {ORANGE};
        font-family: {FONT_MONO};
        font-size: 28px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {GREY_TEXT};
        font-family: {FONT_MONO};
        font-size: 12px;
        letter-spacing: 1.5px;
    }}
    [data-testid="stMetricDelta"] {{
        font-family: {FONT_MONO};
    }}

    /* ---------- helper classes used in custom HTML ---------- */
    .bb-up    {{ color: {GREEN_UP}; }}
    .bb-down  {{ color: {RED_DOWN}; }}
    .bb-dim   {{ color: {ORANGE_DIM}; }}
    .bb-label {{
        color: {GREY_TEXT};
        font-size: 11px;
        letter-spacing: 2px;
    }}
    .bb-panel {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        padding: 12px;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)