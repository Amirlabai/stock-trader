"""Dividend and growth strategy filters plus composite scoring."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from fetch import StockSnapshot
from ratios import RatioResult


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
        },
    )
