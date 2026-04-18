# file: data/yf_fetcher.py
# Central yfinance wrapper. Every tab imports from here.
# All calls are cached to avoid rate limits.

import time
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from io import StringIO

from config import (
    CACHE_LIVE_PRICES, CACHE_SECTOR,
    MAJOR_INDICES, SECTOR_ETFS,
)


_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

_BATCH_SIZE = 15   # 🔧 lower to 10 if cloud still rate-limits
_BATCH_DELAY = 1   # 🔧 increase to 2 if still failing


# ============================================================
# CORE FETCHERS
# ============================================================

@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_history(symbol, period="1y", interval="1d"):
    """Historical OHLCV for one symbol."""
    try:
        df = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=True)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"[get_history] {symbol}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_quote(symbol):
    """Latest price + % change vs previous close."""
    try:
        df = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=True)
        if len(df) < 2:
            return None
        price = float(df["Close"].iloc[-1])
        prev  = float(df["Close"].iloc[-2])
        vol   = int(df["Volume"].iloc[-1])
        return {
            "symbol": symbol, "price": price, "prev_close": prev,
            "change": price - prev,
            "pct_change": ((price - prev) / prev) * 100,
            "volume": vol,
        }
    except Exception as e:
        print(f"[get_quote] {symbol}: {e}")
        return None


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_batch_quotes(symbols):
    """Quotes for many symbols — batched to avoid cloud rate limits."""
    if not symbols:
        return []

    results = []

    for i in range(0, len(symbols), _BATCH_SIZE):
        batch = symbols[i:i + _BATCH_SIZE]
        try:
            data = yf.download(
                tickers=" ".join(batch),
                period="5d", interval="1d",
                progress=False, group_by="ticker", auto_adjust=True,
            )
            for sym in batch:
                try:
                    df = data[sym] if len(batch) > 1 else data
                    close = df["Close"].dropna()
                    vol   = df["Volume"].dropna()
                    if len(close) < 2:
                        continue
                    price = float(close.iloc[-1])
                    prev  = float(close.iloc[-2])
                    results.append({
                        "symbol": sym, "price": price, "prev_close": prev,
                        "change": price - prev,
                        "pct_change": ((price - prev) / prev) * 100,
                        "volume": int(vol.iloc[-1]) if len(vol) > 0 else 0,
                    })
                except Exception:
                    continue
        except Exception:
            continue

        if i + _BATCH_SIZE < len(symbols):
            time.sleep(_BATCH_DELAY)

    return results


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_batch_history(symbols, period="1y", interval="1d"):
    """Bulk history — batched to avoid cloud rate limits."""
    if not symbols:
        return {}

    results = {}

    for i in range(0, len(symbols), _BATCH_SIZE):
        batch = symbols[i:i + _BATCH_SIZE]
        try:
            data = yf.download(
                tickers=" ".join(batch),
                period=period, interval=interval,
                progress=False, group_by="ticker", auto_adjust=True,
            )
            for sym in batch:
                try:
                    df = data[sym] if len(batch) > 1 else data
                    if not df.empty:
                        results[sym] = df
                except Exception:
                    continue
        except Exception:
            continue

        if i + _BATCH_SIZE < len(symbols):
            time.sleep(_BATCH_DELAY)

    return results


# ============================================================
# INDEX & SECTOR SNAPSHOTS
# ============================================================

@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_major_indices():
    """Major US indices — for Home tab."""
    symbols = list(MAJOR_INDICES.values())
    quotes  = get_batch_quotes(symbols)
    sym_to_name = {v: k for k, v in MAJOR_INDICES.items()}
    for q in quotes:
        q["name"] = sym_to_name.get(q["symbol"], q["symbol"])
    return quotes


@st.cache_data(ttl=CACHE_SECTOR)
def get_sector_quotes():
    """11 S&P sector ETFs — for Sector Data tab."""
    symbols = list(SECTOR_ETFS.values())
    quotes  = get_batch_quotes(symbols)
    sym_to_sector = {v: k for k, v in SECTOR_ETFS.items()}
    for q in quotes:
        q["sector"] = sym_to_sector.get(q["symbol"], q["symbol"])
    return quotes


@st.cache_data(ttl=CACHE_SECTOR)
def get_sector_history(period="6mo"):
    """Historical prices for all 11 sector ETFs. For Sector Rotation tab."""
    symbols = list(SECTOR_ETFS.values())
    data    = get_batch_history(symbols, period=period)
    sym_to_sector = {v: k for k, v in SECTOR_ETFS.items()}
    return {sym_to_sector.get(s, s): df for s, df in data.items()}


