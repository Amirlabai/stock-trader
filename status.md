# Status

## Objectives
- [x] Workspace docs and Vite React app scaffold
- [x] Python AAOIFI + strategy screening pipeline
- [x] Dual pick dashboard + compliance audit drawer
- [x] View-only public UI (no per-visitor actions)
- [x] Shared paper portfolio ledger (DCA, mark-to-market, dividends + DRIP)
- [x] Transaction journal of every fill (not only aggregated holdings)
- [x] GitHub Actions weekday (Mon–Fri) screen + ledger commit + Pages deploy

## Completed
- `pipeline/portfolio_ledger.py` maintains `apps/web/public/data/paper-portfolio.json`
- Dashboard shows cash invested, current value, P&L, holdings snapshot, and a transaction journal of every fill
- Repeat buy: another USD 100 lot on every new `asOf` while the ticker is still on the unique pick list
- Visual system documented in `DESIGN.md` and `.impeccable/design.json` (Quiet Ledger)
- Unused CSS and leftover Vite assets removed; look unchanged
- `pipeline/SCREEN_PARAMETERS.md` documents Tier 1/2 and strategy thresholds
- Mobile fit: compact horizontal ledger cards under 720px (2–3 metric columns, no page spill), 44px tap targets, safe-area insets, full-width audit drawer
- Screen calendar: weekday `asOf` only; delayed weekend UTC jobs snap to Friday (no Sat/Sun buy days)
- Holdings table shows per-position unrealized P&L (market value minus total cost basis), with the P&L cell colored green for a gain and red for a loss (`.pos` / `.neg`); `usd()` now formats negatives as `-$12.34`; holdings sorted by P&L, largest gain first
- Mobile ledger cards tightened: holdings put P&L on the ticker line, transactions put side and date on the ticker line with the reason as a caption; three metric columns from 340px (was 380px)
- Contrast audit: all text tokens pass WCAG AA on panels; Dusty Coral lifted from `#e08a7a` to `#e69584` so the header error passes 4.5:1 on the brightest canvas wash
- 2026-11-05: Valuation added from the course "Financial Statement and Capital Market Analysis" (P/E, PEG, P/B, Gordon model). PEG adjusts the growth score; a two-stage dividend model margin of safety adjusts the dividend score (replaced a capped single-stage Gordon model that rated every fast-growing payer equally cheap) (each clamped to plus or minus 10); missing figures add nothing. The audit drawer shows a Valuation section. Score changes alter which names make the top 5, so ledger buys from the next `asOf` onward reflect valuation; past lots are unchanged.
- Code graph built in `graphify-out/` (refresh with `/graphify . --update`)
- Universe expanded to ~527 tickers via `pipeline/universe/seed_expansion.csv` (US/UK/EU/APAC/CA)

## Next
- Enable GitHub Pages and push to `main` for the first live deploy
- Expand `pipeline/universe/*.csv` further over time as needed
- Considered from the course and deferred: cash flow life-cycle stage (CFO/CFI/CFF signs), liquidity/leverage/margin ratios in the audit drawer, ledger sell rules (exit on compliance failure, stop loss)
- Optional: `/impeccable init` to capture PRODUCT.md (not required for the current dashboard)
