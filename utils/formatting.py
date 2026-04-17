# file: utils/formatting.py
# Number formatting helpers. Turn raw numbers into Bloomberg-style display strings.

from config import GREEN_UP, RED_DOWN


def format_large(num):
    """Format big numbers: 1_250_000_000 -> '1.25B'."""
    if num is None or num == 0:
        return "—"

    abs_num = abs(num)
    sign = "-" if num < 0 else ""

    if abs_num >= 1_000_000_000_000:
        return f"{sign}{abs_num / 1_000_000_000_000:.2f}T"
    if abs_num >= 1_000_000_000:
        return f"{sign}{abs_num / 1_000_000_000:.2f}B"
    if abs_num >= 1_000_000:
        return f"{sign}{abs_num / 1_000_000:.2f}M"
    if abs_num >= 1_000:
        return f"{sign}{abs_num / 1_000:.2f}K"
    return f"{sign}{abs_num:.2f}"


def format_price(price):
    """Format price with 2 decimals and thousands separator: 1234.5 -> '1,234.50'."""
    if price is None:
        return "—"
    return f"{price:,.2f}"


def format_pct(pct):
    """Format percentage with sign: 2.45 -> '+2.45%', -1.2 -> '-1.20%'."""
    if pct is None:
        return "—"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def color_pct_html(pct):
    """Return HTML-colored % string. Green if up, red if down. For use in st.markdown."""
    if pct is None:
        return "<span>—</span>"
    color = GREEN_UP if pct >= 0 else RED_DOWN
    sign = "+" if pct >= 0 else ""
    return f'<span style="color:{color};">{sign}{pct:.2f}%</span>'


def format_volume(vol):
    """Format trading volume. 45_200_000 -> '45.20M'."""
    return format_large(vol)