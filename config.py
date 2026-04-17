# file: config.py
# Central settings for DataTerminal — colors, tickers, constants.
# Every other file imports from here. Change a value here, whole app updates.

# ---------- BLOOMBERG COLOR PALETTE ----------
BG_BLACK      = "#000000"      # 🔧 change: main background
BG_PANEL      = "#0A0A0A"      # 🔧 change: card/panel background
ORANGE        = "#FF8C00"      # 🔧 change: primary accent (headings, labels)
ORANGE_DIM    = "#8B5A00"      # 🔧 change: secondary/muted orange
WHITE         = "#FFFFFF"      # 🔧 change: main text
GREY_TEXT     = "#808080"      # 🔧 change: secondary text
GREEN_UP      = "#00C853"      # 🔧 change: positive % / gainers
RED_DOWN      = "#FF1744"      # 🔧 change: negative % / losers
BORDER        = "#1A1A1A"      # 🔧 change: thin dividers

# ---------- FONTS ----------
FONT_MONO = "Consolas, 'Courier New', monospace"   # 🔧 change: terminal font

# ---------- APP METADATA ----------
APP_NAME    = "DATATERMINAL"                       # 🔧 change: shown in header
APP_TAGLINE = "US Market"    # 🔧 change: shown under name

# ---------- TICKER TAPE (scrolling bar at top) ----------
TICKER_TAPE_SYMBOLS = [
    "SPY", "QQQ", "DIA", "IWM",           # major indices ETFs
    "AAPL", "MSFT", "NVDA", "GOOGL",      # mega-cap tech
    "AMZN", "META", "TSLA", "AVGO",
    "JPM", "V", "MA", "BAC",              # finance
    "XOM", "CVX",                         # energy
    "UNH", "JNJ", "LLY",                  # healthcare
    "WMT", "COST",                        # retail
]  # 🔧 change: add/remove symbols from the scrolling tape

# ---------- DEFAULT TIMEFRAMES ----------
DEFAULT_CHART_PERIOD   = "1y"     # 🔧 change: 1mo, 3mo, 6mo, 1y, 2y, 5y, max
DEFAULT_CHART_INTERVAL = "1d"     # 🔧 change: 1d, 1wk, 1mo

# ---------- CACHE DURATIONS (in seconds) ----------
CACHE_LIVE_PRICES = 300      # 🔧 change: 5 min — Home/Gainers data freshness
CACHE_COMPANY     = 3600     # 🔧 change: 1 hr — company info
CACHE_NEWS        = 600      # 🔧 change: 10 min — RSS feeds
CACHE_MACRO       = 86400    # 🔧 change: 24 hr — FRED data (monthly releases)
CACHE_SECTOR      = 900      # 🔧 change: 15 min — sector performance

# ---------- MARKET INDICES (for Home tab) ----------
MAJOR_INDICES = {
    "S&P 500":    "^GSPC",
    "Nasdaq 100": "^NDX",
    "Dow 30":     "^DJI",
    "Russell 2k": "^RUT",
    "VIX":        "^VIX",
}  # 🔧 change: which indices show on Home

# ---------- 11 S&P SECTOR ETFs ----------
SECTOR_ETFS = {
    "Technology":           "XLK",
    "Financials":           "XLF",
    "Healthcare":           "XLV",
    "Consumer Discretionary": "XLY",
    "Consumer Staples":     "XLP",
    "Energy":               "XLE",
    "Industrials":          "XLI",
    "Materials":            "XLB",
    "Utilities":            "XLU",
    "Real Estate":          "XLRE",
    "Communication":        "XLC",
}  # 🔧 change: sector mapping — used in Sector Data + Rotation tabs