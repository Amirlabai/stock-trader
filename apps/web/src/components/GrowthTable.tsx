import type { GrowthPick } from '../types/picks'
import { pct, score, usd } from '../lib/format'

type Props = {
  picks: GrowthPick[]
  onSelect: (pick: GrowthPick) => void
}

export function GrowthTable({ picks, onSelect }: Props) {
  if (picks.length === 0) {
    return <p className="empty">No growth picks for this session yet.</p>
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Sector</th>
            <th>Price</th>
            <th>TTM rev growth</th>
            <th>Forward EPS growth</th>
            <th>Debt / MC</th>
            <th>Score</th>
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
              <td>{usd(p.price)}</td>
              <td>{pct(p.revGrowthTtm)}</td>
              <td>{pct(p.fwdEpsGrowth)}</td>
              <td>{pct(p.debtToMc, 2)}</td>
              <td>{score(p.score)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
