# file: tabs/sector_rotation.py
# Sector rotation — ranked leaderboard vs S&P 500.

import streamlit as st
import pandas as pd

from data.yf_fetcher import get_sector_rotation
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL, BG_BLACK,
    BORDER, FONT_MONO, GREY_TEXT,
)
from utils.formatting import format_price


def _build_table_html(df):
    # Header
    html = (
        f'<div style="background:{BG_PANEL};padding:10px 14px;border:1px solid {BORDER};'
        f'color:{GREY_TEXT};font-size:11px;letter-spacing:2px;font-family:{FONT_MONO};">'
        f'SECTOR RANKING — STRONGEST TO WEAKEST</div>'
    )

    # Column labels
    html += (
        f'<div style="display:flex;padding:6px 14px;background:{BG_PANEL};'
        f'border-left:1px solid {BORDER};border-right:1px solid {BORDER};'
        f'border-bottom:1px solid {BORDER};font-family:{FONT_MONO};font-size:10px;'
        f'letter-spacing:1.5px;color:{GREY_TEXT};">'
        f'<span style="width:8%;">RANK</span>'
        f'<span style="width:32%;">SECTOR</span>'
        f'<span style="width:15%;text-align:right;">1W</span>'
        f'<span style="width:15%;text-align:right;">1M</span>'
        f'<span style="width:15%;text-align:right;">3M</span>'
        f'<span style="width:15%;text-align:right;">6M</span>'
        f'</div>'
    )

    rows_html = ""
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        def _col(val):
            if pd.isna(val):
                return f'<span style="width:15%;text-align:right;color:{GREY_TEXT};">—</span>'
            color = GREEN_UP if val >= 0 else RED_DOWN
            sign  = "+" if val >= 0 else ""
            return (f'<span style="width:15%;text-align:right;color:{color};font-weight:500;">'
                    f'{sign}{val:.2f}%</span>')

        rows_html += (
            f'<div style="display:flex;padding:10px 14px;border-bottom:1px solid {BORDER};'
            f'font-family:{FONT_MONO};font-size:13px;align-items:center;">'
            f'<span style="width:8%;color:{ORANGE};font-weight:500;">#{i:02d}</span>'
            f'<span style="width:32%;color:white;">{r["sector"]}</span>'
            f'{_col(r.get("ret_1w"))}'
            f'{_col(r.get("ret_1m"))}'
            f'{_col(r.get("ret_3m"))}'
            f'{_col(r.get("ret_6m"))}'
            f'</div>'
        )

    html += (
        f'<div style="background:{BG_BLACK};border:1px solid {BORDER};border-top:none;">'
        f'{rows_html}</div>'
    )
    return html


def render():
    st.markdown(
        f"<p style='color:{GREY_TEXT};font-size:12px;margin:4px 0 16px;'>"
        f"Relative strength of each sector vs S&P 500 (SPY)."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Computing sector rankings..."):
        df = get_sector_rotation()

    if df.empty:
        st.markdown(
            f"<div style='color:{GREY_TEXT};padding:14px;border:1px solid {BORDER};'>"
            f"Data unavailable</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(_build_table_html(df), unsafe_allow_html=True)