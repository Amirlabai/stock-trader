import type { LotSide, PaperPortfolio, PortfolioLot } from '../types/portfolio'
import { num, pct, usd } from '../lib/format'
import { Disclose } from './Disclose'

type Props = {
  portfolio: PaperPortfolio
}

function lotReason(lot: PortfolioLot): string {
  if (lot.reason) return lot.reason
  if (lot.source === 'drip') return 'Dividend reinvestment'
  if (lot.track === 'dividend') return 'Daily pick, dividend track'
  if (lot.track === 'growth') return 'Daily pick, growth track'
  return 'Daily pick'
}

function sideLabel(side: LotSide | undefined): string {
  return side === 'sell' ? 'Sell' : 'Buy'
}

function journalRows(lots: PortfolioLot[]) {
  let cash = 0
  const chronological = lots.map((lot, index) => {
    if (lot.source === 'pick') cash += lot.costUsd
    return {
      ...lot,
      index,
      side: lot.side ?? 'buy',
      reason: lotReason(lot),
      cashInvestedAfter: lot.cashInvestedAfter ?? cash,
    }
  })
  return chronological.slice().reverse()
}

export function PortfolioPanel({ portfolio }: Props) {
  const s = portfolio.summary
  const fills = journalRows(portfolio.lots || [])

  return (
    <Disclose
      className="panel"
      startOpen
      summary={
        <>
          <span className="eyebrow">Paper portfolio</span>
          <span className="disclose-title">Shared ledger as of {portfolio.asOf}</span>
          <span className="disclose-hint muted">
            {usd(portfolio.buyAmountUsd, 0)} per unique daily pick · repeat buys while still listed
          </span>
        </>
      }
    >
      <div className="disclose-body">
        <p className="lede portfolio-lede">
          Each unique ticker on a day's pick list is bought for{' '}
          {usd(portfolio.buyAmountUsd, 0)}. If it is still on the next day's unique list,
          another lot is bought. Dividends are reinvested when payout data is available.
          Figures are the same for every visitor.
        </p>

        <div className="stat-row">
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

        <Disclose
          className="subfold"
          startOpen
          summaryClassName="disclose-summary disclose-summary-nested"
          summary={
            <>
              <span className="disclose-title disclose-title-nested">Holdings</span>
              <span className="disclose-hint muted">
                {s.positionCount === 0
                  ? 'No positions yet'
                  : `${s.positionCount} position${s.positionCount === 1 ? '' : 's'}`}
              </span>
            </>
          }
        >
          <div className="disclose-body">
            {portfolio.positions.length === 0 ? (
              <p className="empty">No positions in the ledger yet.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table">
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
                        <td data-label="Ticker">
                          <strong>{p.ticker}</strong>
                          <span className="sub">{p.name}</span>
                        </td>
                        <td data-label="Shares">{num(p.shares, 4)}</td>
                        <td data-label="DCA">{usd(p.dca)}</td>
                        <td data-label="Price">{usd(p.currentPrice)}</td>
                        <td data-label="Market value">{usd(p.marketValue)}</td>
                        <td data-label="Cash in">{usd(p.cashInvested)}</td>
                        <td data-label="Dividends">{usd(p.dividendsReceived, 4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Disclose>

        <Disclose
          className="subfold journal"
          summaryClassName="disclose-summary disclose-summary-nested"
          summary={
            <>
              <span className="disclose-title disclose-title-nested">Transactions</span>
              <span className="disclose-hint muted">
                {fills.length === 0
                  ? 'No fills recorded yet'
                  : `${fills.length} fill${fills.length === 1 ? '' : 's'}, newest first`}
              </span>
            </>
          }
        >
          <div className="disclose-body">
            {fills.length === 0 ? (
              <p className="empty">No fills recorded yet.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Ticker</th>
                      <th>Side</th>
                      <th>Shares</th>
                      <th>Price</th>
                      <th>Cash invested after</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fills.map((lot) => (
                      <tr key={`${lot.asOf}-${lot.ticker}-${lot.source}-${lot.index}`}>
                        <td data-label="Date">{lot.asOf}</td>
                        <td data-label="Ticker">
                          <strong>{lot.ticker}</strong>
                        </td>
                        <td data-label="Side">{sideLabel(lot.side)}</td>
                        <td data-label="Shares">{num(lot.shares, 4)}</td>
                        <td data-label="Price">{usd(lot.price)}</td>
                        <td data-label="Cash invested after">{usd(lot.cashInvestedAfter)}</td>
                        <td data-label="Reason">{lot.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Disclose>
      </div>
    </Disclose>
  )
}
