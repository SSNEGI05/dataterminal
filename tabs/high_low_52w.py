# file: tabs/high_low_52w.py
# S&P 500 stocks near their 52-week highs and lows.

import streamlit as st
from data.yf_fetcher import get_52w_extremes
from utils.formatting import format_price
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL,
    BORDER, FONT_MONO, GREY_TEXT,
)


def _build_table_html(df, is_high, title):
    """Build full table as one HTML string."""
    color     = GREEN_UP if is_high else RED_DOWN
    ref_col   = "high_52w" if is_high else "low_52w"
    pct_col   = "pct_from_high" if is_high else "pct_from_low"
    ref_label = "52W HIGH" if is_high else "52W LOW"

    # Table header
    html = (
        f'<div style="background:{BG_PANEL};padding:10px 14px;border:1px solid {BORDER};'
        f'color:{GREY_TEXT};font-size:11px;letter-spacing:2px;font-family:{FONT_MONO};">'
        f'{title}</div>'
    )

    # Column labels row
    html += (
        f'<div style="display:flex;justify-content:space-between;'
        f'padding:6px 14px;background:{BG_PANEL};border-left:1px solid {BORDER};'
        f'border-right:1px solid {BORDER};border-bottom:1px solid {BORDER};'
        f'font-family:{FONT_MONO};font-size:10px;letter-spacing:1.5px;color:{GREY_TEXT};">'
        f'<span style="width:22%;">SYMBOL</span>'
        f'<span style="width:26%;text-align:right;">PRICE</span>'
        f'<span style="width:26%;text-align:right;">{ref_label}</span>'
        f'<span style="width:20%;text-align:right;">FROM {"HIGH" if is_high else "LOW"}</span>'
        f'</div>'
    )

    if df.empty:
        html += (
            f'<div style="padding:14px;color:{GREY_TEXT};'
            f'border:1px solid {BORDER};border-top:none;">No stocks within threshold</div>'
        )
        return html

    # Data rows
    rows_html = ""
    for _, r in df.iterrows():
        sign = "+" if r[pct_col] >= 0 else ""
        rows_html += (
            f'<div style="display:flex;justify-content:space-between;'
            f'padding:8px 14px;border-bottom:1px solid {BORDER};'
            f'font-family:{FONT_MONO};font-size:13px;">'
            f'<span style="color:{ORANGE};font-weight:500;width:22%;">{r["symbol"]}</span>'
            f'<span style="color:white;width:26%;text-align:right;">{format_price(r["price"])}</span>'
            f'<span style="color:{GREY_TEXT};width:26%;text-align:right;">{format_price(r[ref_col])}</span>'
            f'<span style="color:{color};width:20%;text-align:right;">{sign}{r[pct_col]:.2f}%</span>'
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
        f"S&P 500 stocks within 2% of their 52-week high or low."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Analyzing S&P 500 52-week ranges... (first load ~20 sec)"):
        near_high, near_low = get_52w_extremes(threshold_pct=2.0, top_n=15)

    col_h, col_l = st.columns(2)
    with col_h:
        st.markdown(_build_table_html(near_high, True, "NEAR 52-WEEK HIGH"), unsafe_allow_html=True)
    with col_l:
        st.markdown(_build_table_html(near_low, False, "NEAR 52-WEEK LOW"), unsafe_allow_html=True)