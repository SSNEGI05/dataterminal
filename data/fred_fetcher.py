# file: data/fred_fetcher.py
# FRED API wrapper for US macro data.

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

from config import CACHE_MACRO

load_dotenv()
try:
    _FRED_KEY = st.secrets["FRED_API_KEY"]  # Streamlit Cloud
except (FileNotFoundError, KeyError):
    _FRED_KEY = os.getenv("FRED_API_KEY")   # local .env fallback



# 🔧 9 macro indicators — FRED series IDs
MACRO_SERIES = {
    # Interest rates
    "Fed Funds Rate":   {"id": "DFF",             "unit": "%",    "group": "rates"},
    "10Y Treasury":     {"id": "DGS10",           "unit": "%",    "group": "rates"},
    "2Y Treasury":      {"id": "DGS2",            "unit": "%",    "group": "rates"},
    # Inflation
    "CPI YoY":          {"id": "CPIAUCSL",        "unit": "%",    "group": "inflation"},
    "Core CPI YoY":     {"id": "CPILFESL",        "unit": "%",    "group": "inflation"},
    "PCE YoY":          {"id": "PCEPI",           "unit": "%",    "group": "inflation"},
    # Labor & growth
    "Unemployment":     {"id": "UNRATE",          "unit": "%",    "group": "labor"},
    "Nonfarm Payrolls": {"id": "PAYEMS",          "unit": "K",    "group": "labor"},
    "GDP QoQ":          {"id": "A191RL1Q225SBEA", "unit": "%",    "group": "labor"},
}


def _get_fred():
    if not _FRED_KEY:
        return None
    return Fred(api_key=_FRED_KEY)


@st.cache_data(ttl=CACHE_MACRO)
def get_macro_series(series_id, years=5):
    """Fetch one FRED series as a pandas Series."""
    fred = _get_fred()
    if fred is None:
        return pd.Series(dtype=float)
    try:
        end   = pd.Timestamp.today()
        start = end - pd.DateOffset(years=years)
        data  = fred.get_series(series_id, observation_start=start, observation_end=end)
        return data.dropna()
    except Exception as e:
        print(f"[fred] {series_id}: {e}")
        return pd.Series(dtype=float)


@st.cache_data(ttl=CACHE_MACRO)
def get_all_macro_snapshots():
    """
    For each of the 9 indicators: latest value + month-over-month change.
    For CPI/Core CPI/PCE: convert index levels to YoY % change.
    For Payrolls: convert absolute level to monthly change (in thousands).
    Returns dict keyed by indicator name.
    """
    results = {}

    for name, meta in MACRO_SERIES.items():
        series = get_macro_series(meta["id"], years=3)
        if series.empty:
            results[name] = None
            continue

        # Transform based on indicator type
        if name in ("CPI YoY", "Core CPI YoY", "PCE YoY"):
            # Convert index levels -> YoY % change
            yoy = series.pct_change(periods=12) * 100
            yoy = yoy.dropna()
            if yoy.empty:
                results[name] = None
                continue
            latest = float(yoy.iloc[-1])
            prev   = float(yoy.iloc[-2]) if len(yoy) > 1 else latest
            display_series = yoy

        elif name == "Nonfarm Payrolls":
            # Convert absolute jobs to monthly change in thousands
            change = series.diff().dropna()
            if change.empty:
                results[name] = None
                continue
            latest = float(change.iloc[-1])
            prev   = float(change.iloc[-2]) if len(change) > 1 else latest
            display_series = change

        else:
            # DFF, DGS10, DGS2, UNRATE, GDP — use as-is
            latest = float(series.iloc[-1])
            prev   = float(series.iloc[-2]) if len(series) > 1 else latest
            display_series = series

        results[name] = {
            "latest":  latest,
            "prev":    prev,
            "change":  latest - prev,
            "unit":    meta["unit"],
            "group":   meta["group"],
            "series":  display_series,
        }

    return results