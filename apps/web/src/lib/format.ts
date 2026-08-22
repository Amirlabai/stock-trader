export function pct(value: number | null | undefined, digits = 1): string {
  if (value == null || Number.isNaN(value)) return '-'
  return `${(value * 100).toFixed(digits)}%`
}

export function num(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) return '-'
  return value.toFixed(digits)
}

export function usd(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) return '-'
  return `$${value.toFixed(digits)}`
}

export function score(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return '-'
  return value.toFixed(1)
}
