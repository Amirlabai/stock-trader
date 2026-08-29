# Halal Dual-Strategy Stock Screener

Daily Shariah-compliant dividend and growth picks. Static site on GitHub Pages; screening is scheduled Mon–Fri 22:00 UTC via GitHub Actions (`yfinance`). If a job is delayed into the weekend, `asOf` still snaps to the last weekday.

## Local development

```powershell
cd apps/web
npm install
npm run dev
```

## Screening pipeline

```powershell
cd pipeline
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\pipeline\.venv\Scripts\python.exe run_screen.py
```

Output lands in `apps/web/public/data/daily-picks.json`.

## Expand universe

Add rows to `pipeline/universe/*.csv` with columns `ticker,region,name`.

## Paper portfolio

Shared ledger at `apps/web/public/data/paper-portfolio.json` (updated by the daily pipeline):

- Each unique ticker on a day's pick list is bought for the amount in `daily-picks.json` (default USD 100).
- If that ticker is still on the next day's unique list, another lot is bought. Already holding the name does not skip the buy. Same ticker on both tracks the same day is one lot (dividend track preferred).
- Holdings are marked to market. The transaction journal lists every fill (date, side, shares, price, cash invested after, reason).
- Dividends are recorded when yfinance provides payout history and reinvested (DRIP). DRIP does not add cash invested.
- The public site is view-only; every visitor sees the same ledger.

## Hosting

1. Push this repo to GitHub.
2. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
3. The `Weekday screen and deploy` workflow screens the universe Mon–Fri, builds the site, and publishes to Pages at `/stock-trader/`.

Manual screen (no deploy):

```powershell
pipeline\.venv\Scripts\python.exe pipeline\run_screen.py
```
