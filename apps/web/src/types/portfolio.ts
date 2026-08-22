export type LotSource = 'pick' | 'drip'
export type LotTrack = 'dividend' | 'growth' | null

export type PortfolioLot = {
  asOf: string
  ticker: string
  name: string
  source: LotSource
  shares: number
  price: number
  costUsd: number
  track: LotTrack
}

export type DividendEvent = {
  asOf: string
  ticker: string
  amountPerShare: number
  sharesHeld: number
  cash: number
  reinvestPrice: number
  sharesBought: number
}

export type PortfolioPosition = {
  ticker: string
  name: string
  shares: number
  cashInvested: number
  dividendsReinvested: number
  totalCostBasis: number
  dca: number
  currentPrice: number
  marketValue: number
  dividendsReceived: number
  firstBuyAsOf: string
  lastBuyAsOf: string
}

export type PortfolioSummary = {
  cashInvested: number
  dividendsReinvested: number
  totalCostBasis: number
  currentValue: number
  unrealizedPnl: number
  returnPct: number | null
  positionCount: number
  dividendEventCount: number
}

export type PaperPortfolio = {
  asOf: string
  buyAmountUsd: number
  summary: PortfolioSummary
  positions: PortfolioPosition[]
  lots: PortfolioLot[]
  dividendEvents: DividendEvent[]
  lastBuyAsOf: string | null
  lastDividendCheckAsOf: string | null
  generatedAt?: string
}
