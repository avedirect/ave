import { SectionHead } from './SectionHead'
import { tiers, type Tier } from '../data/content'

function Check({ on }: { on: boolean }) {
  return on ? (
    <svg viewBox="0 0 16 16" aria-hidden="true" className="mt-[3px] h-4 w-4 shrink-0 text-lime">
      <path
        d="M3 8.4l3.2 3.2L13 4.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ) : (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className="mt-[3px] h-4 w-4 shrink-0 text-ink-faint opacity-60"
    >
      <path
        d="M4.6 4.6l6.8 6.8M11.4 4.6l-6.8 6.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  )
}

function TierCard({ tier }: { tier: Tier }) {
  return (
    <div
      className={`reveal col-span-4 flex flex-col rounded-card p-8 md:col-span-4 ${
        tier.highlight
          ? 'border border-lime-line bg-surface-raised glow-lime lg:-mt-6 lg:pb-14'
          : 'surface-card'
      }`}
    >
      <p className={`eyebrow ${tier.highlight ? 'text-lime' : '!text-ink-faint'}`}>{tier.eyebrow}</p>

      <h3 className="mt-6 text-h3 font-medium">{tier.name}</h3>
      <p className="mt-2 text-[15px] leading-relaxed text-ink-muted">{tier.blurb}</p>

      <p className="mt-8 flex items-baseline gap-2">
        <span className="text-h1 font-medium tabular-nums leading-none">{tier.price}</span>
        <span className="font-mono text-mono text-ink-faint">one-shot</span>
      </p>

      <ul className="mt-8 flex flex-col gap-3.5 border-t border-hairline pt-8">
        {tier.features.map((f) => (
          <li key={f.label} className="flex items-start gap-3 text-[15px]">
            <Check on={f.included} />
            <span className={f.included ? 'text-ink' : 'text-ink-faint line-through decoration-white/20'}>
              <span className="sr-only">{f.included ? 'Included: ' : 'Not included: '}</span>
              {f.label}
            </span>
          </li>
        ))}
      </ul>

      <a
        href="#templates"
        className={`mt-10 w-full ${tier.highlight ? 'btn-primary' : 'btn-ghost'}`}
      >
        {tier.cta}
      </a>
    </div>
  )
}

export function Pricing() {
  return (
    <section id="pricing" className="section container-page scroll-mt-24">
      <SectionHead
        align="center"
        eyebrow="Pricing"
        title={
          <>
            Pay once.{' '}
            <span className="font-display italic font-normal">Own it forever.</span>
          </>
        }
        sub="No seats, no renewals, no feature gates that appear six months in."
      />

      <div className="mt-16 grid-12 items-start lg:items-center">
        {tiers.map((t) => (
          <TierCard key={t.name} tier={t} />
        ))}
      </div>

      <p className="reveal mt-12 text-center font-mono text-mono text-ink-faint">
        All prices one-shot, no subscription
      </p>
    </section>
  )
}
