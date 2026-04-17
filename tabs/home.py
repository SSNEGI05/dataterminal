# file: tabs/home.py
# Home tab — index cards + S&P 500 and Nasdaq 100 charts.

import streamlit as st
import matplotlib.pyplot as plt

from data.yf_fetcher import get_major_indices, get_history
from utils.formatting import format_price
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL, BG_BLACK,
    BORDER, FONT_MONO, GREY_TEXT,
)


def _index_card_html(name, price, pct):
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
    st.markdown(
        f"<div style='color:{GREY_TEXT};font-size:11px;letter-spacing:2px;margin-bottom:8px;'>MAJOR INDICES</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching indices..."):
        indices = get_major_indices()

    if not indices:
        st.markdown(f"<p style='color:{GREY_TEXT};'>Data unavailable</p>", unsafe_allow_html=True)
        return

    cols = st.columns(len(indices))
    for col, idx in zip(cols, indices):
        with col:
            st.markdown(
                _index_card_html(idx["name"], idx["price"], idx["pct_change"]),
                unsafe_allow_html=True,
            )


def _plot_index(symbol, display_name, period="1y"):          # 🔧 period: 3mo, 6mo, 1y, 2y, 5y, max
    df = get_history(symbol, period=period, interval="1d")
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 3.2), facecolor=BG_BLACK)   # 🔧 chart size
    ax.set_facecolor(BG_BLACK)

    start_price = df["Close"].iloc[0]
    end_price   = df["Close"].iloc[-1]
    line_color  = GREEN_UP if end_price >= start_price else RED_DOWN

    ax.plot(df.index, df["Close"], color=line_color, linewidth=1.4)
    ax.fill_between(df.index, df["Close"], df["Close"].min(), color=line_color, alpha=0.08)

    ax.set_title(f"{display_name}  —  {period.upper()}",
                 color=ORANGE, fontsize=11, loc="left",
                 family="monospace", pad=12)
    ax.tick_params(colors=GREY_TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.grid(True, color=BORDER, linewidth=0.4, alpha=0.5)

    plt.tight_layout()
    return fig


def _render_charts():
    st.markdown(
        f"<div style='color:{GREY_TEXT};font-size:11px;letter-spacing:2px;margin:24px 0 8px;'>INDEX CHARTS</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = _plot_index("^GSPC", "S&P 500")
        if fig:
            st.pyplot(fig, width="stretch")
            plt.close(fig)

    with col2:
        fig = _plot_index("^NDX", "NASDAQ 100")
        if fig:
            st.pyplot(fig, width="stretch")
            plt.close(fig)


def render():
    _render_indices()
    _render_charts()