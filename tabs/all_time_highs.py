# file: tabs/all_time_highs.py
# S&P 500 stocks at or near all-time highs.

import streamlit as st
from data.yf_fetcher import get_all_time_highs
from utils.formatting import format_price
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL,
    BORDER, FONT_MONO, GREY_TEXT,
)


def _build_table_html(df):
    # Header bar
    html = (
        f'<div style="background:{BG_PANEL};padding:10px 14px;border:1px solid {BORDER};'
        f'color:{GREY_TEXT};font-size:11px;letter-spacing:2px;font-family:{FONT_MONO};">'
        f'TOP 20 — CLOSEST TO ALL-TIME HIGH</div>'
    )

    # Column labels
    html += (
        f'<div style="display:flex;justify-content:space-between;'
        f'padding:6px 14px;background:{BG_PANEL};border-left:1px solid {BORDER};'
        f'border-right:1px solid {BORDER};border-bottom:1px solid {BORDER};'
        f'font-family:{FONT_MONO};font-size:10px;letter-spacing:1.5px;color:{GREY_TEXT};">'
        f'<span style="width:6%;">#</span>'
        f'<span style="width:20%;">SYMBOL</span>'
        f'<span style="width:24%;text-align:right;">PRICE</span>'
        f'<span style="width:24%;text-align:right;">ALL-TIME HIGH</span>'
        f'<span style="width:22%;text-align:right;">FROM ATH</span>'
        f'</div>'
    )

    if df.empty:
        html += (
            f'<div style="padding:14px;color:{GREY_TEXT};'
            f'border:1px solid {BORDER};border-top:none;">Data unavailable</div>'
        )
        return html

    rows_html = ""
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        # pct_from_ath is 0 when at ATH, negative below. Color = green if within 2%, red if deep below.
        color = GREEN_UP if r["pct_from_ath"] >= -2 else RED_DOWN
        sign  = "+" if r["pct_from_ath"] >= 0 else ""

        rows_html += (
            f'<div style="display:flex;justify-content:space-between;'
            f'padding:8px 14px;border-bottom:1px solid {BORDER};'
            f'font-family:{FONT_MONO};font-size:13px;">'
            f'<span style="color:{GREY_TEXT};width:6%;">{i:02d}</span>'
            f'<span style="color:{ORANGE};font-weight:500;width:20%;">{r["symbol"]}</span>'
            f'<span style="color:white;width:24%;text-align:right;">{format_price(r["price"])}</span>'
            f'<span style="color:{GREY_TEXT};width:24%;text-align:right;">{format_price(r["ath"])}</span>'
            f'<span style="color:{color};width:22%;text-align:right;">{sign}{r["pct_from_ath"]:.2f}%</span>'
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
        f"S&P 500 stocks ranked by proximity to their all-time high. "
        f"Green = within 2% of ATH (breakout zone)."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Analyzing 500 stocks vs all-time highs... (first load ~30-45 sec)"):
        df = get_all_time_highs(top_n=20)

    st.markdown(_build_table_html(df), unsafe_allow_html=True)