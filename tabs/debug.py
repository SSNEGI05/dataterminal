# file: tabs/debug.py
# Temporary debug tab — delete after fixing

import streamlit as st
import yfinance as yf
import pandas as pd

def render():
    st.subheader("Debug — yfinance test")
    
    # Test 1: single stock
    st.write("**Test 1: Single stock (AAPL)**")
    try:
        df = yf.Ticker("AAPL").history(period="5d")
        st.write(f"Rows returned: {len(df)}")
        st.dataframe(df.tail())
    except Exception as e:
        st.error(f"Single stock failed: {e}")
    
    # Test 2: small batch
    st.write("**Test 2: Batch download (5 stocks)**")
    try:
        data = yf.download("AAPL MSFT GOOGL AMZN META", period="5d", progress=False)
        st.write(f"Shape: {data.shape}")
        st.dataframe(data.tail())
    except Exception as e:
        st.error(f"Batch download failed: {e}")
    
    # Test 3: Wikipedia scrape
    st.write("**Test 3: S&P 500 ticker list from Wikipedia**")
    try:
        from data.yf_fetcher import get_sp500_tickers
        tickers = get_sp500_tickers()
        st.write(f"Tickers found: {len(tickers)}")
        st.dataframe(tickers.head())
    except Exception as e:
        st.error(f"Wikipedia scrape failed: {e}")