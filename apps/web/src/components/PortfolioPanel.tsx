import type { PaperPortfolio } from '../types/portfolio'
import { num, pct, usd } from '../lib/format'

type Props = {
  portfolio: PaperPortfolio
}

export function PortfolioPanel({ portfolio }: Props) {
  const s = portfolio.summary
  const events = [...(portfolio.dividendEvents || [])]
    .sort((a, b) => (a.asOf < b.asOf ? 1 : a.asOf > b.asOf ? -1 : 0))
    .slice(0, 10)

  return (
    <section className="panel portfolio">
      <div className="panel-head">
        <div>
          <p className="eyebrow">Paper portfolio</p>
          <h2>Shared ledger as of {portfolio.asOf}</h2>
          <p className="lede">
            Each daily pick is bought for {usd(portfolio.buyAmountUsd, 0)}. Dividends are
            reinvested (DRIP) when payout data is available. Figures are the same for every
            visitor.
          </p>
        </div>
      </div>

      <div className="stat-row stat-row-wide">
        <div>
          <span className="stat-label">Cash invested</span>
          <strong>{usd(s.cashInvested)}</strong>
        </div>
        <div>
          <span className="stat-label">Current value</span>
          <strong>{usd(s.currentValue)}</strong>
        </div>
        <div>
          <span className="stat-label">Unrealized P&amp;L</span>
          <strong className={s.unrealizedPnl >= 0 ? 'pos' : 'neg'}>
            {usd(s.unrealizedPnl)} ({pct(s.returnPct)})
          </strong>
        </div>
        <div>
          <span className="stat-label">Dividends reinvested</span>
          <strong>{usd(s.dividendsReinvested, 4)}</strong>
        </div>
        <div>
          <span className="stat-label">Positions</span>
          <strong>{s.positionCount}</strong>
        </div>
      </div>

      {portfolio.positions.length === 0 ? (
        <p className="empty">No positions in the ledger yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Shares</th>
                <th>DCA</th>
                <th>Price</th>
                <th>Market value</th>
                <th>Cash in</th>
                <th>Dividends</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.positions.map((p) => (
                <tr key={p.ticker}>
                  <td>
                    <strong>{p.ticker}</strong>
                    <span className="sub">{p.name}</span>
                  </td>
                  <td>{num(p.shares, 4)}</td>
                  <td>{usd(p.dca)}</td>
                  <td>{usd(p.currentPrice)}</td>
                  <td>{usd(p.marketValue)}</td>
                  <td>{usd(p.cashInvested)}</td>
                  <td>{usd(p.dividendsReceived, 4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="dividend-log">
        <h3>Recent dividend DRIP</h3>
        {events.length === 0 ? (
          <p className="empty">No dividend payouts recorded yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Ticker</th>
                  <th>$ / share</th>
                  <th>Cash</th>
                  <th>Reinvest price</th>
                  <th>Shares bought</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e) => (
                  <tr key={`${e.asOf}-${e.ticker}-${e.amountPerShare}`}>
                    <td>{e.asOf}</td>
                    <td>{e.ticker}</td>
                    <td>{usd(e.amountPerShare, 4)}</td>
                    <td>{usd(e.cash, 4)}</td>
                    <td>{usd(e.reinvestPrice)}</td>
                    <td>{num(e.sharesBought, 6)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}
