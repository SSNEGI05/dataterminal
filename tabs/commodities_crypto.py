# file: tabs/commodities_crypto.py
# Commodities & Crypto — 2x2 grid layout

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from data.yf_fetcher import get_history, get_quote
from config import ORANGE, ORANGE_DIM, WHITE, FONT_MONO
from utils.formatting import format_price, format_pct


# 🔧 4 assets in 2x2 grid
ASSETS = {
    "Crude Oil": "CL=F",
    "Gold":      "GC=F",
    "Silver":    "SI=F",
    "Bitcoin":   "BTC-USD",
}

# 🔧 Timeframe options
PERIODS = {
    "1D": "1d",
    "1W": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
}


def _make_chart(df, name):
    """Bloomberg-style price chart."""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#000000")
    ax.set_facecolor("#000000")

    close = df["Close"].dropna()
    if close.empty:
        return None

    color = "#00C853" if float(close.iloc[-1]) >= float(close.iloc[0]) else "#FF1744"

    ax.plot(close.index, close.values, color=color, linewidth=1.5)
    ax.fill_between(close.index, close.values, alpha=0.06, color=color)

    # Y-axis starts from actual min, not zero
    y_min = float(close.min()) * 0.98
    y_max = float(close.max()) * 1.02
    ax.set_ylim(y_min, y_max)

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

    st.markdown("<div style='padding:10px 0;'></div>", unsafe_allow_html=True)

    # --- 2x2 Grid ---
    asset_list = list(ASSETS.items())

    for row in range(0, len(asset_list), 2):
        col_left, col_right = st.columns(2, gap="large")

        for idx, col in enumerate([col_left, col_right]):
            if row + idx >= len(asset_list):
                break

            name, symbol = asset_list[row + idx]
            quote = get_quote(symbol)
            hist = get_history(symbol, period=selected_period)

            with col:
                # Price header
                if quote:
                    pct = quote["pct_change"]
                    pct_color = "#00C853" if pct >= 0 else "#FF1744"
                    arrow = "▲" if pct >= 0 else "▼"

                    st.markdown(
                        f"""<div style='font-family:{FONT_MONO};padding:8px 0 4px 0;'>
                            <span style='color:{ORANGE};font-size:18px;font-weight:500;'>{name}</span>
                            <span style='color:#666;font-size:11px;margin-left:8px;'>{symbol}</span>
                        </div>
                        <div style='font-family:{FONT_MONO};display:flex;align-items:baseline;gap:16px;'>
                            <span style='color:{WHITE};font-size:28px;font-weight:500;'>{format_price(quote['price'])}</span>
                            <span style='color:{pct_color};font-size:18px;'>{arrow} {format_pct(pct)}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='font-family:{FONT_MONO};color:{ORANGE};"
                        f"font-size:18px;padding:8px 0;'>{name}</div>"
                        f"<div style='color:#666;'>No data</div>",
                        unsafe_allow_html=True,
                    )

                # Chart below price
                if not hist.empty:
                    fig = _make_chart(hist, name)
                    if fig:
                        st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
                else:
                    st.markdown(
                        "<div style='color:#666;padding:40px 0;text-align:center;'>No chart data</div>",
                        unsafe_allow_html=True,
                    )

        # Space between rows
        st.markdown("<div style='padding:8px 0;'></div>", unsafe_allow_html=True)