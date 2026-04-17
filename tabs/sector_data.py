# file: tabs/sector_data.py
# 11 S&P sector ETFs — sortable multi-timeframe performance.

import streamlit as st
import pandas as pd

from data.yf_fetcher import get_sector_multi_timeframe
from config import GREEN_UP, RED_DOWN, GREY_TEXT, BORDER


def render():
    st.markdown(
        f"<p style='color:{GREY_TEXT};font-size:12px;margin:4px 0 16px;'>"
        f"11 S&P sectors (SPDR ETFs). Click any column header to sort ascending/descending."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching sector performance across timeframes..."):
        df = get_sector_multi_timeframe()

    if df.empty:
        st.markdown(
            f"<div style='color:{GREY_TEXT};padding:14px;border:1px solid {BORDER};'>"
            f"Data unavailable</div>",
            unsafe_allow_html=True,
        )
        return

    pct_cols = ["1D", "1W", "1M", "3M", "6M", "1Y", "3Y"]
    df = df[["sector", "symbol", "price"] + pct_cols].rename(columns={
        "sector": "SECTOR",
        "symbol": "SYMBOL",
        "price":  "PRICE",
    })

    # Color formatter for % columns
    def _color(v):
        if pd.isna(v):
            return f"color: {GREY_TEXT}"
        return f"color: {GREEN_UP}; font-weight: 600" if v >= 0 \
               else f"color: {RED_DOWN}; font-weight: 600"

    def _fmt_pct(v):
        if pd.isna(v): return "—"
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.2f}%"

    styled = (
        df.style
          .format({"PRICE": "{:,.2f}", **{c: _fmt_pct for c in pct_cols}})
          .map(_color, subset=pct_cols)
    )

    st.dataframe(
        styled,
        width="stretch",
        height=460,
        hide_index=True,
    )