TL;DR: This revised PRD establishes a 100% Halal-by-design stock screener featuring a split daily dashboard dedicated to Halal Dividend Picks and Halal Growth Picks.

Product Requirement Document (PRD): Halal Dual-Strategy Stock Screener

1. Executive Summary & Objective
The product is a specialized equity screening engine and daily dashboard built exclusively for Shariah-compliant investing. Non-compliant stocks are purged at the ingestion layer, ensuring that 100% of the universe accessible to users is Halal.

The platform processes the compliant universe daily and outputs high-conviction ideas split across two distinct investment tracks:

* Halal Dividend Track: Focus on sustainable yield, consistent dividend growth, and low payout risk.
* Halal Growth Track: Focus on top-line expansion, earnings acceleration, and business momentum.

---

2. Architecture & Compliance Gateway (Universal Rule)
All screening operations operate strictly downstream of the Shariah Compliance Engine. A stock cannot enter either strategy pipeline unless it passes both Tier 1 and Tier 2 criteria based on standard AAOIFI guidelines.

Tier 1: Sector & Business Activity Screen
Zero tolerance / <5% revenue threshold for:

* Conventional banking, insurance, and interest-based financial services.
* Alcohol, tobacco, gambling, adult entertainment, weapons/defense, and non-halal food/meat processing.

Tier 2: Financial Ratio Screen (Using 24-Month Trailing Average Market Cap)

* Debt Screen: Total Interest-Bearing Debt / Market Cap < 33%
* Cash Screen: (Cash + Interest-Bearing Securities) / Market Cap < 33%
* Receivables Screen: Accounts Receivable / Market Cap < 33%

---

3. Strategy Screening Engines

Strategy A: Halal Dividend Growth Engine
Target: Stable cash-flow compounding without violating leverage or purification limits.

* Minimum 5 consecutive years of steady or increasing dividend payouts.
* Free Cash Flow (FCF) Payout Ratio: 25% to 70%.
* Dividend Yield: 2.5% to 7.5%.
* Interest Coverage Ratio: Operating Income / Interest Expense > 3.5x.
* Cash Flow Stability: Positive Operating Cash Flow across the last 3 fiscal years.

Strategy B: Halal Capital Growth Engine
Target: High-conviction compounders with compliant capital structures.

* YoY Revenue Growth (TTM): > 15%.
* 3-Year Revenue CAGR: > 12%.
* Forward EPS Growth: > 15%.
* Return on Invested Capital (ROIC): > 12% (3-year average).
* Technical Momentum: Price above 200-day Simple Moving Average (SMA); positive 3-month relative price strength.

---

4. Dashboard & Daily Pick System

Daily Pick Algorithm:
Every day post-market close, compliant equities are evaluated on a 0-100 composite score (incorporating balance-sheet health, valuation multiples, and momentum).

Dashboard UI Layout:
The main dashboard is partitioned into two distinct daily pick sections:

1. Halal Dividend Daily Picks (Top 5 Tickers)

* Columns: Ticker & Name, Sector, Current Yield, 5-Year Dividend CAGR, FCF Payout Ratio, Composite Score, Purification Estimate per Share ($/share).

2. Halal Growth Daily Picks (Top 5 Tickers)

* Columns: Ticker & Name, Sector, Current Price, TTM Revenue Growth %, Forward EPS Growth %, Debt-to-Market Cap %, Composite Score.

3. Compliance Audit Modal

* Clicking any ticker opens an audit drawer showing exact AAOIFI ratio percentages and non-operating interest income for purification.

---

5. Key Performance Indicators (KPIs)

* Compliance Precision: 0% false-positive rate for non-compliant stocks entering user feeds.
* Tracking Alpha: Strategy performance benchmarked against the MSCI World Islamic Index, S&P 500 Dividend Aristocrats, and Nasdaq-100.
* Daily Engagement: Daily Active Users (DAU) reviewing morning pick drops.

---

To tailor the next steps for implementation:

1. Which specific geographic markets/exchanges are you launching with first (e.g., US markets only vs. global)?
2. Would you like to include an automated portfolio tracker that calculates total purification amounts for users' holdings?
3. What is the target launch platform (Web app, Mobile iOS/Android, or both)?