import { useId, useState } from 'react'
import { SectionHead } from './SectionHead'
import { faq } from '../data/content'

function Item({
  q,
  a,
  open,
  onToggle,
  idBase,
}: {
  q: string
  a: string
  open: boolean
  onToggle: () => void
  idBase: string
}) {
  return (
    <li
      className={`reveal border-b border-hairline transition-[border-color,background-color] duration-300 ease-out ${
        open ? 'border-l-2 border-l-lime bg-surface' : 'border-l-2 border-l-transparent'
      }`}
    >
      <h3>
        <button
          type="button"
          id={`${idBase}-btn`}
          aria-expanded={open}
          aria-controls={`${idBase}-panel`}
          onClick={onToggle}
          className="flex w-full items-start justify-between gap-6 px-5 py-6 text-left text-[18px] font-medium transition-colors duration-200 ease-out [@media(hover:hover)]:hover:text-lime md:px-7"
        >
          <span className="max-w-[46ch]">{q}</span>
          <span
            aria-hidden="true"
            className={`mt-1 shrink-0 text-ink-faint transition-transform duration-300 ease-out ${
              open ? 'rotate-45 text-lime' : ''
            }`}
          >
            <svg viewBox="0 0 16 16" className="h-4 w-4">
              <path
                d="M8 2v12M2 8h12"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </span>
        </button>
      </h3>

      {/* 0fr → 1fr animates to the content's natural height with no JS
          measurement, so there is no jump on resize or font swap. */}
      <div
        id={`${idBase}-panel`}
        role="region"
        aria-labelledby={`${idBase}-btn`}
        // `inert` rather than `hidden`: it takes the collapsed answer out of
        // the tab order and the a11y tree without a display change, which
        // would kill the height transition in both directions.
        {...(open ? {} : ({ inert: '' } as Record<string, string>))}
        className="grid transition-[grid-template-rows,opacity] duration-300 ease-out"
        style={{ gridTemplateRows: open ? '1fr' : '0fr', opacity: open ? 1 : 0 }}
      >
        <div className="overflow-hidden">
          <p className="max-w-[62ch] px-5 pb-7 text-body text-ink-muted text-pretty md:px-7">{a}</p>
        </div>
      </div>
    </li>
  )
}

export function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)
  const idBase = useId()

  return (
    <section id="faq" className="section container-page scroll-mt-24">
      <div className="grid-12 gap-y-14">
        <div className="col-span-4 md:col-span-12 lg:col-span-4">
          <SectionHead
            eyebrow="FAQ"
            title={
              <>
                Questions,{' '}
                <span className="font-display italic font-normal">answered plainly.</span>
              </>
            }
          />
        </div>

        <ul className="col-span-4 border-t border-hairline md:col-span-12 lg:col-span-7 lg:col-start-6">
          {faq.map((item, i) => (
            <Item
              key={item.q}
              q={item.q}
              a={item.a}
              idBase={`${idBase}-${i}`}
              open={openIndex === i}
              onToggle={() => setOpenIndex(openIndex === i ? null : i)}
            />
          ))}
        </ul>
      </div>
    </section>
  )
}
