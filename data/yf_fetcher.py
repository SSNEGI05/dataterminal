# file: data/yf_fetcher.py
# Central yfinance wrapper. Every tab imports from here.
# All calls are cached to avoid rate limits.

import streamlit as st
import yfinance as yf
import pandas as pd
from config import (
    CACHE_LIVE_PRICES, CACHE_SECTOR,
    MAJOR_INDICES, SECTOR_ETFS,
)


# ---------- 1. Historical prices for one symbol ----------
@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_history(symbol, period="1y", interval="1d"):
    """
    Fetch historical OHLCV data for one symbol.
    period:   1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max   🔧 tweakable
    interval: 1d, 1wk, 1mo                           🔧 tweakable
    Returns: pandas DataFrame with columns Open, High, Low, Close, Volume
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, auto_adjust=True)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"[get_history] error for {symbol}: {e}")
        return pd.DataFrame()


# ---------- 2. Latest quote for one symbol ----------
@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_quote(symbol):
    """
    Fetch latest price + % change vs previous close.
    Returns dict: {symbol, price, prev_close, change, pct_change, volume}
    """
    try:
        df = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=True)
        if len(df) < 2:
            return None

        price = float(df["Close"].iloc[-1])
        prev  = float(df["Close"].iloc[-2])
        vol   = int(df["Volume"].iloc[-1])

        return {
            "symbol":     symbol,
            "price":      price,
            "prev_close": prev,
            "change":     price - prev,
            "pct_change": ((price - prev) / prev) * 100,
            "volume":     vol,
        }
    except Exception as e:
        print(f"[get_quote] error for {symbol}: {e}")
        return None


# ---------- 3. Batch quotes for many symbols ----------
@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_batch_quotes(symbols):
    """
    Fetch quotes for multiple symbols in ONE api call.
    Much faster than calling get_quote() in a loop.
    Returns: list of dicts (same shape as get_quote)
    """
    if not symbols:
        return []

    results = []
    try:
        data = yf.download(
            tickers=" ".join(symbols),
            period="5d",
            interval="1d",
            progress=False,
            group_by="ticker",
            auto_adjust=True,
        )

        for sym in symbols:
            try:
                df = data[sym] if len(symbols) > 1 else data
                close = df["Close"].dropna()
                vol   = df["Volume"].dropna()
                if len(close) < 2:
                    continue

                price = float(close.iloc[-1])
                prev  = float(close.iloc[-2])

                results.append({
                    "symbol":     sym,
                    "price":      price,
                    "prev_close": prev,
                    "change":     price - prev,
                    "pct_change": ((price - prev) / prev) * 100,
                    "volume":     int(vol.iloc[-1]) if len(vol) > 0 else 0,
                })
            except Exception:
                continue

    except Exception as e:
        print(f"[get_batch_quotes] error: {e}")

    return results


# ---------- 5. Major indices snapshot (for Home tab) ----------
@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_major_indices():
    """
    Fetch all major US indices in one call.
    Uses MAJOR_INDICES from config.
    Returns: list of dicts with name + quote fields.
    """
    symbols = list(MAJOR_INDICES.values())
    quotes  = get_batch_quotes(symbols)

    # Map the cryptic symbol back to human-friendly name
    sym_to_name = {v: k for k, v in MAJOR_INDICES.items()}
    for q in quotes:
        q["name"] = sym_to_name.get(q["symbol"], q["symbol"])

    return quotes


# ---------- 6. Sector ETF snapshot (for Sector Data tab) ----------
@st.cache_data(ttl=CACHE_SECTOR)
def get_sector_quotes():
    """
    Fetch all 11 S&P sector ETFs in one call.
    Uses SECTOR_ETFS from config.
    Returns: list of dicts with sector name + quote fields.
    """
    symbols = list(SECTOR_ETFS.values())
    quotes  = get_batch_quotes(symbols)

    sym_to_sector = {v: k for k, v in SECTOR_ETFS.items()}
    for q in quotes:
        q["sector"] = sym_to_sector.get(q["symbol"], q["symbol"])

    return quotes


# ---------- 7. S&P 500 ticker list (scraped from Wikipedia) ----------
@st.cache_data(ttl=86400)   # 🔧 24 hours — list barely changes
def get_sp500_tickers():
    """
    Scrape S&P 500 constituent list from Wikipedia.
    Returns: DataFrame with columns Symbol, Security, GICS Sector
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        tables = pd.read_html(url)
        df = tables[0][["Symbol", "Security", "GICS Sector"]]
        # yfinance uses dashes, Wikipedia uses dots (BRK.B vs BRK-B)
        df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
        return df
    except Exception as e:
        print(f"[get_sp500_tickers] error: {e}")
        return pd.DataFrame(columns=["Symbol", "Security", "GICS Sector"])


# ---------- 8. Nasdaq 100 ticker list ----------
@st.cache_data(ttl=86400)
def get_nasdaq100_tickers():
    """Scrape Nasdaq 100 list from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    try:
        tables = pd.read_html(url)
        # Nasdaq 100 components table — usually index 4 on that page
        for t in tables:
            if "Symbol" in t.columns or "Ticker" in t.columns:
                col = "Symbol" if "Symbol" in t.columns else "Ticker"
                return t[[col]].rename(columns={col: "Symbol"})
        return pd.DataFrame(columns=["Symbol"])
    except Exception as e:
        print(f"[get_nasdaq100_tickers] error: {e}")
        return pd.DataFrame(columns=["Symbol"])