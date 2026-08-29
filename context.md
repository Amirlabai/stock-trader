# Halal Dual-Strategy Stock Screener

## Purpose
Static daily dashboard for Shariah-compliant (AAOIFI-style) equity picks, split into Dividend and Growth tracks. Hosted on GitHub Pages.

## Architecture
- **Frontend:** Vite + React + TypeScript in `apps/web/`. Loads `public/data/daily-picks.json` and `public/data/paper-portfolio.json`.
- **Pipeline:** Python screener in `pipeline/`. Fail-closed Tier 1 (missing sector/industry rejected). Tier 2 ratios fail closed on missing debt/cash/receivables. Prices stored in USD (FX via Yahoo pairs; GBp handled).
- **Paper portfolio:** Shared ledger with DCA / mark-to-market / DRIP. Dedupes tickers across tracks per day. Repeat buy: another lot on every new `asOf` while the ticker is still on the unique pick list. Journal lists every fill; positions are the mark-to-market snapshot.
- **CI:** Screen cron is Mon–Fri 22:00 UTC; GitHub may delay into weekend UTC. `asOf` snaps to the last weekday so delayed runs do not create Sat/Sun buy days. Manual `workflow_dispatch` uses the same snap. Push builds from committed data.

## Key parameters
- Full screen parameter reference: `pipeline/SCREEN_PARAMETERS.md`.
- Debt / Cash / Receivables screens: each under 33% of trailing market cap (24-month average when available).
- Dividend track: yield about 2.5–7.5%, payout 25–70%, multi-year dividend growth, interest coverage above 3.5x.
- Growth track: revenue/EPS growth and ROIC thresholds; price above 200-day SMA.
- Daily output: top 5 dividend + top 5 growth.
- Paper buy size: USD 100 per pick lot; DCA = total cost basis / shares; cash invested excludes DRIP cash.
- Repeat buy: if a ticker was bought yesterday, it is bought again today whenever it is still on that day's unique pick list (price present and greater than 0). `lastBuyAsOf` only prevents applying the same date twice.

## Visual system
- Captured in root `DESIGN.md` (tokens in YAML frontmatter) and `.impeccable/design.json`.
- North star: The Quiet Ledger. Dark pine interiors, antique-brass citations, Fraunces + Source Sans 3, square hairline chambers, no shadows.
- CSS tokens live in `apps/web/src/App.css` (`--bg0` through `--danger`, `--font-display`, `--font-body`).
- Mobile (under 720px): compact ledger cards (ticker + name on one line; metrics in 2–3 columns); audit drawer is full-width; tap targets ≥44px.
- Main panels use disclosure summaries; Track A, Track B, and Paper portfolio default open; Methodology and Transactions default closed.
- Methodology panel (collapsed at bottom) parses `pipeline/SCREEN_PARAMETERS.md` (synced to `apps/web/src/content/screen-parameters.md` by Vite).

## Conventions
- Product copy: formal plain language; no em dashes; no emoji.
- Public UI is view-only (no per-visitor actions).
- Expand the investable universe via `pipeline/universe/*.csv` (columns: `ticker,region,name`).
- Data contracts: `apps/web/src/types/picks.ts`, `apps/web/src/types/portfolio.ts`.
- Vite `base` defaults to `/stock-trader/` for project Pages hosting.
