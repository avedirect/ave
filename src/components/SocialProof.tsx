import { SectionHead } from './SectionHead'
import { stats, testimonials } from '../data/content'

export function SocialProof() {
  return (
    <section id="proof" className="section container-page scroll-mt-24">
      {/* Stat band */}
      <dl className="reveal grid grid-cols-2 gap-px overflow-hidden rounded-card border border-hairline bg-hairline md:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-obsidian px-6 py-8 md:px-8 md:py-10">
            <dt className="sr-only">{s.label}</dt>
            <dd>
              <span className="block text-h2 font-medium tabular-nums">{s.value}</span>
              <span className="mt-2 block font-mono text-mono uppercase tracking-[0.18em] text-ink-faint">
                {s.label}
              </span>
            </dd>
          </div>
        ))}
      </dl>

      <div className="mt-24">
        <SectionHead
          eyebrow="Social proof"
          title={
            <>
              People who stopped{' '}
              <span className="font-display italic font-normal">rebuilding templates.</span>
            </>
          }
        />
      </div>

      {/* Testimonial wall — CSS columns keep the ragged, editorial rhythm. */}
      <ul className="mt-14 columns-1 gap-gutter md:columns-2 lg:columns-3 [column-fill:_balance]">
        {testimonials.map((t) => (
          <li key={t.name} className="reveal mb-gutter break-inside-avoid">
            <figure className="surface-card p-7 transition-colors duration-300 ease-out [@media(hover:hover)]:hover:bg-surface-hover">
              <span aria-hidden="true" className="block font-display text-[40px] leading-none text-lime">
                &ldquo;
              </span>
              <blockquote className="mt-3 text-[17px] leading-[1.55] text-ink text-pretty">
                {t.quote}
              </blockquote>
              <figcaption className="mt-6 flex items-center gap-3 border-t border-hairline pt-5">
                <span
                  aria-hidden="true"
                  className="grid h-9 w-9 shrink-0 place-items-center rounded-pill border border-hairline bg-surface font-mono text-[11px] text-ink-muted"
                >
                  {t.name
                    .split(' ')
                    .map((p) => p[0])
                    .join('')}
                </span>
                <span className="text-[14px]">
                  <span className="block text-ink">{t.name}</span>
                  <span className="block text-ink-muted">{t.role}</span>
                </span>
              </figcaption>
            </figure>
          </li>
        ))}
      </ul>
    </section>
  )
}
