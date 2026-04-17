# file: data/news_feed.py
# Fetch financial news from RSS feeds. Free, no API key.

import streamlit as st
import feedparser
from datetime import datetime
from config import CACHE_NEWS


# 🔧 Add/remove feeds here. All free RSS.
NEWS_FEEDS = {
    "Yahoo Finance":   "https://finance.yahoo.com/news/rssindex",
    "MarketWatch":     "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "CNBC Markets":    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "Investing.com":   "https://www.investing.com/rss/news_25.rss",
    "Seeking Alpha":   "https://seekingalpha.com/market_currents.xml",
}


@st.cache_data(ttl=CACHE_NEWS)
def fetch_all_news(limit_per_source=15):
    """
    Pull latest headlines from every feed, merge, sort newest-first.
    Returns list of dicts: {source, title, link, published}
    """
    all_items = []

    for source, url in NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit_per_source]:
                # published_parsed is a time.struct_time — convert to datetime
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])

                all_items.append({
                    "source":    source,
                    "title":     entry.get("title", "").strip(),
                    "link":      entry.get("link", ""),
                    "published": published,
                })
        except Exception as e:
            print(f"[news_feed] {source}: {e}")
            continue

    # Sort by publish time (newest first). Items with no timestamp go to the end.
    all_items.sort(
        key=lambda x: x["published"] or datetime.min,
        reverse=True,
    )

    return all_items