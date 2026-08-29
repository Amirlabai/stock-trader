import { useState, type ReactNode, type ToggleEvent } from 'react'

type Props = {
  className?: string
  summaryClassName?: string
  startOpen?: boolean
  summary: ReactNode
  children: ReactNode
}

/** Controlled <details> so panels can start open without invalid defaultOpen. */
export function Disclose({
  className,
  summaryClassName = 'disclose-summary',
  startOpen = false,
  summary,
  children,
}: Props) {
  const [open, setOpen] = useState(startOpen)

  return (
    <details
      className={className}
      open={open}
      onToggle={(e: ToggleEvent<HTMLDetailsElement>) => {
        if (e.target !== e.currentTarget) return
        setOpen(e.currentTarget.open)
      }}
    >
      <summary className={summaryClassName}>{summary}</summary>
      {children}
    </details>
  )
}
