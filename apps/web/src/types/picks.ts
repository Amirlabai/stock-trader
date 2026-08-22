export interface AaoifiRatios {
  debtToMarketCap: number | null;
  cashToMarketCap: number | null;
  receivablesToMarketCap: number | null;
  mcBasis: "trailing_24m" | "spot" | "unknown";
  interestIncomeNonOp: number | null;
  purificationPerShare: number | null;
}

export interface DividendPick {
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

export interface GrowthPick {
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