# ============================================================
# TICKER LISTS (from Wikipedia)
# ============================================================

@st.cache_data(ttl=86400)
def get_sp500_tickers():
    """S&P 500 constituents from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        html = requests.get(url, headers=_BROWSER_HEADERS, timeout=10).text
        tables = pd.read_html(StringIO(html))
        df = tables[0][["Symbol", "Security", "GICS Sector"]]
        df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
        return df
    except Exception as e:
        print(f"[get_sp500_tickers] {e}")
        return pd.DataFrame(columns=["Symbol", "Security", "GICS Sector"])


@st.cache_data(ttl=86400)
def get_nasdaq100_tickers():
    """Nasdaq 100 constituents from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    try:
        html = requests.get(url, headers=_BROWSER_HEADERS, timeout=10).text
        tables = pd.read_html(StringIO(html))
        for t in tables:
            if "Symbol" in t.columns or "Ticker" in t.columns:
                col = "Symbol" if "Symbol" in t.columns else "Ticker"
                return t[[col]].rename(columns={col: "Symbol"})
        return pd.DataFrame(columns=["Symbol"])
    except Exception as e:
        print(f"[get_nasdaq100_tickers] {e}")
        return pd.DataFrame(columns=["Symbol"])


# ============================================================
# SCREENERS (used by specific tabs)
# ============================================================

@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_gainers_losers(universe="sp500", top_n=10):
    """Top gainers + losers for a universe."""
    if universe == "sp500":
        symbols = get_sp500_tickers()["Symbol"].tolist()
    elif universe == "nasdaq100":
        symbols = get_nasdaq100_tickers()["Symbol"].tolist()
    elif universe == "dow30":
        symbols = [
            "AAPL","AMGN","AXP","BA","CAT","CRM","CSCO","CVX","DIS","DOW",
            "GS","HD","HON","IBM","INTC","JNJ","JPM","KO","MCD","MMM",
            "MRK","MSFT","NKE","PG","TRV","UNH","V","VZ","WBA","WMT",
        ]
    else:
        return pd.DataFrame(), pd.DataFrame()

    if not symbols:
        return pd.DataFrame(), pd.DataFrame()
    quotes = get_batch_quotes(symbols)
    if not quotes:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(quotes).sort_values("pct_change", ascending=False)
    gainers = df.head(top_n).reset_index(drop=True)
    losers  = df.tail(top_n).sort_values("pct_change").reset_index(drop=True)
    return gainers, losers


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_52w_extremes(threshold_pct=2.0, top_n=15):
    """S&P 500 stocks near 52-week high and low."""
    symbols = get_sp500_tickers()["Symbol"].tolist()
    if not symbols:
        return pd.DataFrame(), pd.DataFrame()

    data = get_batch_history(symbols, period="1y")
    if not data:
        return pd.DataFrame(), pd.DataFrame()

    results = []
    for sym, df in data.items():
        try:
            close = df["Close"].dropna()
            if len(close) < 50:
                continue
            price    = float(close.iloc[-1])
            high_52w = float(close.max())
            low_52w  = float(close.min())
            results.append({
                "symbol": sym, "price": price,
                "high_52w": high_52w, "low_52w": low_52w,
                "pct_from_high": ((price - high_52w) / high_52w) * 100,
                "pct_from_low":  ((price - low_52w)  / low_52w)  * 100,
            })
        except Exception:
            continue

    if not results:
        return pd.DataFrame(), pd.DataFrame()

    df_all = pd.DataFrame(results)
    near_high = df_all[df_all["pct_from_high"] >= -threshold_pct] \
                 .sort_values("pct_from_high", ascending=False).head(top_n).reset_index(drop=True)
    near_low  = df_all[df_all["pct_from_low"]  <=  threshold_pct] \
                 .sort_values("pct_from_low",  ascending=True).head(top_n).reset_index(drop=True)
    return near_high, near_low


