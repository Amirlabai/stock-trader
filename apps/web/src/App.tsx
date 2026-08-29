import { useEffect, useState } from 'react'
import type { DailyPicks, DividendPick, GrowthPick } from './types/picks'
import type { PaperPortfolio } from './types/portfolio'
import { AuditDrawer } from './components/AuditDrawer'
import { Disclose } from './components/Disclose'
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
  const dividendCount = data?.dividendPicks?.length ?? 0
  const growthCount = data?.growthPicks?.length ?? 0

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
        <Disclose
          className="panel"
          startOpen
          summary={
            <>
              <span className="eyebrow">Track A</span>
              <span className="disclose-title">Halal Dividend Daily Picks</span>
              <span className="disclose-hint muted">
                {data
                  ? `Top ${dividendCount || 5} by composite score after AAOIFI-style screens`
                  : 'Top five by composite score after AAOIFI-style screens'}
              </span>
            </>
          }
        >
          <div className="disclose-body">
            {!data ? (
              <p className="empty">Loading picks…</p>
            ) : (
              <DividendTable
                picks={data.dividendPicks}
                onSelect={(pick) => setAudit({ track: 'dividend', pick })}
              />
            )}
          </div>
        </Disclose>

        <Disclose
          className="panel"
          startOpen
          summary={
            <>
              <span className="eyebrow">Track B</span>
              <span className="disclose-title">Halal Growth Daily Picks</span>
              <span className="disclose-hint muted">
                {data
                  ? `Top ${growthCount || 5} compounders with compliant capital structures`
                  : 'Top five compounders with compliant capital structures'}
              </span>
            </>
          }
        >
          <div className="disclose-body">
            {!data ? (
              <p className="empty">Loading picks…</p>
            ) : (
              <GrowthTable
                picks={data.growthPicks}
                onSelect={(pick) => setAudit({ track: 'growth', pick })}
              />
            )}
          </div>
        </Disclose>

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
