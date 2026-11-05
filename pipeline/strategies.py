"""Dividend and growth strategy filters plus composite scoring."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from fetch import StockSnapshot
from ratios import RatioResult

# Two-stage dividend model (Gordon model with a high-growth first stage).
REQUIRED_RETURN = 0.09  # k: annual shareholder hurdle used to discount dividends
HIGH_GROWTH_YEARS = 5  # stage 1: dividends grow at the recent 5-year CAGR
HIGH_GROWTH_CAP = 0.15  # stage 1 growth is clipped to 0-15%
TERMINAL_GROWTH = 0.03  # stage 2: long-run growth (about inflation), well below k


@dataclass
class ScoredPick:
    track: str
    snap: StockSnapshot
    ratios: RatioResult
    score: float
    metrics: dict[str, Any]


def _cagr(start: float, end: float, years: float) -> float | None:
    if start <= 0 or end <= 0 or years <= 0:
        return None
    return (end / start) ** (1.0 / years) - 1.0


def _complete_dividend_years(snap: StockSnapshot) -> list[tuple[int, float]]:
    years = list(snap.dividend_history_years)
    if not years:
        return []
    current_year = date.today().year
    if years[-1][0] == current_year:
        years = years[:-1]
    return years


def dividend_div_cagr(snap: StockSnapshot) -> float | None:
    years = _complete_dividend_years(snap)
    if len(years) < 5:
        return None
    recent = years[-1][1]
    older = years[-5][1]
    return _cagr(older, recent, 4.0)


def consecutive_dividend_years(snap: StockSnapshot, min_years: int = 5) -> bool:
    years = _complete_dividend_years(snap)
    if len(years) < min_years:
        return False
    tail = years[-min_years:]
    year_nums = [y for y, _ in tail]
    expected = list(range(year_nums[0], year_nums[0] + min_years))
    if year_nums != expected:
        return False
    amounts = [a for _, a in tail]
    for i in range(1, len(amounts)):
        if amounts[i] + 1e-12 < amounts[i - 1]:
            return False
    return True


def fcf_payout(snap: StockSnapshot) -> float | None:
    if not snap.free_cash_flow or snap.free_cash_flow <= 0:
        return None
    if not snap.dividend_rate or not snap.shares_outstanding:
        return None
    total_div = snap.dividend_rate * snap.shares_outstanding
    return total_div / snap.free_cash_flow


def interest_coverage(snap: StockSnapshot) -> float | None:
    if snap.operating_income is None:
        return None
    ie = snap.interest_expense
    if ie is None or ie == 0:
        return 999.0 if snap.operating_income > 0 else None
    return snap.operating_income / abs(ie)


def gordon_margin_of_safety(
    snap: StockSnapshot, div_cagr: float | None, k: float = REQUIRED_RETURN
) -> tuple[float | None, float | None]:
    """Two-stage dividend discount model.

    Stage 1: dividends grow at the recent CAGR (clipped to 0-15%) for
    HIGH_GROWTH_YEARS, each discounted at k. Stage 2: the Gordon model,
    P = D(n+1) / (k - g_terminal), discounted back n years.

    Works in units of price (D0 / price = yield), so the result is unit-free
    and listing-currency quirks cancel. Returns (fair value in local currency,
    margin of safety as fair / price - 1).
    """
    yld = snap.dividend_yield
    if yld is None or yld <= 0 or div_cagr is None:
        return None, None
    g1 = max(0.0, min(div_cagr, HIGH_GROWTH_CAP))
    n = HIGH_GROWTH_YEARS
    ratio = 0.0
    d = yld
    for t in range(1, n + 1):
        d *= 1.0 + g1
        ratio += d / (1.0 + k) ** t
    terminal = d * (1.0 + TERMINAL_GROWTH) / (k - TERMINAL_GROWTH)
    ratio += terminal / (1.0 + k) ** n
    fair = snap.price * ratio if snap.price else None
    return fair, ratio - 1.0


def peg(snap: StockSnapshot) -> float | None:
    """PEG = (P/E) / g, with g as forward EPS growth in percent; Yahoo's PEG as fallback."""
    pe = snap.trailing_pe
    g = snap.forward_eps_growth
    if pe is not None and g is not None and g > 0:
        return pe / (g * 100.0)
    return snap.peg_ratio


def valuation_metrics(snap: StockSnapshot) -> dict[str, Any]:
    return {"pe": snap.trailing_pe, "peg": peg(snap), "pb": snap.price_to_book}


