import { useEffect, useState } from 'react'
import type { DailyPicks, DividendPick, GrowthPick } from './types/picks'
import type { PaperPortfolio } from './types/portfolio'
import { AuditDrawer } from './components/AuditDrawer'
import { DividendTable } from './components/DividendTable'
import { GrowthTable } from './components/GrowthTable'
import { PortfolioPanel } from './components/PortfolioPanel'
import { ScreenMethodPanel } from './components/ScreenMethodPanel'
import './App.css'

type AuditTarget =
  | { track: 'dividend'; pick: DividendPick }
  | { track: 'growth'; pick: GrowthPick }

function App() {
  const [data, setData] = useState<DailyPicks | null>(null)
  const [portfolio, setPortfolio] = useState<PaperPortfolio | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [audit, setAudit] = useState<AuditTarget | null>(null)

  useEffect(() => {
    const base = import.meta.env.BASE_URL
    Promise.all([
      fetch(`${base}data/daily-picks.json`).then(async (res) => {
        if (!res.ok) throw new Error(`Failed to load picks (${res.status})`)
        return res.json() as Promise<DailyPicks>
      }),
      fetch(`${base}data/paper-portfolio.json`).then(async (res) => {
        if (!res.ok) throw new Error(`Failed to load portfolio (${res.status})`)
        return res.json() as Promise<PaperPortfolio>
      }),
    ])
      .then(([picks, ledger]) => {
        setData(picks)
        setPortfolio(ledger)
      })
      .catch((err: Error) => setError(err.message))
  }, [])

  const buyAmount = data?.buyAmountUsd ?? portfolio?.buyAmountUsd ?? 100

  return (
    <div className="app">
      <header className="site-header">
        <div>
          <p className="brand">Halal Dual-Strategy Screener</p>
          <h1>Daily Shariah-compliant picks</h1>
          <p className="lede">
            Dividend and growth ideas from a curated global universe. Non-compliant names
            are removed before strategy scoring.
          </p>
        </div>
        <div className="asof">
          {data ? (
            <>
              <span className="stat-label">As of</span>
              <strong>{data.asOf}</strong>
              <span className="muted">
                Paper buy {buyAmount.toFixed(0)} USD · universe{' '}
                {data.meta?.universeSize ?? '-'} · compliant{' '}
                {data.meta?.compliantCount ?? '-'}
              </span>
            </>
          ) : error ? (
            <span className="error">{error}</span>
          ) : (
            <span className="muted">Loading daily picks…</span>
          )}
        </div>
      </header>

      <main>
        <section className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">Track A</p>
              <h2>Halal Dividend Daily Picks</h2>
              <p className="lede">Top five by composite score after AAOIFI-style screens.</p>
            </div>
          </div>
          {!data ? (
            <p className="empty">Loading picks…</p>
          ) : (
            <DividendTable
              picks={data.dividendPicks}
              onSelect={(pick) => setAudit({ track: 'dividend', pick })}
            />
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">Track B</p>
              <h2>Halal Growth Daily Picks</h2>
              <p className="lede">Top five compounders with compliant capital structures.</p>
            </div>
          </div>
          {!data ? (
            <p className="empty">Loading picks…</p>
          ) : (
            <GrowthTable
              picks={data.growthPicks}
              onSelect={(pick) => setAudit({ track: 'growth', pick })}
            />
          )}
        </section>

        {portfolio && <PortfolioPanel portfolio={portfolio} />}

        <ScreenMethodPanel />
      </main>

      <footer className="site-footer">
        <p>
          Screening is AAOIFI-inspired (fail-closed activity labels; segment revenue not fully
          verified from free data). This is not investment advice and not a substitute for a
          qualified Shariah board.
        </p>
      </footer>

      {audit && (
        <AuditDrawer
          ticker={audit.pick.ticker}
          name={audit.pick.name}
          sector={audit.pick.sector}
          region={audit.pick.region}
          ratios={audit.pick.ratios}
          onClose={() => setAudit(null)}
        />
      )}
    </div>
  )
}

export default App
