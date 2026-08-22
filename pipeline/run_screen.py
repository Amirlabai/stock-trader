#!/usr/bin/env python3
"""Daily Halal dual-strategy screen -> apps/web/public/data/daily-picks.json"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from compliance import passes_tier1
from fetch import fetch_snapshot
from portfolio_ledger import DEFAULT_LEDGER, update_ledger
from ratios import compute_ratios, ratios_dict
from strategies import evaluate_dividend, evaluate_growth
from universe_loader import load_universe

DEFAULT_OUT = ROOT.parent / "apps" / "web" / "public" / "data" / "daily-picks.json"
BUY_AMOUNT_USD = 100


def pick_to_dividend(p) -> dict:
    s = p.snap
    r = p.ratios
    return {
        "ticker": s.ticker,
        "name": s.name,
        "sector": s.sector or "Unknown",
        "region": s.region,
        "currency": s.currency,
        "price": s.price_usd,
        "priceLocal": s.price,
        "yield": p.metrics["yield"],
        "divCagr5y": p.metrics.get("divCagr5y"),
        "fcfPayout": p.metrics.get("fcfPayout"),
        "score": round(p.score, 1),
        "purificationPerShare": r.purification_per_share,
        "ratios": ratios_dict(r),
    }


def pick_to_growth(p) -> dict:
    s = p.snap
    r = p.ratios
    return {
        "ticker": s.ticker,
        "name": s.name,
        "sector": s.sector or "Unknown",
        "region": s.region,
        "currency": s.currency,
        "price": s.price_usd,
        "priceLocal": s.price,
        "revGrowthTtm": p.metrics.get("revGrowthTtm"),
        "fwdEpsGrowth": p.metrics.get("fwdEpsGrowth"),
        "debtToMc": p.metrics.get("debtToMc"),
        "score": round(p.score, 1),
        "purificationPerShare": r.purification_per_share,
        "ratios": ratios_dict(r),
    }


def run(limit: int | None = None, sleep_s: float = 0.35) -> dict:
    from fetch import LAST_SKIP_REASON

    universe = load_universe(ROOT / "universe")
    if limit is not None:
        universe = universe[:limit]

    notes: list[str] = []
    compliant = 0
    dividend_picks = []
    growth_picks = []

    for i, row in enumerate(universe, start=1):
        print(f"[{i}/{len(universe)}] {row.ticker}", flush=True)
        snap = fetch_snapshot(row.ticker, row.region, row.name, sleep_s=sleep_s)
        if snap is None:
            reason = LAST_SKIP_REASON or "fetch_failed"
            if reason == "missing_activity_data":
                notes.append(f"tier1:{row.ticker}:missing_activity_data")
            elif reason == "fx_unavailable":
                notes.append(f"fx_failed:{row.ticker}")
            else:
                notes.append(f"fetch_failed:{row.ticker}")
            continue

        if snap.price_usd is None or snap.price_usd <= 0:
            notes.append(f"fx_failed:{row.ticker}")
            continue

        ok, reason = passes_tier1(
            snap.ticker,
            snap.sector,
            snap.industry,
            haram_revenue_pct=snap.haram_revenue_pct,
        )
        if not ok:
            notes.append(f"tier1:{row.ticker}:{reason}")
            continue

        ratios = compute_ratios(snap)
        if not ratios.passed:
            notes.append(f"tier2:{row.ticker}:{ratios.reason}")
            continue

        compliant += 1
        d = evaluate_dividend(snap, ratios)
        if d is not None:
            dividend_picks.append(d)
        g = evaluate_growth(snap, ratios)
        if g is not None:
            growth_picks.append(g)

    dividend_picks.sort(key=lambda p: p.score, reverse=True)
    growth_picks.sort(key=lambda p: p.score, reverse=True)

    payload = {
        "asOf": date.today().isoformat(),
        "buyAmountUsd": BUY_AMOUNT_USD,
        "dividendPicks": [pick_to_dividend(p) for p in dividend_picks[:5]],
        "growthPicks": [pick_to_growth(p) for p in growth_picks[:5]],
        "meta": {
            "universeSize": len(universe),
            "compliantCount": compliant,
            "notes": notes[:200],
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "dividendCandidates": len(dividend_picks),
            "growthCandidates": len(growth_picks),
        },
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Halal dual-strategy screen")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=None, help="Limit universe size (dev)")
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument(
        "--keep-previous-if-empty",
        action="store_true",
        help="If new run has zero picks in both tracks, keep existing JSON",
    )
    parser.add_argument(
        "--skip-ledger",
        action="store_true",
        help="Do not update paper-portfolio.json after screening",
    )
    parser.add_argument(
        "--skip-dividends",
        action="store_true",
        help="Skip dividend/DRIP pass when updating the ledger",
    )
    args = parser.parse_args()

    payload = run(limit=args.limit, sleep_s=args.sleep)

    if args.keep_previous_if_empty and not payload["dividendPicks"] and not payload["growthPicks"]:
        if args.out.exists():
            print("No picks produced; keeping previous daily-picks.json", flush=True)
            if not args.skip_ledger:
                update_ledger(
                    picks_path=args.out,
                    ledger_path=DEFAULT_LEDGER,
                    sleep_s=args.sleep,
                    skip_dividends=args.skip_dividends,
                )
            return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.out} | dividend={len(payload['dividendPicks'])} growth={len(payload['growthPicks'])}",
        flush=True,
    )

    if not args.skip_ledger:
        update_ledger(
            picks_path=args.out,
            ledger_path=DEFAULT_LEDGER,
            sleep_s=args.sleep,
            skip_dividends=args.skip_dividends,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
