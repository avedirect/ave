import { useEffect } from 'react'

function revealAll() {
  document
    .querySelectorAll<HTMLElement>('.reveal')
    .forEach((el) => el.classList.add('is-revealed'))
}

/**
 * Scroll-triggered section reveals.
 *
 * GSAP + ScrollTrigger are imported dynamically so they stay out of the
 * critical path — the hero paints before the animation engine is parsed.
 *
 * `started` gates setup until the loading screen is gone, so nothing reveals
 * behind it. Reduced-motion visitors — and anyone whose GSAP chunk fails to
 * load — get every element switched straight to its resolved state, so
 * content is never left invisible.
 */
export function useScrollReveal({ started, reduced }: { started: boolean; reduced: boolean }) {
  useEffect(() => {
    if (reduced) {
      revealAll()
      return
    }
    if (!started) return

    let cancelled = false
    let cleanup: (() => void) | undefined

    void (async () => {
      const mods = await Promise.all([import('gsap'), import('gsap/ScrollTrigger')]).catch(
        (err: unknown) => {
          console.warn('[reveal] animation chunk failed to load', err)
          revealAll()
          return null
        },
      )
      if (cancelled || !mods) return

      const [{ gsap }, { ScrollTrigger }] = mods
      gsap.registerPlugin(ScrollTrigger)

      const ctx = gsap.context(() => {
        ScrollTrigger.batch('.reveal', {
          start: 'top 88%',
          once: true,
          onEnter: (batch) => {
            gsap.to(batch, {
              opacity: 1,
              y: 0,
              duration: 0.9,
              ease: 'power3.out',
              stagger: 0.08,
              overwrite: true,
              onComplete: () =>
                batch.forEach((el) => (el as HTMLElement).classList.add('is-revealed')),
            })
          },
        })

        // Anything already in view on load resolves immediately rather than
        // waiting for a scroll that may never come.
        ScrollTrigger.refresh()
      })

      cleanup = () => ctx.revert()
    })()

    return () => {
      cancelled = true
      cleanup?.()
    }
  }, [started, reduced])
}

/**
 * Desktop-only parallax: drifts an element on scroll. No-ops on touch /
 * reduced motion so mobile keeps a flat, cheap scroll.
 */
export function useParallax(
  ref: React.RefObject<HTMLElement | null>,
  { enabled, distance = 80 }: { enabled: boolean; distance?: number },
) {
  useEffect(() => {
    const el = ref.current
    if (!el || !enabled) return

    let cancelled = false
    let cleanup: (() => void) | undefined

    void (async () => {
      const [{ gsap }, { ScrollTrigger }] = await Promise.all([
        import('gsap'),
        import('gsap/ScrollTrigger'),
      ])
      if (cancelled || !ref.current) return
      gsap.registerPlugin(ScrollTrigger)

      const tween = gsap.fromTo(
        ref.current,
        { y: -distance / 2 },
        {
          y: distance / 2,
          ease: 'none',
          scrollTrigger: {
            trigger: ref.current,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
          },
        },
      )

      cleanup = () => {
        tween.scrollTrigger?.kill()
        tween.kill()
      }
    })()

    return () => {
      cancelled = true
      cleanup?.()
    }
  }, [ref, enabled, distance])
}
