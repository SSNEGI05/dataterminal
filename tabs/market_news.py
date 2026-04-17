# file: tabs/market_news.py
# Market news aggregator — combines RSS feeds from multiple sources.

import streamlit as st
from datetime import datetime
from data.news_feed import fetch_all_news
from config import ORANGE, BG_PANEL, BORDER, FONT_MONO, GREY_TEXT


def _time_ago(published):
    """Convert a datetime to 'Xm ago' / 'Xh ago' / 'Xd ago'."""
    if not published:
        return "—"
    delta = datetime.now() - published
    seconds = delta.total_seconds()
    if seconds < 60:
        return "now"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


def _build_news_html(items, max_items=40):      # 🔧 max headlines shown
    html = (
        f'<div style="background:{BG_PANEL};padding:10px 14px;border:1px solid {BORDER};'
        f'color:{GREY_TEXT};font-size:11px;letter-spacing:2px;font-family:{FONT_MONO};">'
        f'LATEST MARKET HEADLINES</div>'
    )

    if not items:
        html += (
            f'<div style="padding:14px;color:{GREY_TEXT};'
            f'border:1px solid {BORDER};border-top:none;">No news available</div>'
        )
        return html

    rows_html = ""
    for item in items[:max_items]:
        time_str = _time_ago(item["published"])
        title    = item["title"]
        source   = item["source"]
        link     = item["link"]

        rows_html += (
            f'<div style="padding:10px 14px;border-bottom:1px solid {BORDER};'
            f'font-family:{FONT_MONO};">'
            f'<div style="display:flex;justify-content:space-between;font-size:10px;'
            f'color:{GREY_TEXT};letter-spacing:1.5px;margin-bottom:4px;">'
            f'<span>{source.upper()}</span>'
            f'<span>{time_str}</span>'
            f'</div>'
            f'<a href="{link}" target="_blank" style="color:white;text-decoration:none;'
            f'font-size:14px;line-height:1.4;">'
            f'{title}'
            f'</a>'
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
        f"Aggregated from Yahoo Finance, MarketWatch, CNBC, Investing.com, Seeking Alpha. "
        f"Click any headline to read the full article."
        f"</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching latest news..."):
        items = fetch_all_news(limit_per_source=15)

    st.markdown(_build_news_html(items, max_items=40), unsafe_allow_html=True)