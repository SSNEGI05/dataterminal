# file: tabs/gainers_losers.py
# Top 10 gainers and losers from S&P 500.

import streamlit as st
from data.yf_fetcher import get_gainers_losers
from utils.formatting import format_price
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL,
    BORDER, FONT_MONO, GREY_TEXT,
)


def _build_table_html(df, is_gainer, title):
    """Build one full table as a single HTML string (prevents rendering breaks)."""
    color = GREEN_UP if is_gainer else RED_DOWN

    # Header
    html = (
        f'<div style="background:{BG_PANEL};padding:10px 14px;border:1px solid {BORDER};'
        f'color:{GREY_TEXT};font-size:11px;letter-spacing:2px;font-family:{FONT_MONO};">'
        f'{title}</div>'
    )

    if df.empty:
        html += (
            f'<div style="padding:14px;color:{GREY_TEXT};'
            f'border:1px solid {BORDER};border-top:none;">Data unavailable</div>'
        )
        return html

    # Rows
    rows_html = ""
    for _, r in df.iterrows():
        sign = "+" if r["pct_change"] >= 0 else ""
        rows_html += (
            f'<div style="display:flex;justify-content:space-between;'
            f'padding:8px 14px;border-bottom:1px solid {BORDER};'
            f'font-family:{FONT_MONO};font-size:13px;">'
            f'<span style="color:{ORANGE};font-weight:500;width:25%;">{r["symbol"]}</span>'
            f'<span style="color:white;width:35%;text-align:right;">{format_price(r["price"])}</span>'
            f'<span style="color:{color};width:30%;text-align:right;">{sign}{r["pct_change"]:.2f}%</span>'
            f'</div>'
        )

    html += (
        f'<div style="background:{BG_PANEL};border:1px solid {BORDER};border-top:none;">'
        f'{rows_html}</div>'
    )
    return html


def render():
    st.markdown(
        f"<p style='color:{GREY_TEXT};font-size:12px;margin:4px 0 16px;'>"
        f"Showing top 10 from S&P 500 — today's % change vs previous close."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching S&P 500 data... (first load takes ~15 sec)"):
        gainers, losers = get_gainers_losers(universe="sp500", top_n=10)

    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown(_build_table_html(gainers, True, "TOP 10 GAINERS"), unsafe_allow_html=True)
    with col_l:
        st.markdown(_build_table_html(losers, False, "TOP 10 LOSERS"), unsafe_allow_html=True)