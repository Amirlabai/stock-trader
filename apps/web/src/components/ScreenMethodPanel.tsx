import {
  blocksForUserView,
  parseScreenParametersMarkdown,
  type MdBlock,
  type MdInline,
} from '../lib/parseScreenMd'
import screenParametersMarkdown from '../content/screen-parameters.md?raw'

function InlineParts({ parts }: { parts: MdInline[] }) {
  return (
    <>
      {parts.map((part, i) =>
        part.type === 'code' ? (
          <code key={i}>{part.text}</code>
        ) : (
          <span key={i}>{part.text}</span>
        ),
      )}
    </>
  )
}

function MethodTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="table-wrap">
      <table className="data-table method-table">
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              {headers.map((h, ci) => (
                <td key={h} data-label={h}>
                  {row[ci] ?? ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function BlockView({ block }: { block: MdBlock }) {
  if (block.type === 'heading') {
    if (block.level === 1) return <h2>{block.text}</h2>
    return <h3 className="method-h3">{block.text}</h3>
  }
  if (block.type === 'paragraph') {
    return (
      <p className="method-copy">
        <InlineParts parts={block.parts} />
      </p>
    )
  }
  return <MethodTable headers={block.headers} rows={block.rows} />
}

const blocks: MdBlock[] = blocksForUserView(
  parseScreenParametersMarkdown(screenParametersMarkdown),
)

export function ScreenMethodPanel() {
  return (
    <details className="panel method-panel" id="how-we-pick">
      <summary className="method-summary">
        <span className="eyebrow">Methodology</span>
        <span className="method-summary-title">How stocks are picked</span>
        <span className="method-summary-hint muted">
          Thresholds, AAOIFI-style screens, and strategy scores
        </span>
      </summary>

      <p className="lede method-lede">
        Thresholds applied in order: universe, Tier 1 activity screen, Tier 2 AAOIFI-style
        ratios, then the dividend or growth strategy score.
      </p>

      <div className="method-body">
        {blocks.map((block, i) => (
          <BlockView key={i} block={block} />
        ))}
      </div>
    </details>
  )
}
