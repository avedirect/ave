import { useEffect, useRef, useState } from 'react'
import { usePrefersReducedMotion } from '../lib/hooks'

/**
 * Point this at your own HLS manifest via `VITE_HERO_HLS_SRC`. The default is
 * a public test stream so the hero is cinematic out of the box; if it fails to
 * load, the gradient underneath is a complete fallback on its own.
 */
const DEFAULT_SRC =
  import.meta.env.VITE_HERO_HLS_SRC ??
  'https://stream.mux.com/v69RSHhFelSm4701snP22dYz2jICy4E4FUyk02rW4gxRM.m3u8'

/**
 * Full-bleed HLS video backdrop.
 *
 * hls.js is code-split and only fetched when the browser actually needs it —
 * Safari plays HLS natively, and reduced-motion visitors never load it at all.
 * A CSS gradient sits behind the video and carries the section by itself when
 * playback is unavailable, so the hero never renders as a black hole.
 */
export function HlsBackdrop({ src = DEFAULT_SRC }: { src?: string }) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [playing, setPlaying] = useState(false)
  const reduced = usePrefersReducedMotion()

  useEffect(() => {
    const video = videoRef.current
    if (!video || !src || reduced) return

    let destroy: (() => void) | undefined
    let cancelled = false

    const onPlaying = () => setPlaying(true)
    video.addEventListener('playing', onPlaying)

    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = src
      void video.play().catch(() => undefined)
    } else {
      void import('hls.js').then(({ default: Hls }) => {
        if (cancelled || !videoRef.current || !Hls.isSupported()) return
        const hls = new Hls({ enableWorker: true, lowLatencyMode: false, capLevelToPlayerSize: true })
        hls.loadSource(src)
        hls.attachMedia(videoRef.current)
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          void videoRef.current?.play().catch(() => undefined)
        })
        hls.on(Hls.Events.ERROR, (_e, data) => {
          if (data.fatal) {
            setPlaying(false)
            hls.destroy()
          }
        })
        destroy = () => hls.destroy()
      })
    }

    return () => {
      cancelled = true
      video.removeEventListener('playing', onPlaying)
      destroy?.()
    }
  }, [src, reduced])

  return (
    <div aria-hidden="true" className="absolute inset-0 overflow-hidden">
      {/* Gradient ground — also the full fallback when video does not play. */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(120% 90% at 50% 8%, rgba(212,255,79,0.10) 0%, rgba(10,10,10,0) 58%), radial-gradient(90% 70% at 78% 92%, rgba(120,140,255,0.10) 0%, rgba(10,10,10,0) 60%), #0A0A0A',
        }}
      />

      {!reduced && (
        <video
          ref={videoRef}
          muted
          loop
          playsInline
          preload="none"
          tabIndex={-1}
          className="absolute inset-0 h-full w-full object-cover transition-opacity duration-[1200ms] ease-out"
          style={{ opacity: playing ? 0.55 : 0 }}
        />
      )}

      {/* 50% black scrim so headline contrast holds over any frame. */}
      <div className="absolute inset-0 bg-black/50" />

      {/* Bottom fade into the next section. */}
      <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent to-obsidian" />
    </div>
  )
}
