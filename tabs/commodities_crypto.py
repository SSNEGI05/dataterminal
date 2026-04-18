# file: tabs/commodities_crypto.py
# Commodities & Crypto tab — Gold, Crude Oil, Bitcoin, Ethereum, Silver

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from data.yf_fetcher import get_history, get_quote
from config import ORANGE, ORANGE_DIM, WHITE, FONT_MONO
from utils.formatting import format_price, format_pct


# 🔧 Add or remove assets here
ASSETS = {
    "Gold":      "GC=F",
    "Silver":    "SI=F",
    "Crude Oil": "CL=F",
    "Bitcoin":   "BTC-USD",
    "Ethereum":  "ETH-USD",
}

# 🔧 Chart timeframe options
PERIODS = {
    "1W": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
}


def _make_chart(df, name, period_label):
    """Bloomberg-style price chart for one asset."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    fig.patch.set_facecolor("#000000")
    ax.set_facecolor("#000000")

    close = df["Close"].dropna()
    if close.empty:
        return None

    # green if price went up over the period, red if down
    color = "#00C853" if float(close.iloc[-1]) >= float(close.iloc[0]) else "#FF1744"

    ax.plot(close.index, close.values, color=color, linewidth=1.5)
    ax.fill_between(close.index, close.values, alpha=0.08, color=color)

    ax.set_title(f"{name}  —  {period_label}", color=ORANGE, fontsize=12,
                 fontfamily="monospace", loc="left", pad=10)

    ax.tick_params(colors="#666666", labelsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.2f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333333")
    ax.spines["bottom"].set_color("#333333")
    ax.grid(axis="y", color="#1a1a1a", linewidth=0.5)

    plt.tight_layout()
    return fig


def render():
    st.markdown(
        f"<h2 style='color:{ORANGE};font-family:{FONT_MONO};letter-spacing:2px;'>"
        f"COMMODITIES & CRYPTO</h2>",
        unsafe_allow_html=True,
    )

    # --- Timeframe selector ---
    cols_period = st.columns(len(PERIODS))
    if "commod_period" not in st.session_state:
        st.session_state.commod_period = "3M"

    for i, label in enumerate(PERIODS.keys()):
        if cols_period[i].button(label, key=f"commod_{label}",
                                  use_container_width=True):
            st.session_state.commod_period = label

    selected_label = st.session_state.commod_period
    selected_period = PERIODS[selected_label]

    st.markdown("<div style='padding:8px 0;'></div>", unsafe_allow_html=True)

    # --- Price cards + charts ---
    for name, symbol in ASSETS.items():
        quote = get_quote(symbol)
        hist = get_history(symbol, period=selected_period)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 6])

        with col1:
            st.markdown(
                f"<div style='font-family:{FONT_MONO};color:{ORANGE};font-size:16px;"
                f"font-weight:500;padding-top:8px;'>{name}</div>"
                f"<div style='color:#666;font-size:11px;'>{symbol}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            if quote:
                st.markdown(
                    f"<div style='font-family:{FONT_MONO};color:{WHITE};"
                    f"font-size:20px;padding-top:6px;'>"
                    f"{format_price(quote['price'])}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("—")

        with col3:
            if quote:
                pct = quote["pct_change"]
                color = "#00C853" if pct >= 0 else "#FF1744"
                arrow = "▲" if pct >= 0 else "▼"
                st.markdown(
                    f"<div style='font-family:{FONT_MONO};color:{color};"
                    f"font-size:18px;padding-top:6px;'>"
                    f"{arrow} {format_pct(pct)}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("—")

        with col4:
            if not hist.empty:
                fig = _make_chart(hist, name, selected_label)
                if fig:
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
            else:
                st.markdown(
                    f"<div style='color:#666;padding-top:20px;'>No chart data</div>",
                    unsafe_allow_html=True,
                )

        # Divider between assets
        st.markdown(
            f"<hr style='border:none;border-top:1px solid #1a1a1a;margin:4px 0 12px 0;'>",
            unsafe_allow_html=True,
        )