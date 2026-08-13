import { useMemo } from 'react'

/** Small deterministic string hash — same seed always yields the same art. */
function hash(seed: string): number {
  let h = 2166136261
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

function rng(seed: string) {
  let s = hash(seed) || 1
  return () => {
    s ^= s << 13
    s ^= s >>> 17
    s ^= s << 5
    return Math.abs(s % 10000) / 10000
  }
}

type Props = {
  seed: string
  /** Optional real asset. When present it wins over the procedural art. */
  src?: string
  alt: string
  accent?: boolean
  ratio?: string
  className?: string
  priority?: boolean
}

/**
 * Poster art for cards and step rows.
 *
 * The repo ships without binary assets, so the default is a deterministic
 * generated SVG composition — it costs no request, cannot shift layout, and
 * gives each template a distinct identity. Pass `src` (an AVIF or WebP path
 * under /public) once real renders exist and the same box serves them, with
 * next-gen sources and lazy loading already wired.
 */
export function Artwork({
  seed,
  src,
  alt,
  accent = false,
  ratio = '16 / 10',
  className = '',
  priority = false,
}: Props) {
  const art = useMemo(() => {
    const r = rng(seed)
    const hue = Math.round(r() * 360)
    // Kept inside the 100×62 frame so no mark is sliced by the card edge.
    const bars = Array.from({ length: 5 }, () => ({
      x: 8 + r() * 62,
      y: 10 + r() * 42,
      w: 6 + r() * 26,
      h: 1.2 + r() * 3,
      o: 0.12 + r() * 0.4,
    }))
    const orbit = 18 + r() * 22
    const tilt = -24 + r() * 48
    return { hue, bars, orbit, tilt }
  }, [seed])

  const gid = `g-${seed}`

  return (
    <div
      className={`relative overflow-hidden rounded-[12px] border border-hairline bg-[#0D0D0D] ${className}`}
      style={{ aspectRatio: ratio }}
    >
      {src ? (
        <picture>
          <source srcSet={src.replace(/\.\w+$/, '.avif')} type="image/avif" />
          <source srcSet={src.replace(/\.\w+$/, '.webp')} type="image/webp" />
          <img
            src={src}
            alt={alt}
            loading={priority ? 'eager' : 'lazy'}
            decoding="async"
            fetchPriority={priority ? 'high' : 'low'}
            className="h-full w-full object-cover"
          />
        </picture>
      ) : (
        <svg
          viewBox="0 0 100 62"
          preserveAspectRatio="xMidYMid slice"
          role="img"
          aria-label={alt}
          className="h-full w-full"
        >
          <defs>
            <radialGradient id={`${gid}-a`} cx="28%" cy="18%" r="82%">
              <stop
                offset="0%"
                stopColor={accent ? '#D4FF4F' : `hsl(${art.hue} 40% 62%)`}
                stopOpacity={accent ? 0.34 : 0.24}
              />
              <stop offset="70%" stopColor="#0A0A0A" stopOpacity="0" />
            </radialGradient>
            <radialGradient id={`${gid}-b`} cx="78%" cy="88%" r="70%">
              <stop offset="0%" stopColor="#FAFAFA" stopOpacity="0.13" />
              <stop offset="100%" stopColor="#0A0A0A" stopOpacity="0" />
            </radialGradient>
            <linearGradient id={`${gid}-c`} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#FAFAFA" stopOpacity="0.16" />
              <stop offset="100%" stopColor="#FAFAFA" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          <rect width="100" height="62" fill="#0D0D0D" />
          <rect width="100" height="62" fill={`url(#${gid}-a)`} />
          <rect width="100" height="62" fill={`url(#${gid}-b)`} />

          {/* Structural marks: a hairline grid reading as a layout wireframe. */}
          <g stroke="#FAFAFA" strokeOpacity="0.06" strokeWidth="0.25">
            <line x1="0" y1="15.5" x2="100" y2="15.5" />
            <line x1="0" y1="46.5" x2="100" y2="46.5" />
            <line x1="33" y1="0" x2="33" y2="62" />
            <line x1="67" y1="0" x2="67" y2="62" />
          </g>

          <g transform={`rotate(${art.tilt} 50 31)`}>
            <circle
              cx="50"
              cy="31"
              r={art.orbit}
              fill="none"
              stroke={accent ? '#D4FF4F' : '#FAFAFA'}
              strokeOpacity={accent ? 0.5 : 0.18}
              strokeWidth="0.4"
            />
            <rect
              x={50 - art.orbit * 0.62}
              y={31 - art.orbit * 0.38}
              width={art.orbit * 1.24}
              height={art.orbit * 0.76}
              rx="2"
              fill={`url(#${gid}-c)`}
              stroke="#FAFAFA"
              strokeOpacity="0.1"
              strokeWidth="0.25"
            />
          </g>

          {art.bars.map((b, i) => (
            <rect
              key={i}
              x={b.x}
              y={b.y}
              width={b.w}
              height={b.h}
              rx={b.h / 2}
              fill={accent && i === 0 ? '#D4FF4F' : '#FAFAFA'}
              fillOpacity={accent && i === 0 ? 0.72 : b.o * 0.5}
            />
          ))}
        </svg>
      )}

      {/* Soft vignette keeps the card edge from competing with the copy. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'linear-gradient(180deg, rgba(10,10,10,0) 40%, rgba(10,10,10,0.55) 100%)',
        }}
      />
    </div>
  )
}
