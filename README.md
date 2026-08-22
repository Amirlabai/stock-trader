# Halal Dual-Strategy Stock Screener

Daily Shariah-compliant dividend and growth picks. Static site on GitHub Pages; screening runs in GitHub Actions via `yfinance`.

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

- Each published pick is bought for the amount in `daily-picks.json` (default USD 100).
- Positions are marked to market; DCA and unrealized P&L are shown on the dashboard.
- Dividends are recorded when yfinance provides payout history and reinvested (DRIP).
- The public site is view-only; every visitor sees the same ledger.

## Hosting

1. Push this repo to GitHub.
2. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
3. The `Daily screen and deploy` workflow screens the universe, builds the site, and publishes to Pages at `/stock-trader/`.

Manual screen (no deploy):

```powershell
pipeline\.venv\Scripts\python.exe pipeline\run_screen.py
```
