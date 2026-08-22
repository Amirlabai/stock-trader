"""Shared paper portfolio ledger: daily buys, mark-to-market, dividends + DRIP."""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
DEFAULT_PICKS = ROOT.parent / "apps" / "web" / "public" / "data" / "daily-picks.json"
DEFAULT_LEDGER = ROOT.parent / "apps" / "web" / "public" / "data" / "paper-portfolio.json"


def empty_ledger(buy_amount: float = 100.0, as_of: str | None = None) -> dict[str, Any]:
    day = as_of or date.today().isoformat()
    return {
        "asOf": day,
        "buyAmountUsd": buy_amount,
        "summary": {
            "cashInvested": 0.0,
            "dividendsReinvested": 0.0,
            "totalCostBasis": 0.0,
            "currentValue": 0.0,
            "unrealizedPnl": 0.0,
            "returnPct": None,
            "positionCount": 0,
            "dividendEventCount": 0,
        },
        "positions": [],
        "lots": [],
        "dividendEvents": [],
        "lastBuyAsOf": None,
        "lastDividendCheckAsOf": None,
    }


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_ledger()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("lots", [])
    data.setdefault("dividendEvents", [])
    data.setdefault("positions", [])
    data.setdefault("lastBuyAsOf", None)
    data.setdefault("lastDividendCheckAsOf", None)
    return data


