"""AAOIFI Tier 2 ratio screens and purification estimate."""
from __future__ import annotations

from dataclasses import dataclass

from fetch import StockSnapshot

RATIO_LIMIT = 0.33


@dataclass
class RatioResult:
    debt_to_mc: float | None
    cash_to_mc: float | None
    receivables_to_mc: float | None
    mc_basis: str
    interest_income_non_op: float | None
    purification_per_share: float | None
    passed: bool
    reason: str


def compute_ratios(snap: StockSnapshot) -> RatioResult:
    mc = snap.trailing_mc_24m or snap.market_cap
    if not mc or mc <= 0:
        return RatioResult(None, None, None, snap.mc_basis, None, None, False, "missing_market_cap")

    debt = snap.total_debt
    cash_raw = snap.cash
    sti = snap.short_investments or 0.0
    recv = snap.receivables

    if debt is None:
        return RatioResult(None, None, None, snap.mc_basis, snap.interest_income, None, False, "missing_debt")
    if cash_raw is None:
        return RatioResult(None, None, None, snap.mc_basis, snap.interest_income, None, False, "missing_cash")
    if recv is None:
        return RatioResult(None, None, None, snap.mc_basis, snap.interest_income, None, False, "missing_receivables")

    debt_r = debt / mc
    cash_r = (cash_raw + sti) / mc
    recv_r = recv / mc

    if debt_r >= RATIO_LIMIT:
        return RatioResult(debt_r, cash_r, recv_r, snap.mc_basis, snap.interest_income, None, False, "debt_screen")
    if cash_r >= RATIO_LIMIT:
        return RatioResult(debt_r, cash_r, recv_r, snap.mc_basis, snap.interest_income, None, False, "cash_screen")
    if recv_r >= RATIO_LIMIT:
        return RatioResult(debt_r, cash_r, recv_r, snap.mc_basis, snap.interest_income, None, False, "receivables_screen")

    purification = None
    shares = snap.shares_outstanding
    if snap.interest_income is not None and shares and shares > 0:
        purification = abs(snap.interest_income) / shares

    return RatioResult(
        debt_r,
        cash_r,
        recv_r,
        snap.mc_basis or "unknown",
        snap.interest_income,
        purification,
        True,
        "ok",
    )


def ratios_dict(r: RatioResult) -> dict:
    return {
        "debtToMarketCap": r.debt_to_mc,
        "cashToMarketCap": r.cash_to_mc,
        "receivablesToMarketCap": r.receivables_to_mc,
        "mcBasis": r.mc_basis if r.mc_basis in ("trailing_24m", "spot") else "unknown",
        "interestIncomeNonOp": r.interest_income_non_op,
        "purificationPerShare": r.purification_per_share,
    }