@st.cache_data(ttl=CACHE_LIVE_PRICES)
def get_all_time_highs(top_n=20):
    """
    S&P 500 stocks at or near all-time highs (using max available history).
    Uses 'max' period — may take longer on first load.
    """
    symbols = get_sp500_tickers()["Symbol"].tolist()
    if not symbols:
        return pd.DataFrame()

    data = get_batch_history(symbols, period="max")
    if not data:
        return pd.DataFrame()

    results = []
    for sym, df in data.items():
        try:
            close = df["Close"].dropna()
            if len(close) < 250:
                continue
            price   = float(close.iloc[-1])
            ath     = float(close.max())
            results.append({
                "symbol": sym, "price": price, "ath": ath,
                "pct_from_ath": ((price - ath) / ath) * 100,
            })
        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    df_all = pd.DataFrame(results).sort_values("pct_from_ath", ascending=False)
    return df_all.head(top_n).reset_index(drop=True)


# ============================================================
# SECTOR PERFORMANCE — multiple timeframes
# ============================================================

@st.cache_data(ttl=CACHE_SECTOR)
def get_sector_multi_timeframe():
    """
    For each of 11 sector ETFs: compute % change over 1D, 1W, 1M, 3M, 6M, 1Y, 3Y.
    Returns pandas DataFrame, one row per sector.
    """
    symbols = list(SECTOR_ETFS.values())
    data    = get_batch_history(symbols, period="5y")
    if not data:
        return pd.DataFrame()

    sym_to_sector = {v: k for k, v in SECTOR_ETFS.items()}

    timeframes = {
        "1D":   1,
        "1W":   5,
        "1M":   21,
        "3M":   63,
        "6M":   126,
        "1Y":   252,
        "3Y":   756,
    }

    rows = []
    for sym, df in data.items():
        try:
            close = df["Close"].dropna()
            if len(close) < 2:
                continue
            price = float(close.iloc[-1])

            row = {
                "sector": sym_to_sector.get(sym, sym),
                "symbol": sym,
                "price":  price,
            }

            for label, days in timeframes.items():
                if len(close) > days:
                    past  = float(close.iloc[-1 - days])
                    pct   = ((price - past) / past) * 100
                    row[label] = pct
                else:
                    row[label] = None

            rows.append(row)
        except Exception:
            continue

    return pd.DataFrame(rows)


# ============================================================
# SECTOR ROTATION — relative strength vs SPY + momentum
# ============================================================

@st.cache_data(ttl=CACHE_SECTOR)
def get_sector_rotation():
    """
    Rank sectors by relative strength vs SPY using 35/35/30 weighted blend.
    Returns DataFrame sorted strongest-to-weakest with absolute returns too.
    """
    symbols    = list(SECTOR_ETFS.values())
    benchmark  = "SPY"
    all_syms   = symbols + [benchmark]

    data = get_batch_history(all_syms, period="1y")
    if not data or benchmark not in data:
        return pd.DataFrame()

    spy_close = data[benchmark]["Close"].dropna()
    if len(spy_close) < 130:
        return pd.DataFrame()

    windows = {"1W": 5, "1M": 21, "3M": 63, "6M": 126}

    spy_ret = {}
    for label, days in windows.items():
        if len(spy_close) > days:
            spy_ret[label] = ((spy_close.iloc[-1] - spy_close.iloc[-1 - days])
                              / spy_close.iloc[-1 - days]) * 100
        else:
            spy_ret[label] = 0

    sym_to_sector = {v: k for k, v in SECTOR_ETFS.items()}
    rows = []

    for sym in symbols:
        if sym not in data:
            continue
        close = data[sym]["Close"].dropna()
        if len(close) < 130:
            continue

        abs_ret = {}
        rel_strength = {}
        for label, days in windows.items():
            if len(close) > days:
                sec_ret           = ((close.iloc[-1] - close.iloc[-1 - days])
                                     / close.iloc[-1 - days]) * 100
                abs_ret[label]    = sec_ret
                rel_strength[label] = sec_ret - spy_ret[label]
            else:
                abs_ret[label]    = None
                rel_strength[label] = None

        rs_score = ((rel_strength.get("1M") or 0) * 0.35
                  + (rel_strength.get("3M") or 0) * 0.35
                  + (rel_strength.get("6M") or 0) * 0.30)

        rows.append({
            "sector":    sym_to_sector.get(sym, sym),
            "symbol":    sym,
            "ret_1w":    abs_ret["1W"],
            "ret_1m":    abs_ret["1M"],
            "ret_3m":    abs_ret["3M"],
            "ret_6m":    abs_ret["6M"],
            "rs_score":  rs_score,
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("rs_score", ascending=False).reset_index(drop=True)
    return df