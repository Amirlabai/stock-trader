"""Tier 1 sector / business-activity screen (fail closed)."""
from __future__ import annotations

BANNED_SECTOR_KEYWORDS = (
    "financial",
    "financials",
    "banks",
    "insurance",
    "capital markets",
)

BANNED_INDUSTRY_KEYWORDS = (
    "bank",
    "banks",
    "insurance",
    "asset management",
    "capital markets",
    "credit services",
    "mortgage",
    "financial data",
    "financial conglomerates",
    # ponytail: no bare "alcohol" (matches Non-Alcoholic)
    "beverages - brewers",
    "beverages - wineries",
    "beverages - distillers",
    "brewer",
    "distiller",
    "wine",
    "tobacco",
    "gambling",
    "casino",
    "resorts & casinos",
    "adult",
    "aerospace & defense",
    "defense",
    "weapons",
    "meat packing",
    "meat products",
    "pork",
)

TICKER_DENYLIST = {
    "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "BLK", "BX", "KKR",
    "MET", "PRU", "AIG", "TRV", "ALL", "PGR", "CB", "AFL", "SCHW", "TROW",
    "PYPL", "COIN", "HOOD", "PM", "MO", "BTI", "BATS.L", "LMT", "RTX", "NOC",
    "GD", "BA", "MGM", "WYNN", "LVS", "CZR", "DKNG", "PENN", "BUD", "DEO",
    "DGE.L", "STZ", "TAP", "SAM", "LLOY.L", "HSBA.L", "CBA.AX", "ALV.DE",
}

HARAM_REVENUE_LIMIT = 0.05


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(k in text for k in keywords)


def passes_tier1(
    ticker: str,
    sector: str | None,
    industry: str | None,
    haram_revenue_pct: float | None = None,
) -> tuple[bool, str]:
    """Return (pass, reason). Fail closed on missing activity labels."""
    t = ticker.upper()
    if t in TICKER_DENYLIST:
        return False, "ticker_denylist"

    sector_l = (sector or "").strip().lower()
    industry_l = (industry or "").strip().lower()
    if not sector_l or not industry_l:
        return False, "missing_activity_data"

    if _contains_any(sector_l, BANNED_SECTOR_KEYWORDS):
        return False, "banned_sector"

    if _contains_any(industry_l, BANNED_INDUSTRY_KEYWORDS):
        return False, "banned_industry"

    combined = f"{sector_l} {industry_l}"
    if "aerospace & defense" in industry_l or " defense" in combined:
        return False, "banned_defense"

    if haram_revenue_pct is not None and haram_revenue_pct >= HARAM_REVENUE_LIMIT:
        return False, "haram_revenue"

    return True, "ok"
