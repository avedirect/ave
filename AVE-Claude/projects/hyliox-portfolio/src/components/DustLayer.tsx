import { useEffect, useRef } from 'react'
import { usePrefersReducedMotion } from '../lib/hooks'

type Particle = { x: number; y: number; r: number; vx: number; vy: number; a: number }

/**
 * Drifting dust over the hero video. Canvas rather than DOM nodes so a few
 * dozen particles cost one composited layer instead of dozens. Skipped
 * entirely for reduced motion, and thinned out on small screens.
 */
export function DustLayer() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const reduced = usePrefersReducedMotion()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || reduced) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let frame = 0
    let particles: Particle[] = []
    let w = 0
    let h = 0
    const dpr = Math.min(window.devicePixelRatio || 1, 2)

    const seed = () => {
      const rect = canvas.getBoundingClientRect()
      w = rect.width
      h = rect.height
      canvas.width = Math.floor(w * dpr)
      canvas.height = Math.floor(h * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const count = w < 768 ? 26 : 64
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.4 + Math.random() * 1.3,
        vx: (Math.random() - 0.5) * 0.14,
        vy: -0.06 - Math.random() * 0.18,
        a: 0.06 + Math.random() * 0.3,
      }))
    }

    const draw = () => {
      ctx.clearRect(0, 0, w, h)
      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        if (p.y < -4) {
          p.y = h + 4
          p.x = Math.random() * w
        }
        if (p.x < -4) p.x = w + 4
        if (p.x > w + 4) p.x = -4

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(250,250,250,${p.a})`
        ctx.fill()
      }
      frame = requestAnimationFrame(draw)
    }

    const start = () => {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(draw)
    }
    const stop = () => cancelAnimationFrame(frame)

    seed()
    start()

    const onResize = () => {
      seed()
    }
    // Pause when the hero scrolls away or the tab is backgrounded.
    const io = new IntersectionObserver(
      ([entry]) => (entry.isIntersecting && !document.hidden ? start() : stop()),
      { threshold: 0 },
    )
    io.observe(canvas)
    const onVisibility = () => (document.hidden ? stop() : start())

    window.addEventListener('resize', onResize)
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      stop()
      io.disconnect()
      window.removeEventListener('resize', onResize)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [reduced])

  if (reduced) return null

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 h-full w-full"
    />
  )
}
