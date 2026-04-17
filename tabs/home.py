# file: tabs/home.py
# Home tab — the terminal's front page.
# Built in pieces: 2A index cards → 2B charts → 2C gainers/losers preview

import streamlit as st
from data.yf_fetcher import get_major_indices
from utils.formatting import format_price, format_pct
from config import ORANGE, GREEN_UP, RED_DOWN, BG_PANEL, BORDER, FONT_MONO, GREY_TEXT


def _index_card_html(name, price, pct):
    """Build one Bloomberg-style index card as raw HTML."""
    color = GREEN_UP if pct >= 0 else RED_DOWN
    sign  = "+" if pct >= 0 else ""

    return f"""
    <div style="
        background:{BG_PANEL};
        border:1px solid {BORDER};
        padding:14px 18px;
        font-family:{FONT_MONO};
        min-height:100px;
    ">
        <div style="color:{GREY_TEXT};font-size:11px;letter-spacing:2px;">
            {name.upper()}
        </div>
        <div style="color:{ORANGE};font-size:24px;font-weight:500;margin:4px 0;">
            {format_price(price)}
        </div>
        <div style="color:{color};font-size:13px;">
            {sign}{pct:.2f}%
        </div>
    </div>
    """


def _render_indices():
    """Top strip — 5 index cards in a row."""
    st.markdown(
        f"<div style='color:{GREY_TEXT};font-size:11px;letter-spacing:2px;margin-bottom:8px;'>MAJOR INDICES</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching indices..."):
        indices = get_major_indices()

    if not indices:
        st.markdown(f"<p style='color:{GREY_TEXT};'>Data unavailable</p>", unsafe_allow_html=True)
        return

    # 5 columns, one per index
    cols = st.columns(len(indices))
    for col, idx in zip(cols, indices):
        with col:
            st.markdown(
                _index_card_html(idx["name"], idx["price"], idx["pct_change"]),
                unsafe_allow_html=True,
            )


def render():
    """Main entry point for Home tab. Called from app.py."""
    _render_indices()

    # Spacer
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{GREY_TEXT};'>S&P 500 and Nasdaq 100 charts coming next.</p>",
        unsafe_allow_html=True,
    )