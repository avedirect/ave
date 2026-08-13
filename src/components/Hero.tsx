import { motion } from 'framer-motion'
import { HlsBackdrop } from './HlsBackdrop'
import { DustLayer } from './DustLayer'
import { usePrefersReducedMotion } from '../lib/hooks'

export function Hero({ ready }: { ready: boolean }) {
  const reduced = usePrefersReducedMotion()

  const rise = (delay: number) =>
    reduced
      ? { initial: { opacity: 0 }, animate: { opacity: ready ? 1 : 0 }, transition: { duration: 0.3 } }
      : {
          initial: { opacity: 0, y: 22 },
          animate: ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 },
          transition: { duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] as const },
        }

  return (
    <section
      id="top"
      className="relative flex min-h-[100svh] items-center justify-center overflow-hidden"
    >
      <HlsBackdrop />
      <DustLayer />

      <div className="container-page relative z-10 flex flex-col items-center py-32 text-center">
        <motion.p {...rise(0)} className="eyebrow">
          Templates · 2026
        </motion.p>

        <motion.h1
          {...rise(0.08)}
          className="mt-8 max-w-[15ch] text-h1 font-medium text-balance md:text-display"
        >
          Ship a site that{' '}
          <span className="font-display italic font-normal">doesn&rsquo;t feel like AI made it.</span>
        </motion.h1>

        <motion.p {...rise(0.16)} className="mt-7 max-w-[46ch] text-body text-ink-muted text-pretty">
          8 premium templates. Cursor / v0 / Lovable ready.
        </motion.p>

        <motion.div {...rise(0.24)} className="mt-11 flex flex-col items-center gap-3 sm:flex-row">
          <a href="#templates" className="btn-primary w-full sm:w-auto">
            Browse templates <span aria-hidden="true">→</span>
          </a>
          <a href="#method" className="btn-ghost w-full sm:w-auto">
            See the method
          </a>
        </motion.div>
      </div>

      <motion.div
        {...rise(0.4)}
        className="absolute inset-x-0 bottom-8 z-10 flex justify-center"
        aria-hidden="true"
      >
        <span className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-faint">
          Scroll
        </span>
      </motion.div>
    </section>
  )
}
