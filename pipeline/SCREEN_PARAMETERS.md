# Screen parameters

Thresholds used by the Halal dual-strategy screener. Source of truth for runtime values: `compliance.py`, `ratios.py`, `strategies.py`, and `run_screen.py`. The dashboard Methodology panel parses this file (synced into `apps/web/src/content/screen-parameters.md` on Vite start/build).

All strategy filters run only after Tier 1 and Tier 2 pass. Fail closed on missing required data.

## Output

| Parameter | Value | Code |
|---|---|---|
| Dividend daily picks | Top 5 by score | `run_screen.py` |
| Growth daily picks | Top 5 by score | `run_screen.py` |
| Paper buy size | USD 100 per pick lot | `BUY_AMOUNT_USD` |
| Default fetch sleep | 0.35 s between tickers | `--sleep` |

## Paper ledger

Each unique ticker on a day's pick list is bought for USD 100. The same ticker on both tracks that day is one lot (dividend track preferred). If the ticker remains on a later day's unique list, another lot is bought. Already holding the name does not skip the buy. `lastBuyAsOf` only blocks applying the same calendar date twice. Dividend reinvestment adds shares but does not add cash invested. Holdings are the mark-to-market snapshot; the transaction journal lists every fill.

| Parameter | Value | Notes |
|---|---|---|
| Paper buy size | USD 100 per pick lot | New cash per unique ticker per `asOf` |
| Same-day overlap | One lot | Dividend track preferred |
| Repeat buy | Every new `asOf` while still on the unique pick list | Already held does not skip |
| Journal | Every fill | Date, side, shares, price, cash invested after, reason |

## Tier 1: Sector and business activity

Fail closed if sector or industry is missing. Optional haram revenue share, when known, must stay below the limit.

| Parameter | Threshold | Notes |
|---|---|---|
| Haram revenue share | `< 5%` | `HARAM_REVENUE_LIMIT = 0.05` |
| Banned sectors | Keyword match | Financials, banks, insurance, capital markets |
| Banned industries | Keyword match | Alcohol, tobacco, gambling, adult, defense/weapons, non-halal meat, and related labels |
| Ticker denylist | Exact ticker match | Hard exclusions in `TICKER_DENYLIST` |

Banned labels and the denylist are maintained in the compliance module.

## Tier 2: AAOIFI-style financial ratios

Denominator prefers 24-month trailing average market cap when available; otherwise spot market cap. Cash includes short-term investments.

| Screen | Formula | Pass if |
|---|---|---|
| Debt | Total interest-bearing debt / market cap | `< 33%` |
| Cash | (Cash + short-term investments) / market cap | `< 33%` |
| Receivables | Accounts receivable / market cap | `< 33%` |

`RATIO_LIMIT = 0.33`. Missing debt, cash, receivables, or market cap fails the name.

Purification estimate (informational, not a gate): `|interest income| / shares outstanding` when both are available.

## Strategy A: Dividend

| Parameter | Threshold |
|---|---|
| Dividend yield | `2.5%` to `7.5%` inclusive band |
| Dividend history | At least 5 consecutive complete years, non-decreasing |
| FCF payout | Total dividends / free cash flow between `25%` and `70%` |
| Interest coverage | Operating income / interest expense `> 3.5x` (treated as pass if expense is zero and operating income is positive) |
| Operating cash flow | Positive in each of the last 3 fiscal years |

Composite score (0–100): base 50, plus yield, 5-year dividend CAGR, payout near 45%, and lower debt-to-market-cap.

## Strategy B: Growth

| Parameter | Threshold |
|---|---|
| YoY revenue growth (TTM) | `> 15%` |
| 3-year revenue CAGR | `> 12%` (needs 4 annual revenue points) |
| Forward EPS growth | `> 15%` |
| ROIC (3-year average) | `> 12%` |
| Price vs 200-day SMA | Price `>=` SMA |
| 3-month relative strength | Price / price 3 months ago `- 1 > 0` |

Composite score (0–100): base 50, plus YoY growth, revenue CAGR, forward EPS growth, ROIC, 3-month relative strength, and lower debt-to-market-cap.

## Universe

Tickers come from the curated universe CSVs (`ticker,region,name`). Expand the investable set by adding rows there.
