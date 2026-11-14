import type { ReactNode } from 'react'

export function SectionHead({
  eyebrow,
  title,
  sub,
  align = 'left',
}: {
  eyebrow: string
  title: ReactNode
  sub?: string
  align?: 'left' | 'center'
}) {
  return (
    <div
      className={`reveal flex flex-col ${
        align === 'center' ? 'items-center text-center' : 'items-start'
      }`}
    >
      <p className="eyebrow">{eyebrow}</p>
      <h2 className="mt-6 max-w-[20ch] text-h1 font-medium text-balance">{title}</h2>
      {sub && (
        <p
          className={`mt-5 max-w-[52ch] text-body text-ink-muted text-pretty ${
            align === 'center' ? 'mx-auto' : ''
          }`}
        >
          {sub}
        </p>
      )}
    </div>
  )
}
