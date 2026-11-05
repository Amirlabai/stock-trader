import { useEffect, useRef } from 'react'
import type { AaoifiRatios, Valuation } from '../types/picks'
import { num, pct, usd } from '../lib/format'

type Props = {
  ticker: string
  name: string
  sector: string
  region: string
  ratios: AaoifiRatios
  /** USD price, used to show the Gordon fair value in USD. */
  price: number
  valuation: Valuation
  /** Dividend picks carry the Gordon model rows. */
  showGordon: boolean
  onClose: () => void
}

export function AuditDrawer({
  ticker,
  name,
  sector,
  region,
  ratios,
  price,
  valuation,
  showGordon,
  onClose,
}: Props) {
  const mos = valuation.marginOfSafety
  const fairUsd = mos == null ? null : price * (1 + mos)
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

        <p className="eyebrow drawer-section">Valuation</p>
        <table className="metric-table">
          <tbody>
            <tr>
              <th>Price / earnings (trailing)</th>
              <td>{num(valuation.pe, 1)}</td>
            </tr>
            <tr>
              <th>PEG (P/E over forward EPS growth)</th>
              <td>{num(valuation.peg, 2)}</td>
            </tr>
            <tr>
              <th>Price / book</th>
              <td>{num(valuation.pb, 2)}</td>
            </tr>
            {showGordon && (
              <>
                <tr>
                  <th>Dividend model fair value</th>
                  <td>{usd(fairUsd)}</td>
                </tr>
                <tr>
                  <th>Margin of safety</th>
                  <td className={mos == null ? undefined : mos >= 0 ? 'pos' : 'neg'}>
                    {pct(mos, 1)}
                  </td>
                </tr>
              </>
            )}
          </tbody>
        </table>

        <p className="hint">
          PEG under 1 means earnings growth outpaces the multiple paid.
          {showGordon &&
            ' Fair value uses a two-stage dividend model: dividends grow at the 5-year dividend CAGR (up to 15%) for 5 years, then at 3% a year, all discounted at a 9% required return.'}{' '}
          Valuation adjusts the score but never excludes a name.
        </p>
      </aside>
    </div>
  )
}
