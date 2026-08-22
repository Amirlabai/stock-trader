import { useEffect, useRef } from 'react'
import type { AaoifiRatios } from '../types/picks'
import { pct, usd } from '../lib/format'

type Props = {
  ticker: string
  name: string
  sector: string
  region: string
  ratios: AaoifiRatios
  onClose: () => void
}

export function AuditDrawer({
  ticker,
  name,
  sector,
  region,
  ratios,
  onClose,
}: Props) {
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    closeRef.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="drawer-backdrop" role="presentation" onClick={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="drawer-header">
          <div>
            <p className="eyebrow">Compliance audit</p>
            <h2 id="audit-title">
              {ticker} <span className="muted">{name}</span>
            </h2>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="ghost"
            onClick={onClose}
            aria-label="Close"
          >
            Close
          </button>
        </header>

        <p className="drawer-meta">
          {sector} · {region} · market cap basis: {ratios.mcBasis}
        </p>

        <table className="metric-table">
          <tbody>
            <tr>
              <th>Debt / market cap</th>
              <td>{pct(ratios.debtToMarketCap, 2)}</td>
            </tr>
            <tr>
              <th>Cash + interest securities / market cap</th>
              <td>{pct(ratios.cashToMarketCap, 2)}</td>
            </tr>
            <tr>
              <th>Receivables / market cap</th>
              <td>{pct(ratios.receivablesToMarketCap, 2)}</td>
            </tr>
            <tr>
              <th>Non-operating interest income</th>
              <td>{usd(ratios.interestIncomeNonOp, 0)}</td>
            </tr>
            <tr>
              <th>Purification estimate per share</th>
              <td>{usd(ratios.purificationPerShare, 4)}</td>
            </tr>
          </tbody>
        </table>

        <p className="hint">
          AAOIFI-style screens use a 33% limit on debt, cash, and receivables versus
          trailing market cap when available. Purification is an estimate from reported
          interest income and is not a fatwa. Missing interest income shows as -.
        </p>
      </aside>
    </div>
  )
}
