import { useRef } from 'react'
import { Artwork } from './Artwork'
import { SectionHead } from './SectionHead'
import { useIsDesktop, usePrefersReducedMotion } from '../lib/hooks'
import { useParallax } from '../lib/scrollReveal'
import { steps, type Step } from '../data/content'

function StepRow({ step, index, parallax }: { step: Step; index: number; parallax: boolean }) {
  const artRef = useRef<HTMLDivElement>(null)
  useParallax(artRef, { enabled: parallax, distance: 48 })

  const flipped = index % 2 === 1

  return (
    <div className="grid-12 items-start gap-y-10 lg:gap-y-0">
      {/* Copy column */}
      <div
        className={`reveal col-span-4 md:col-span-6 lg:col-span-5 lg:py-[14vh] ${
          flipped ? 'lg:order-2 lg:col-start-8' : 'lg:order-1'
        }`}
      >
        <span className="font-mono text-mono uppercase tracking-[0.28em] text-lime">{step.n}</span>
        <h3 className="mt-6 max-w-[16ch] text-h2 font-medium text-balance">{step.title}</h3>
        <p className="mt-5 max-w-[46ch] text-body text-ink-muted text-pretty">{step.body}</p>
        <p className="mt-8 border-t border-hairline pt-5 font-mono text-mono text-ink-faint">
          {step.note}
        </p>
      </div>

      {/* Media column — pins on desktop, flows inline everywhere else. */}
      <div
        className={`reveal col-span-4 md:col-span-6 lg:col-span-6 ${
          flipped ? 'lg:order-1 lg:col-start-1' : 'lg:order-2 lg:col-start-7'
        } lg:sticky lg:top-[18vh]`}
      >
        <div ref={artRef} className="surface-card p-2">
          <Artwork seed={`step-${step.n}`} alt={`Step ${step.n}: ${step.title}`} ratio="4 / 3" />
        </div>
      </div>
    </div>
  )
}

export function HowItWorks() {
  const isDesktop = useIsDesktop()
  const reduced = usePrefersReducedMotion()

  return (
    <section id="method" className="section container-page scroll-mt-24">
      <SectionHead
        eyebrow="The method"
        title={
          <>
            Three steps.{' '}
            <span className="font-display italic font-normal">No blank canvas.</span>
          </>
        }
        sub="The reason AI output looks generic is that nobody wrote the rules down. These templates ship the rules."
      />

      <div className="mt-20 flex flex-col gap-24 lg:gap-0">
        {steps.map((s, i) => (
          <StepRow key={s.n} step={s} index={i} parallax={isDesktop && !reduced} />
        ))}
      </div>
    </section>
  )
}
