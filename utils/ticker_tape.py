# file: utils/ticker_tape.py
# Scrolling ticker tape. Shows live prices + % change, loops horizontally.
# Called once from app.py at the top of every page.

import streamlit as st
import yfinance as yf
from config import (
    TICKER_TAPE_SYMBOLS, CACHE_LIVE_PRICES,
    BG_PANEL, ORANGE, GREEN_UP, RED_DOWN, BORDER, FONT_MONO,
)


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def fetch_ticker_data(symbols):
    """Fetch price + % change for each symbol. Cached for 5 min (CACHE_LIVE_PRICES)."""
    results = []

    # yfinance batch download — one API call for all symbols
    data = yf.download(
        tickers=" ".join(symbols),
        period="2d",             # 🔧 2 days so we can compute today vs yesterday
        interval="1d",
        progress=False,
        group_by="ticker",
        auto_adjust=True,
    )

    for sym in symbols:
        try:
            df = data[sym] if len(symbols) > 1 else data
            close = df["Close"].dropna()
            if len(close) < 2:
                continue
            price = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            pct   = ((price - prev) / prev) * 100
            results.append({"symbol": sym, "price": price, "pct": pct})
        except Exception:
            continue

    return results


def render_ticker_tape():
    """Inject the scrolling ticker tape HTML into the page."""
    data = fetch_ticker_data(TICKER_TAPE_SYMBOLS)

    if not data:
        st.markdown("<div style='color:gray;padding:6px;'>Ticker tape unavailable</div>",
                    unsafe_allow_html=True)
        return

    # Build one <span> per stock with color-coded % change
    items_html = ""
    for d in data:
        color = GREEN_UP if d["pct"] >= 0 else RED_DOWN
        sign  = "+" if d["pct"] >= 0 else ""
        items_html += (
            f'<span class="tape-item">'
            f'<span class="tape-sym">{d["symbol"]}</span> '
            f'<span class="tape-price">{d["price"]:.2f}</span> '
            f'<span style="color:{color};">{sign}{d["pct"]:.2f}%</span>'
            f'</span>'
        )

    # Doubled so the loop animation feels continuous (no visible jump)
    full_html = f"""
    <style>
    .tape-container {{
        background-color: {BG_PANEL};
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        overflow: hidden;
        white-space: nowrap;
        padding: 8px 0;
        font-family: {FONT_MONO};
        font-size: 13px;
    }}
    .tape-track {{
        display: inline-block;
        animation: scroll-tape 120s linear infinite;   /* 🔧 speed: lower = faster */
    }}
    .tape-item {{
        display: inline-block;
        margin: 0 28px;                                /* 🔧 gap between stocks */
        color: white;
    }}
    .tape-sym {{
        color: {ORANGE};
        font-weight: 500;
    }}
    .tape-price {{
        color: white;
    }}
    @keyframes scroll-tape {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    </style>
    <div class="tape-container">
        <div class="tape-track">{items_html}{items_html}</div>
    </div>
    """

    st.markdown(full_html, unsafe_allow_html=True)