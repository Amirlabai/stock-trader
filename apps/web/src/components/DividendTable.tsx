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
      <table>
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
              <td>
                <button type="button" className="linkish" onClick={() => onSelect(p)}>
                  <strong>{p.ticker}</strong>
                  <span className="sub">{p.name}</span>
                </button>
              </td>
              <td>{p.sector}</td>
              <td>{pct(p.yield)}</td>
              <td>{pct(p.divCagr5y)}</td>
              <td>{pct(p.fcfPayout)}</td>
              <td>{score(p.score)}</td>
              <td>{usd(p.purificationPerShare, 4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
