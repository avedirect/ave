import { Artwork } from './Artwork'
import { SectionHead } from './SectionHead'
import { templates, type Template } from '../data/content'

// Static class strings — Tailwind needs to see the full name to emit it.
const spanClass: Record<Template['span'], string> = {
  4: 'md:col-span-4',
  6: 'md:col-span-6',
  8: 'md:col-span-8',
  12: 'md:col-span-12',
}

function Card({ t, index }: { t: Template; index: number }) {
  const wide = t.span >= 8

  return (
    <a
      href={`#${t.id}`}
      aria-label={`${t.name} — ${t.subtitle}`}
      className={`reveal group col-span-4 ${spanClass[t.span]} surface-card relative flex flex-col overflow-hidden p-3 transition-[transform,background-color,border-color,box-shadow] duration-300 ease-out [@media(hover:hover)]:hover:-translate-y-1.5 [@media(hover:hover)]:hover:bg-surface-hover ${
        t.featured
          ? 'border-lime-line [@media(hover:hover)]:hover:shadow-[0_24px_60px_-32px_rgba(212,255,79,0.45)]'
          : '[@media(hover:hover)]:hover:border-white/10'
      }`}
    >
      <div className={wide ? 'flex flex-col gap-3 md:flex-row md:items-stretch' : ''}>
        <Artwork
          seed={t.id}
          alt={`${t.name} template preview`}
          accent={t.featured}
          ratio={wide ? '16 / 9' : '16 / 10'}
          priority={index < 2}
          className={wide ? 'md:w-[62%]' : ''}
        />

        <div
          className={`flex flex-1 flex-col justify-between gap-6 px-3 pb-3 pt-5 ${
            wide ? 'md:px-6 md:py-6' : ''
          }`}
        >
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-h3 font-medium">{t.name}</h3>
              {t.featured && (
                <span className="rounded-pill bg-lime px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-obsidian">
                  Featured
                </span>
              )}
            </div>
            <p className="mt-2 max-w-[38ch] text-[15px] leading-relaxed text-ink-muted">
              {t.subtitle}
            </p>
          </div>

          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint">
              {t.tag}
            </span>
            <span
              aria-hidden="true"
              className="text-[15px] text-ink-faint transition-[color,transform] duration-300 ease-out group-hover:translate-x-0.5 group-hover:text-lime"
            >
              →
            </span>
          </div>
        </div>
      </div>
    </a>
  )
}

export function Templates() {
  return (
    <section id="templates" className="section container-page scroll-mt-24">
      <SectionHead
        eyebrow="The library"
        title={
          <>
            Eight directions,{' '}
            <span className="font-display italic font-normal">not eight variations.</span>
          </>
        }
        sub="Each one is a finished point of view — art direction, motion budget and component system written down before a single line was generated."
      />

      <div className="mt-16 grid-12">
        {templates.map((t, i) => (
          <Card key={t.id} t={t} index={i} />
        ))}
      </div>
    </section>
  )
}
