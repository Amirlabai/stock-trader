"""Fetch fundamentals and prices via yfinance."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

import numpy as np
import pandas as pd
import yfinance as yf

T = TypeVar("T")

# Cache FX -> USD for one process run
_FX_TO_USD: dict[str, float] = {"USD": 1.0}
LAST_SKIP_REASON: str | None = None


class NonRetryableFetchError(RuntimeError):
    """Do not retry (e.g. missing sector/industry)."""


@dataclass
class StockSnapshot:
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    region: str = "UNK"
    currency: str = "USD"
    price: float | None = None
    price_usd: float | None = None
    market_cap: float | None = None
    trailing_mc_24m: float | None = None
    mc_basis: str = "unknown"
    total_debt: float | None = None
    cash: float | None = None
    short_investments: float | None = None
    receivables: float | None = None
    operating_income: float | None = None
    interest_expense: float | None = None
    interest_income: float | None = None
    free_cash_flow: float | None = None
    operating_cashflow_years: list[float] = field(default_factory=list)
    dividend_yield: float | None = None
    dividend_rate: float | None = None
    payout_ratio: float | None = None
    dividend_history_years: list[tuple[int, float]] = field(default_factory=list)
    revenue_ttm: float | None = None
    revenue_prior: float | None = None
    revenue_3y: list[float] = field(default_factory=list)
    earnings_growth: float | None = None  # trailing
    forward_eps_growth: float | None = None
    revenue_growth: float | None = None
    return_on_equity: float | None = None
    invested_capital: float | None = None
    nopat: float | None = None
    nopat_years: list[float] = field(default_factory=list)
    invested_capital_years: list[float] = field(default_factory=list)
    roic_3y: float | None = None
    sma_200: float | None = None
    price_3m_ago: float | None = None
    shares_outstanding: float | None = None
    haram_revenue_pct: float | None = None
    raw_info: dict[str, Any] = field(default_factory=dict)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(f) or np.isinf(f):
        return None
    return f


def with_backoff(fn: Callable[[], T], *, attempts: int = 3, base_sleep: float = 1.0, label: str = "") -> T | None:
    global LAST_SKIP_REASON
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except NonRetryableFetchError as exc:
            LAST_SKIP_REASON = str(exc)
            print(f"yfinance skip {label}: {exc}", flush=True)
            return None
        except Exception as exc:  # noqa: BLE001
            last = exc
            msg = str(exc).lower()
            wait = base_sleep * (2**i)
            if "429" in msg or "rate" in msg:
                wait = max(wait, 5.0 * (i + 1))
            print(f"yfinance retry {i + 1}/{attempts} {label}: {exc}", flush=True)
            time.sleep(wait)
    print(f"yfinance failed {label}: {last}", flush=True)
    return None


def _latest_balance_value(bs: pd.DataFrame, keys: tuple[str, ...]) -> float | None:
    if bs is None or bs.empty:
        return None
    for key in keys:
        if key in bs.index:
            series = bs.loc[key].dropna()
            if not series.empty:
                return _safe_float(series.iloc[0])
    return None


def _balance_series(bs: pd.DataFrame, keys: tuple[str, ...], n: int = 3) -> list[float]:
    if bs is None or bs.empty:
        return []
    for key in keys:
        if key in bs.index:
            series = bs.loc[key].dropna()
            vals = [_safe_float(v) for v in series.tolist()[:n]]
            return [v for v in vals if v is not None]
    return []


def _cashflow_series(cf: pd.DataFrame, keys: tuple[str, ...], n: int = 3) -> list[float]:
    if cf is None or cf.empty:
        return []
    for key in keys:
        if key in cf.index:
            series = cf.loc[key].dropna()
            vals = [_safe_float(v) for v in series.tolist()[:n]]
            return [v for v in vals if v is not None]
    return []


def _income_series(inc: pd.DataFrame, keys: tuple[str, ...], n: int = 4) -> list[float]:
    if inc is None or inc.empty:
        return []
    for key in keys:
        if key in inc.index:
            series = inc.loc[key].dropna()
            vals = [_safe_float(v) for v in series.tolist()[:n]]
            return [v for v in vals if v is not None]
    return []


def _trailing_market_cap(hist: pd.DataFrame, shares: float | None) -> tuple[float | None, str]:
    if hist is None or hist.empty or shares is None or shares <= 0:
        return None, "unknown"
    closes = hist["Close"].dropna()
    if closes.empty:
        return None, "unknown"
    window = closes.tail(min(len(closes), 504))
    avg_price = float(window.mean())
    basis = "trailing_24m" if len(window) >= 200 else "spot"
    return avg_price * shares, basis


def fx_to_usd(currency: str | None) -> float | None:
    """Return multiplier to convert 1 unit of currency into USD."""
    if not currency:
        return None
    c = currency.strip()
    # Yahoo uses GBp for pence
    if c == "GBp":
        gbp = fx_to_usd("GBP")
        return (gbp / 100.0) if gbp else None
    c = c.upper()
    if c in _FX_TO_USD:
        return _FX_TO_USD[c]
    if c == "USD":
        _FX_TO_USD[c] = 1.0
        return 1.0

    def _load() -> float:
        pair = f"{c}USD=X"
        t = yf.Ticker(pair)
        hist = t.history(period="5d")
        if hist is not None and not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
        info = t.info or {}
        px = info.get("regularMarketPrice") or info.get("previousClose")
        if px is None:
            raise RuntimeError(f"no fx for {pair}")
        return float(px)

    rate = with_backoff(_load, attempts=3, label=f"fx:{c}")
    if rate is None or rate <= 0:
        return None
    _FX_TO_USD[c] = rate
    return rate


def to_usd(amount: float | None, currency: str | None) -> float | None:
    if amount is None:
        return None
    mult = fx_to_usd(currency or "USD")
    if mult is None:
        return None
    return amount * mult


def fetch_snapshot(ticker: str, region: str, display_name: str, sleep_s: float = 0.35) -> StockSnapshot | None:
    global LAST_SKIP_REASON
    LAST_SKIP_REASON = None
    time.sleep(sleep_s)

    def _build() -> StockSnapshot:
        t = yf.Ticker(ticker)
        info: dict[str, Any] = {}
        try:
            info = t.info or {}
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"info failed: {exc}") from exc

        sector = info.get("sector")
        industry = info.get("industry")
        if not sector or not industry:
            raise NonRetryableFetchError("missing_activity_data")

        currency = (info.get("currency") or "USD").strip()
        price_local = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))

        snap = StockSnapshot(
            ticker=ticker,
            name=display_name or info.get("shortName") or info.get("longName") or ticker,
            sector=sector,
            industry=industry,
            region=region,
            currency=currency,
            price=price_local,
            # Prefer Yahoo marketCap (usually already consistent); still convert below
            market_cap=_safe_float(info.get("marketCap")),
            dividend_yield=_safe_float(info.get("dividendYield")),
            dividend_rate=_safe_float(info.get("dividendRate")),
            payout_ratio=_safe_float(info.get("payoutRatio")),
            revenue_growth=_safe_float(info.get("revenueGrowth")),
            return_on_equity=_safe_float(info.get("returnOnEquity")),
            shares_outstanding=_safe_float(info.get("sharesOutstanding")),
            free_cash_flow=_safe_float(info.get("freeCashflow")),
            operating_income=_safe_float(info.get("operatingIncome") or info.get("ebit")),
            interest_expense=_safe_float(info.get("interestExpense")),
            # Debt filled from BS below; ignore info.totalDebt here (0 is ambiguous)
            raw_info={k: info.get(k) for k in ("sector", "industry", "quoteType", "currency") if k in info},
        )

        snap.earnings_growth = _safe_float(
            info.get("earningsGrowth") or info.get("earningsQuarterlyGrowth")
        )
        trail_eps = _safe_float(info.get("trailingEps"))
        fwd_eps = _safe_float(info.get("forwardEps"))
        # Avoid blow-ups when trailing EPS is a few cents
        if trail_eps is not None and abs(trail_eps) >= 0.50 and fwd_eps is not None:
            g = fwd_eps / trail_eps - 1.0
            snap.forward_eps_growth = max(-0.99, min(g, 5.0))
        else:
            snap.forward_eps_growth = None

        if snap.dividend_yield is not None and snap.dividend_yield > 1:
            snap.dividend_yield = snap.dividend_yield / 100.0

        bs = t.balance_sheet
        # Prefer BS Total Debt; info.totalDebt of 0 must not block BS
        bs_debt = _latest_balance_value(bs, ("Total Debt",))
        info_debt = _safe_float(info.get("totalDebt"))
        if bs_debt is not None:
            snap.total_debt = bs_debt
        elif info_debt is not None and info_debt > 0:
            snap.total_debt = info_debt
        else:
            snap.total_debt = None
        # CCE only; STI added once in ratios
        snap.cash = _latest_balance_value(bs, ("Cash And Cash Equivalents", "Cash"))
        snap.short_investments = _latest_balance_value(
            bs, ("Other Short Term Investments", "Short Term Investments")
        )
        snap.receivables = _latest_balance_value(
            bs, ("Receivables", "Net Receivables", "Accounts Receivable")
        )

        equity_years = _balance_series(
            bs, ("Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"), n=3
        )
        debt_years = _balance_series(bs, ("Total Debt",), n=3)
        cash_years = _balance_series(bs, ("Cash And Cash Equivalents", "Cash"), n=3)

        inc = t.income_stmt
        if inc is None or inc.empty:
            inc = t.financials
        revs = _income_series(inc, ("Total Revenue", "Operating Revenue"), n=4)
        snap.revenue_3y = revs
        if len(revs) >= 1:
            snap.revenue_ttm = revs[0]
        if len(revs) >= 2:
            snap.revenue_prior = revs[1]

        oi_years = _income_series(inc, ("Operating Income", "EBIT"), n=3)
        if oi_years:
            snap.operating_income = oi_years[0]
        ie = _income_series(inc, ("Interest Expense", "Interest Expense Non Operating"), n=1)
        if ie:
            snap.interest_expense = abs(ie[0]) if ie[0] is not None else None
        ii = _income_series(inc, ("Interest Income", "Interest Income Non Operating"), n=1)
        if ii and ii[0] is not None:
            snap.interest_income = abs(ii[0])

        # ponytail: pre-tax ROIC (EBIT/IC); no fake 21% tax across jurisdictions
        nopat_years = list(oi_years)
        snap.nopat_years = nopat_years
        if nopat_years:
            snap.nopat = nopat_years[0]

        ic_years: list[float] = []
        for i in range(len(equity_years)):
            eq = equity_years[i]
            d = debt_years[i] if i < len(debt_years) else (snap.total_debt or 0.0)
            c = cash_years[i] if i < len(cash_years) else (snap.cash or 0.0)
            ic_years.append(eq + (d or 0.0) - (c or 0.0))
        snap.invested_capital_years = ic_years
        if ic_years:
            snap.invested_capital = ic_years[0]

        pairs = []
        for i in range(min(len(nopat_years), len(ic_years))):
            if ic_years[i] and ic_years[i] > 0:
                pairs.append(nopat_years[i] / ic_years[i])
        if len(pairs) >= 3:
            snap.roic_3y = sum(pairs[:3]) / 3.0
        else:
            snap.roic_3y = None

        cf = t.cashflow
        ocf = _cashflow_series(
            cf,
            (
                "Operating Cash Flow",
                "Total Cash From Operating Activities",
                "Cash Flow From Continuing Operating Activities",
            ),
            n=3,
        )
        snap.operating_cashflow_years = ocf
        fcf_vals = _cashflow_series(cf, ("Free Cash Flow",), n=1)
        if fcf_vals:
            snap.free_cash_flow = fcf_vals[0]

        hist = t.history(period="2y", auto_adjust=True)
        if hist is not None and not hist.empty:
            if snap.price is None:
                snap.price = _safe_float(hist["Close"].iloc[-1])
            if len(hist) >= 200:
                snap.sma_200 = _safe_float(hist["Close"].tail(200).mean())
            if len(hist) >= 63:
                snap.price_3m_ago = _safe_float(hist["Close"].iloc[-63])
            shares = snap.shares_outstanding
            # Only infer shares when price and marketCap share listing currency (USD path)
            if (
                shares is None
                and snap.market_cap
                and snap.price
                and currency in ("USD", "usd")
            ):
                shares = snap.market_cap / snap.price
                snap.shares_outstanding = shares
            trailing, basis = _trailing_market_cap(hist, shares)
            if trailing:
                snap.trailing_mc_24m = trailing
                snap.mc_basis = basis
            elif snap.market_cap:
                snap.trailing_mc_24m = snap.market_cap
                snap.mc_basis = "spot"
        elif snap.market_cap:
            snap.trailing_mc_24m = snap.market_cap
            snap.mc_basis = "spot"

        divs = t.dividends
        if divs is not None and not divs.empty:
            by_year: dict[int, float] = {}
            for ts, amt in divs.items():
                year = int(pd.Timestamp(ts).year)
                by_year[year] = by_year.get(year, 0.0) + float(amt)
            snap.dividend_history_years = sorted(by_year.items())

        # Convert monetary fields to USD for ratios / purification / paper ledger
        fx = fx_to_usd(currency)
        if fx is None:
            raise NonRetryableFetchError("fx_unavailable")

        snap.price_usd = (snap.price * fx) if snap.price is not None else None
        # Convert local-currency fundamentals; Yahoo marketCap for USD listings stays as-is
        if currency not in ("USD", "usd"):
            if snap.market_cap is not None:
                snap.market_cap = snap.market_cap * fx
        if snap.trailing_mc_24m is not None:
            snap.trailing_mc_24m = snap.trailing_mc_24m * fx
        if snap.total_debt is not None:
            snap.total_debt = snap.total_debt * fx
        if snap.cash is not None:
            snap.cash = snap.cash * fx
        if snap.short_investments is not None:
            snap.short_investments = snap.short_investments * fx
        if snap.receivables is not None:
            snap.receivables = snap.receivables * fx
        if snap.interest_income is not None:
            snap.interest_income = snap.interest_income * fx
        if snap.interest_expense is not None:
            snap.interest_expense = snap.interest_expense * fx
        if snap.operating_income is not None:
            snap.operating_income = snap.operating_income * fx
        if snap.free_cash_flow is not None:
            snap.free_cash_flow = snap.free_cash_flow * fx
        if snap.dividend_rate is not None:
            snap.dividend_rate = snap.dividend_rate * fx
        snap.operating_cashflow_years = [v * fx for v in snap.operating_cashflow_years]
        if snap.invested_capital is not None:
            snap.invested_capital = snap.invested_capital * fx
        snap.invested_capital_years = [v * fx for v in snap.invested_capital_years]
        snap.nopat_years = [v * fx for v in snap.nopat_years]
        if snap.nopat is not None:
            snap.nopat = snap.nopat * fx
        pairs = []
        for i in range(min(len(snap.nopat_years), len(snap.invested_capital_years))):
            ic = snap.invested_capital_years[i]
            if ic and ic > 0:
                pairs.append(snap.nopat_years[i] / ic)
        if len(pairs) >= 3:
            snap.roic_3y = sum(pairs[:3]) / 3.0

        return snap

    return with_backoff(_build, attempts=3, base_sleep=1.0, label=ticker)
