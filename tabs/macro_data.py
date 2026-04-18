# file: tabs/macro_data.py
# US Macro Data — 9 key indicators + 3 trend charts.

import streamlit as st
import matplotlib.pyplot as plt

from data.fred_fetcher import get_all_macro_snapshots, get_macro_series
from config import (
    ORANGE, GREEN_UP, RED_DOWN, BG_PANEL, BG_BLACK,
    BORDER, FONT_MONO, GREY_TEXT,
)


def _card_html(name, snapshot):
    """One Bloomberg-style card for one macro indicator."""
    if snapshot is None:
        return (
            f'<div style="background:{BG_PANEL};border:1px solid {BORDER};'
            f'padding:14px 18px;font-family:{FONT_MONO};min-height:100px;">'
            f'<div style="color:{GREY_TEXT};font-size:11px;letter-spacing:2px;">{name.upper()}</div>'
            f'<div style="color:{GREY_TEXT};font-size:14px;margin-top:10px;">Data unavailable</div>'
            f'</div>'
        )

    latest = snapshot["latest"]
    change = snapshot["change"]
    unit   = snapshot["unit"]

    # Format latest value
    if unit == "K":
        value_str = f"{latest:+,.0f}K"
    else:
        value_str = f"{latest:.2f}{unit}"

    # Format change
    color = GREEN_UP if change >= 0 else RED_DOWN
    sign  = "+" if change >= 0 else ""
    if unit == "K":
        change_str = f"{sign}{change:,.0f}K vs prior"
    else:
        change_str = f"{sign}{change:.2f}{unit} vs prior"

    return f"""
    <div style="background:{BG_PANEL};border:1px solid {BORDER};
                padding:14px 18px;font-family:{FONT_MONO};min-height:100px;">
        <div style="color:{GREY_TEXT};font-size:11px;letter-spacing:2px;">{name.upper()}</div>
        <div style="color:{ORANGE};font-size:24px;font-weight:500;margin:4px 0;">{value_str}</div>
        <div style="color:{color};font-size:12px;">{change_str}</div>
    </div>
    """


def _render_group(title, indicators, snapshots):
    st.markdown(
        f"<div style='color:{GREY_TEXT};font-size:11px;letter-spacing:2px;margin:24px 0 8px;'>"
        f"{title}</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(len(indicators))
    for col, name in zip(cols, indicators):
        with col:
            st.markdown(_card_html(name, snapshots.get(name)), unsafe_allow_html=True)


def _plot_multi_line(series_dict, title, period_years=2):
    """Plot multiple series on one chart — Bloomberg style."""
    fig, ax = plt.subplots(figsize=(14, 3.6), facecolor=BG_BLACK)
    ax.set_facecolor(BG_BLACK)

    # Distinct colors for each line (Bloomberg-ish)
    colors = [ORANGE, "#00C853", "#29B6F6"]

    plotted_any = False
    for i, (label, series) in enumerate(series_dict.items()):
        if series.empty:
            continue
        # Trim to the requested window
        end   = series.index.max()
        start = end - __import__("pandas").DateOffset(years=period_years)
        subset = series.loc[series.index >= start]
        if subset.empty:
            continue
        ax.plot(subset.index, subset.values,
                color=colors[i % len(colors)],
                linewidth=1.4, label=label)
        plotted_any = True

    if not plotted_any:
        plt.close(fig)
        return None

    ax.set_title(title, color=ORANGE, fontsize=11, loc="left",
                 family="monospace", pad=12)
    ax.tick_params(colors=GREY_TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.grid(True, color=BORDER, linewidth=0.4, alpha=0.5)

    # Legend — match Bloomberg theme
    leg = ax.legend(loc="upper left", facecolor=BG_BLACK, edgecolor=BORDER,
                    labelcolor=GREY_TEXT, fontsize=9, framealpha=1)

    plt.tight_layout()
    return fig


def render():
    st.markdown(
        f"<p style='color:{GREY_TEXT};font-size:12px;margin:4px 0 16px;'>"
        f"Key US macroeconomic indicators. Source: Federal Reserve Economic Data (FRED)."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching macro data from FRED..."):
        snapshots = get_all_macro_snapshots()

    # ---------- GROUP 1: RATES ----------
    _render_group(
        "INTEREST RATES & MONETARY POLICY",
        ["Fed Funds Rate", "10Y Treasury", "2Y Treasury"],
        snapshots,
    )

    rates_series = {
        name: snapshots[name]["series"]
        for name in ["Fed Funds Rate", "10Y Treasury", "2Y Treasury"]
        if snapshots.get(name)
    }
    fig = _plot_multi_line(rates_series, "RATES — 2Y WINDOW", period_years=2)
    if fig:
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    # ---------- GROUP 2: INFLATION ----------
    _render_group(
        "INFLATION",
        ["CPI YoY", "Core CPI YoY", "PCE YoY"],
        snapshots,
    )

    inflation_series = {
        name: snapshots[name]["series"]
        for name in ["CPI YoY", "Core CPI YoY", "PCE YoY"]
        if snapshots.get(name)
    }
    fig = _plot_multi_line(inflation_series, "INFLATION — 5Y WINDOW", period_years=5)
    if fig:
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    # ---------- GROUP 3: LABOR & GROWTH ----------
    _render_group(
        "LABOR & GROWTH",
        ["Unemployment", "Nonfarm Payrolls", "GDP QoQ"],
        snapshots,
    )

    unemp_series = {"Unemployment": snapshots["Unemployment"]["series"]} \
                    if snapshots.get("Unemployment") else {}
    fig = _plot_multi_line(unemp_series, "UNEMPLOYMENT — 5Y WINDOW", period_years=5)
    if fig:
        st.pyplot(fig, width="stretch")
        plt.close(fig)