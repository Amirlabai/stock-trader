export type MdInline =
  | { type: 'text'; text: string }
  | { type: 'code'; text: string }

export type MdBlock =
  | { type: 'heading'; level: 1 | 2 | 3; text: string }
  | { type: 'paragraph'; parts: MdInline[] }
  | { type: 'table'; headers: string[]; rows: string[][] }

const DEV_COLUMNS = new Set(['code'])

function splitCells(line: string): string[] {
  return line
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim())
}

function isSeparatorRow(line: string): boolean {
  return /^\|?\s*:?-{3,}/.test(line)
}

function parseInline(text: string): MdInline[] {
  const parts: MdInline[] = []
  const re = /`([^`]+)`/g
  let last = 0
  let match: RegExpExecArray | null
  while ((match = re.exec(text)) !== null) {
    if (match.index > last) {
      parts.push({ type: 'text', text: text.slice(last, match.index) })
    }
    parts.push({ type: 'code', text: match[1] })
    last = match.index + match[0].length
  }
  if (last < text.length) {
    parts.push({ type: 'text', text: text.slice(last) })
  }
  return parts.length > 0 ? parts : [{ type: 'text', text }]
}

function stripDevColumns(headers: string[], rows: string[][]): {
  headers: string[]
  rows: string[][]
} {
  const keep = headers.map((h, i) => ({ h, i })).filter(({ h }) => !DEV_COLUMNS.has(h.toLowerCase()))
  return {
    headers: keep.map(({ h }) => h),
    rows: rows.map((row) => keep.map(({ i }) => row[i] ?? '')),
  }
}

/** Lightweight markdown parse for SCREEN_PARAMETERS.md (headings, paragraphs, tables). */
export function parseScreenParametersMarkdown(source: string): MdBlock[] {
  const lines = source.replace(/\r\n/g, '\n').split('\n')
  const blocks: MdBlock[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]
    const trimmed = line.trim()

    if (!trimmed) {
      i += 1
      continue
    }

    const heading = /^(#{1,3})\s+(.+)$/.exec(trimmed)
    if (heading) {
      blocks.push({
        type: 'heading',
        level: heading[1].length as 1 | 2 | 3,
        text: heading[2].trim(),
      })
      i += 1
      continue
    }

    if (trimmed.startsWith('|') && i + 1 < lines.length && isSeparatorRow(lines[i + 1].trim())) {
      const headers = splitCells(trimmed)
      i += 2
      const rows: string[][] = []
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        if (!isSeparatorRow(lines[i].trim())) {
          rows.push(splitCells(lines[i].trim()))
        }
        i += 1
      }
      const cleaned = stripDevColumns(headers, rows)
      if (cleaned.headers.length > 0) {
        blocks.push({ type: 'table', headers: cleaned.headers, rows: cleaned.rows })
      }
      continue
    }

    const para: string[] = [trimmed]
    i += 1
    while (i < lines.length) {
      const next = lines[i].trim()
      if (!next || next.startsWith('#') || next.startsWith('|')) break
      para.push(next)
      i += 1
    }
    blocks.push({ type: 'paragraph', parts: parseInline(para.join(' ')) })
  }

  return blocks
}

/** Drop the H1 and engineer-only asides; UI supplies its own title. */
export function blocksForUserView(blocks: MdBlock[]): MdBlock[] {
  const out: MdBlock[] = []
  let skippedTitle = false
  for (const block of blocks) {
    if (!skippedTitle && block.type === 'heading' && block.level === 1) {
      skippedTitle = true
      continue
    }
    if (block.type === 'paragraph') {
      const plain = block.parts.map((p) => p.text).join('')
      if (/source of truth for runtime values/i.test(plain)) continue
      if (/synced into .*screen-parameters/i.test(plain)) continue
      if (/^see [`']?\w+\.py/i.test(plain.trim())) continue
    }
    if (block.type === 'table') {
      const paramIdx = block.headers.findIndex((h) => /^parameter$/i.test(h))
      const rows =
        paramIdx >= 0
          ? block.rows.filter((row) => !/fetch sleep/i.test(row[paramIdx] ?? ''))
          : block.rows
      out.push({ ...block, rows })
      continue
    }
    out.push(block)
  }
  return out
}