def _pick_rows(picks: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per ticker per day; prefer dividend track if in both."""
    by_ticker: dict[str, dict[str, Any]] = {}
    for p in picks.get("dividendPicks") or []:
        t = p.get("ticker")
        if t:
            by_ticker[t] = {**p, "track": "dividend"}
    for p in picks.get("growthPicks") or []:
        t = p.get("ticker")
        if t and t not in by_ticker:
            by_ticker[t] = {**p, "track": "growth"}
    return list(by_ticker.values())


def apply_daily_buys(ledger: dict[str, Any], picks: dict[str, Any]) -> bool:
    """Append pick lots for picks.asOf if not already applied. Returns True if changed."""
    as_of = picks.get("asOf")
    if not as_of:
        return False
    if ledger.get("lastBuyAsOf") == as_of:
        return False

    buy_amount = float(picks.get("buyAmountUsd") or ledger.get("buyAmountUsd") or 100)
    ledger["buyAmountUsd"] = buy_amount
    changed = False

    for p in _pick_rows(picks):
        ticker = p.get("ticker")
        # Prices in daily-picks are USD after FX conversion in the screener
        price = p.get("price")
        if not ticker or price is None or price <= 0:
            continue
        shares = buy_amount / float(price)
        ledger["lots"].append(
            {
                "asOf": as_of,
                "ticker": ticker,
                "name": p.get("name") or ticker,
                "source": "pick",
                "shares": shares,
                "price": float(price),
                "costUsd": buy_amount,
                "track": p.get("track"),
                "currency": p.get("currency") or "USD",
            }
        )
        changed = True

    if changed or not _pick_rows(picks):
        ledger["lastBuyAsOf"] = as_of
        ledger["asOf"] = as_of
        return True
    return False


def _shares_before(lots: list[dict[str, Any]], ticker: str, before_as_of: str) -> float:
    total = 0.0
    for lot in lots:
        if lot.get("ticker") != ticker:
            continue
        if lot.get("asOf", "") < before_as_of:
            total += float(lot.get("shares") or 0)
    return total


def _close_on_or_before(hist: pd.DataFrame, day: str, fallback: float | None) -> float | None:
    if hist is None or hist.empty:
        return fallback
    closes = hist["Close"].dropna()
    if closes.empty:
        return fallback
    # Normalize index to date strings
    target = pd.Timestamp(day).tz_localize(None)
    idx = closes.index.tz_localize(None) if closes.index.tz is not None else closes.index
    closes = closes.copy()
    closes.index = idx
    eligible = closes[closes.index <= target]
    if eligible.empty:
        return float(closes.iloc[0]) if fallback is None else fallback
    return float(eligible.iloc[-1])


def apply_dividends_and_drip(
    ledger: dict[str, Any],
    sleep_s: float = 0.2,
) -> None:
    """Scan dividends since last check / first buy; reinvest (DRIP)."""
    lots: list[dict[str, Any]] = list(ledger.get("lots") or [])
    if not lots:
        ledger["lastDividendCheckAsOf"] = ledger.get("asOf") or date.today().isoformat()
        return

    tickers = sorted({lot["ticker"] for lot in lots})
    # Earliest buy per ticker
    first_buy: dict[str, str] = {}
    for lot in lots:
        if lot.get("source") != "pick":
            continue
        t = lot["ticker"]
        as_of = lot["asOf"]
        if t not in first_buy or as_of < first_buy[t]:
            first_buy[t] = as_of

    last_check = ledger.get("lastDividendCheckAsOf")
    events: list[dict[str, Any]] = list(ledger.get("dividendEvents") or [])
    seen = {(e.get("asOf"), e.get("ticker"), round(float(e.get("amountPerShare") or 0), 8)) for e in events}

    today = date.today().isoformat()

    for ticker in tickers:
        start = first_buy.get(ticker)
        if not start:
            continue
        # Only look at dividends on/after first buy; skip already-processed window start
        query_start = start
        if last_check and last_check > start:
            # Re-scan a short overlap window is OK; dedupe via seen set
            query_start = last_check

        time.sleep(sleep_s)
        try:
            t = yf.Ticker(ticker)
            divs = t.dividends
            hist = t.history(start=query_start, auto_adjust=False)
        except Exception:
            continue

        if divs is None or len(divs) == 0:
            continue

        name = next((lot["name"] for lot in lots if lot["ticker"] == ticker), ticker)
        currency = next(
            (lot.get("currency") for lot in lots if lot["ticker"] == ticker and lot.get("currency")),
            "USD",
        )

        from fetch import to_usd

        for ts, amount in divs.items():
            try:
                day = pd.Timestamp(ts).tz_localize(None).date().isoformat()
            except Exception:
                continue
            if day < start:
                continue
            if day > today:
                continue
            amt_local = float(amount)
            if amt_local <= 0:
                continue
            key = (day, ticker, round(amt_local, 8))
            if key in seen:
                continue

            shares_held = _shares_before(lots, ticker, day)
            if shares_held <= 0:
                continue

            price_local = _close_on_or_before(hist, day, None)
            if price_local is None or price_local <= 0:
                try:
                    info_price = t.fast_info.last_price  # type: ignore[attr-defined]
                    price_local = float(info_price) if info_price else None
                except Exception:
                    price_local = None
            if price_local is None or price_local <= 0:
                continue

            amt_usd = to_usd(amt_local, currency)
            price_usd = to_usd(price_local, currency)
            if amt_usd is None or price_usd is None or price_usd <= 0:
                continue

            cash_usd = shares_held * amt_usd
            shares_bought = cash_usd / price_usd
            lot = {
                "asOf": day,
                "ticker": ticker,
                "name": name,
                "source": "drip",
                "shares": shares_bought,
                "price": price_usd,
                "costUsd": cash_usd,
                "track": None,
                "currency": "USD",
            }
            lots.append(lot)
            event = {
                "asOf": day,
                "ticker": ticker,
                "amountPerShare": amt_usd,
                "sharesHeld": shares_held,
                "cash": cash_usd,
                "reinvestPrice": price_usd,
                "sharesBought": shares_bought,
            }
            events.append(event)
            seen.add(key)

    ledger["lots"] = lots
    events.sort(key=lambda e: (e.get("asOf") or "", e.get("ticker") or ""))
    ledger["dividendEvents"] = events
    ledger["lastDividendCheckAsOf"] = today


def fetch_last_prices(
    tickers: list[str],
    currency_by_ticker: dict[str, str] | None = None,
    sleep_s: float = 0.15,
) -> dict[str, float]:
    """Return last prices in USD using lot currencies when provided."""
    from fetch import to_usd, with_backoff

    currency_by_ticker = currency_by_ticker or {}
    prices: dict[str, float] = {}
    for ticker in tickers:
        time.sleep(sleep_s)
        currency = currency_by_ticker.get(ticker) or "USD"

        def _load(tkr: str = ticker, cur: str = currency) -> float:
            t = yf.Ticker(tkr)
            hist = t.history(period="5d", auto_adjust=True)
            local: float | None = None
            if hist is not None and not hist.empty:
                local = float(hist["Close"].dropna().iloc[-1])
            else:
                try:
                    lp = t.fast_info.last_price  # type: ignore[attr-defined]
                    local = float(lp) if lp else None
                except Exception:
                    local = None
            if local is None:
                raise RuntimeError("no price")
            usd = to_usd(local, cur)
            if usd is None:
                raise RuntimeError("fx failed")
            return usd

        px = with_backoff(_load, attempts=3, label=f"price:{ticker}")
        if px is not None:
            prices[ticker] = px
    return prices


def _round_money(x: float, n: int = 6) -> float:
    return round(float(x), n)


def rebuild_positions(ledger: dict[str, Any], prices: dict[str, float] | None = None) -> None:
    prices = prices or {}
    lots: list[dict[str, Any]] = ledger.get("lots") or []
    by_ticker: dict[str, dict[str, Any]] = {}

    for lot in lots:
        ticker = lot["ticker"]
        pos = by_ticker.setdefault(
            ticker,
            {
                "ticker": ticker,
                "name": lot.get("name") or ticker,
                "shares": 0.0,
                "cashInvested": 0.0,
                "dividendsReinvested": 0.0,
                "firstBuyAsOf": lot["asOf"],
                "lastBuyAsOf": lot["asOf"],
            },
        )
        pos["name"] = lot.get("name") or pos["name"]
        pos["shares"] += float(lot.get("shares") or 0)
        if lot.get("source") == "pick":
            pos["cashInvested"] += float(lot.get("costUsd") or 0)
        elif lot.get("source") == "drip":
            pos["dividendsReinvested"] += float(lot.get("costUsd") or 0)
        if lot["asOf"] < pos["firstBuyAsOf"]:
            pos["firstBuyAsOf"] = lot["asOf"]
        if lot["asOf"] > pos["lastBuyAsOf"]:
            pos["lastBuyAsOf"] = lot["asOf"]

    positions: list[dict[str, Any]] = []
    for ticker, pos in sorted(by_ticker.items()):
        shares = float(pos["shares"])
        cash = float(pos["cashInvested"])
        drip = float(pos["dividendsReinvested"])
        cost = cash + drip
        price = float(prices.get(ticker) or 0.0)
        if price <= 0:
            for lot in reversed(lots):
                if lot["ticker"] == ticker and lot.get("price"):
                    price = float(lot["price"])
                    break
        market = shares * price
        dca = (cost / shares) if shares > 0 else 0.0
        positions.append(
            {
                "ticker": ticker,
                "name": pos["name"],
                "shares": _round_money(shares, 8),
                "cashInvested": _round_money(cash, 4),
                "dividendsReinvested": _round_money(drip, 6),
                "totalCostBasis": _round_money(cost, 4),
                "dca": _round_money(dca, 4),
                "currentPrice": _round_money(price, 4),
                "marketValue": _round_money(market, 4),
                "dividendsReceived": _round_money(drip, 6),
                "firstBuyAsOf": pos["firstBuyAsOf"],
                "lastBuyAsOf": pos["lastBuyAsOf"],
            }
        )

    cash_invested = sum(p["cashInvested"] for p in positions)
    dividends_reinvested = sum(p["dividendsReinvested"] for p in positions)
    total_cost = cash_invested + dividends_reinvested
    current_value = sum(p["marketValue"] for p in positions)
    pnl = current_value - total_cost
    ret = (pnl / total_cost) if total_cost > 0 else None

    ledger["positions"] = positions
    ledger["summary"] = {
        "cashInvested": _round_money(cash_invested, 4),
        "dividendsReinvested": _round_money(dividends_reinvested, 6),
        "totalCostBasis": _round_money(total_cost, 4),
        "currentValue": _round_money(current_value, 4),
        "unrealizedPnl": _round_money(pnl, 4),
        "returnPct": None if ret is None else _round_money(ret, 8),
        "positionCount": len(positions),
        "dividendEventCount": len(ledger.get("dividendEvents") or []),
    }
    if ledger.get("asOf") is None:
        ledger["asOf"] = date.today().isoformat()


def update_ledger(
    picks_path: Path = DEFAULT_PICKS,
    ledger_path: Path = DEFAULT_LEDGER,
    sleep_s: float = 0.2,
    skip_dividends: bool = False,
) -> dict[str, Any]:
    picks = json.loads(picks_path.read_text(encoding="utf-8"))
    ledger = load_ledger(ledger_path)

    apply_daily_buys(ledger, picks)
    if not skip_dividends:
        apply_dividends_and_drip(ledger, sleep_s=sleep_s)

    tickers = sorted({lot["ticker"] for lot in ledger.get("lots") or []})
    currency_by_ticker: dict[str, str] = {}
    for lot in ledger.get("lots") or []:
        t = lot.get("ticker")
        if t and t not in currency_by_ticker and lot.get("currency"):
            currency_by_ticker[t] = lot["currency"]
    prices = fetch_last_prices(
        tickers,
        currency_by_ticker=currency_by_ticker,
        sleep_s=min(sleep_s, 0.2),
    )
    rebuild_positions(ledger, prices)

    ledger["asOf"] = picks.get("asOf") or ledger.get("asOf") or date.today().isoformat()
    ledger["_meta"] = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }

    # Drop internal helper if any
    ledger.pop("_tmp", None)

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    # Persist without private keys
    out = {k: v for k, v in ledger.items() if not k.startswith("_")}
    out["generatedAt"] = ledger["_meta"]["generatedAt"]
    ledger_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"Wrote {ledger_path} | positions={out['summary']['positionCount']} "
        f"cash={out['summary']['cashInvested']:.2f} value={out['summary']['currentValue']:.2f}",
        flush=True,
    )
    return out


def _self_check() -> None:
    # ponytail: one assert demo, no test framework
    ledger = empty_ledger(100, "2026-01-01")
    picks = {
        "asOf": "2026-01-02",
        "buyAmountUsd": 100,
        "dividendPicks": [{"ticker": "X", "name": "X Co", "price": 50}],
        "growthPicks": [{"ticker": "X", "name": "X Co", "price": 50}],
    }
    assert apply_daily_buys(ledger, picks)
    assert not apply_daily_buys(ledger, picks)
    assert len([L for L in ledger["lots"] if L["ticker"] == "X"]) == 1
    rebuild_positions(ledger, {"X": 60})
    assert ledger["summary"]["cashInvested"] == 100
    assert abs(ledger["positions"][0]["shares"] - 2.0) < 1e-9
    assert abs(ledger["positions"][0]["marketValue"] - 120.0) < 1e-6
    ledger["lots"].append(
        {
            "asOf": "2026-01-03",
            "ticker": "X",
            "name": "X Co",
            "source": "drip",
            "shares": 0.1,
            "price": 10,
            "costUsd": 1.0,
            "track": None,
        }
    )
    rebuild_positions(ledger, {"X": 60})
    assert ledger["summary"]["dividendsReinvested"] == 1.0
    assert ledger["summary"]["cashInvested"] == 100
    print("self-check ok")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Update shared paper portfolio ledger")
    parser.add_argument("--picks", type=Path, default=DEFAULT_PICKS)
    parser.add_argument("--out", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--skip-dividends", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        _self_check()
        return 0
    update_ledger(args.picks, args.out, sleep_s=args.sleep, skip_dividends=args.skip_dividends)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