def evaluate_dividend(snap: StockSnapshot, ratios: RatioResult) -> ScoredPick | None:
    if snap.price_usd is None or snap.price_usd <= 0:
        return None
    yld = snap.dividend_yield
    if yld is None or yld < 0.025 or yld > 0.075:
        return None
    if not consecutive_dividend_years(snap, 5):
        return None
    payout = fcf_payout(snap)
    if payout is None or payout < 0.25 or payout > 0.70:
        return None
    cov = interest_coverage(snap)
    if cov is None or cov < 3.5:
        return None
    if len(snap.operating_cashflow_years) < 3 or any(v <= 0 for v in snap.operating_cashflow_years[:3]):
        return None

    div_cagr = dividend_div_cagr(snap)
    score = 50.0
    score += min(20.0, max(0.0, (yld - 0.025) / 0.05 * 10))
    if div_cagr is not None:
        score += min(15.0, max(0.0, div_cagr * 100))
    if payout is not None:
        score += max(0.0, 10.0 - abs(payout - 0.45) * 30)
    if ratios.debt_to_mc is not None:
        score += max(0.0, (0.33 - ratios.debt_to_mc) / 0.33 * 10)
    fair, mos = gordon_margin_of_safety(snap, div_cagr)
    if mos is not None:
        # +10 at 30% or more below fair value, -10 at 30% or more above it
        score += max(-10.0, min(10.0, mos / 0.30 * 10))
    score = float(max(0.0, min(100.0, score)))

    return ScoredPick(
        track="dividend",
        snap=snap,
        ratios=ratios,
        score=score,
        metrics={
            "yield": yld,
            "divCagr5y": div_cagr,
            "fcfPayout": payout,
            "interestCoverage": cov,
            "gordonFairValue": fair,
            "marginOfSafety": mos,
            **valuation_metrics(snap),
        },
    )


def revenue_yoy(snap: StockSnapshot) -> float | None:
    if snap.revenue_growth is not None:
        return snap.revenue_growth
    if snap.revenue_ttm and snap.revenue_prior and snap.revenue_prior > 0:
        return snap.revenue_ttm / snap.revenue_prior - 1.0
    return None


def revenue_cagr_3y(snap: StockSnapshot) -> float | None:
    revs = snap.revenue_3y
    # Need 4 annual points for a true 3-year CAGR (revs[3] -> revs[0])
    if len(revs) < 4:
        return None
    return _cagr(revs[3], revs[0], 3.0)


def evaluate_growth(snap: StockSnapshot, ratios: RatioResult) -> ScoredPick | None:
    if snap.price_usd is None or snap.price_usd <= 0:
        return None
    yoy = revenue_yoy(snap)
    if yoy is None or yoy <= 0.15:
        return None
    cagr = revenue_cagr_3y(snap)
    if cagr is None or cagr <= 0.12:
        return None
    fwd = snap.forward_eps_growth
    if fwd is None or fwd <= 0.15:
        return None
    roic = snap.roic_3y
    if roic is None or roic <= 0.12:
        return None
    if snap.sma_200 is None or (snap.price is not None and snap.price < snap.sma_200):
        return None
    if snap.price_3m_ago is None or snap.price_3m_ago <= 0 or snap.price is None:
        return None
    rel_3m = snap.price / snap.price_3m_ago - 1.0
    if rel_3m <= 0:
        return None

    score = 50.0
    score += min(20.0, (yoy - 0.15) * 50)
    score += min(15.0, (cagr - 0.12) * 40)
    score += min(10.0, (fwd - 0.15) * 30)
    score += min(10.0, (roic - 0.12) * 40)
    score += min(5.0, rel_3m * 20)
    if ratios.debt_to_mc is not None:
        score += max(0.0, (0.33 - ratios.debt_to_mc) / 0.33 * 5)
    peg_v = peg(snap)
    if peg_v is not None:
        # +10 at PEG 0, 0 at PEG 2, down to -10 at PEG 4 or above
        score += max(-10.0, min(10.0, (2.0 - peg_v) * 5))
    score = float(max(0.0, min(100.0, score)))

    return ScoredPick(
        track="growth",
        snap=snap,
        ratios=ratios,
        score=score,
        metrics={
            "revGrowthTtm": yoy,
            "fwdEpsGrowth": fwd,
            "debtToMc": ratios.debt_to_mc,
            "roic": roic,
            "rel3m": rel_3m,
            **valuation_metrics(snap),
        },
    )
