export interface AaoifiRatios {
  debtToMarketCap: number | null;
  cashToMarketCap: number | null;
  receivablesToMarketCap: number | null;
  mcBasis: "trailing_24m" | "spot" | "unknown";
  interestIncomeNonOp: number | null;
  purificationPerShare: number | null;
}

/** Valuation multiples. Informational; null when Yahoo has no usable figure. */
export interface Valuation {
  pe?: number | null;
  peg?: number | null;
  pb?: number | null;
  /** Gordon model fair value in the listing currency (dividend track only). */
  gordonFairValue?: number | null;
  /** Gordon fair value / price - 1 (dividend track only). */
  marginOfSafety?: number | null;
}

export interface DividendPick extends Valuation {
  ticker: string;
  name: string;
  sector: string;
  region: string;
  currency?: string;
  price: number;
  priceLocal?: number | null;
  yield: number;
  divCagr5y: number | null;
  fcfPayout: number | null;
  score: number;
  purificationPerShare: number | null;
  ratios: AaoifiRatios;
}

export interface GrowthPick extends Valuation {
  ticker: string;
  name: string;
  sector: string;
  region: string;
  currency?: string;
  price: number;
  priceLocal?: number | null;
  revGrowthTtm: number | null;
  fwdEpsGrowth: number | null;
  debtToMc: number | null;
  score: number;
  purificationPerShare: number | null;
  ratios: AaoifiRatios;
}

export interface DailyPicks {
  asOf: string;
  buyAmountUsd: number;
  dividendPicks: DividendPick[];
  growthPicks: GrowthPick[];
  meta?: {
    universeSize: number;
    compliantCount: number;
    notes?: string[];
  };
}
