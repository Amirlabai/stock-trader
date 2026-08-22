import type { DividendPick } from '../types/picks'
import { pct, score, usd } from '../lib/format'

type Props = {
  picks: DividendPick[]
  onSelect: (pick: DividendPick) => void
}

export function DividendTable({ picks, onSelect }: Props) {
  if (picks.length === 0) {
    return <p className="empty">No dividend picks for this session yet.</p>
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Sector</th>
            <th>Yield</th>
            <th>5Y Div CAGR</th>
            <th>FCF payout</th>
            <th>Score</th>
            <th>Purification / sh</th>
          </tr>
        </thead>
        <tbody>
          {picks.map((p) => (
            <tr key={p.ticker}>
              <td data-label="Ticker">
                <button type="button" className="linkish" onClick={() => onSelect(p)}>
                  <strong>{p.ticker}</strong>
                  <span className="sub">{p.name}</span>
                </button>
              </td>
              <td data-label="Sector">{p.sector}</td>
              <td data-label="Yield">{pct(p.yield)}</td>
              <td data-label="5Y Div CAGR">{pct(p.divCagr5y)}</td>
              <td data-label="FCF payout">{pct(p.fcfPayout)}</td>
              <td data-label="Score">{score(p.score)}</td>
              <td data-label="Purification / sh">{usd(p.purificationPerShare, 4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
