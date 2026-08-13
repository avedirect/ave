import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { usePrefersReducedMotion } from '../lib/hooks'

const HOLD_MS = 3000
const REDUCED_HOLD_MS = 400

/**
 * Monogram loading screen. Holds for 3s, then fades out on an ease-out curve.
 * Reduced-motion visitors get the same screen without the shimmer and with a
 * short hold, so nothing is gated behind an animation they cannot see.
 */
export function Loader({ onDone }: { onDone: () => void }) {
  const reduced = usePrefersReducedMotion()
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    // The static shell in index.html has done its job once React is up.
    document.getElementById('boot')?.remove()
  }, [])

  useEffect(() => {
    const hold = reduced ? REDUCED_HOLD_MS : HOLD_MS
    document.documentElement.style.overflow = 'hidden'
    const t = window.setTimeout(() => setVisible(false), hold)
    return () => {
      window.clearTimeout(t)
      document.documentElement.style.overflow = ''
    }
  }, [reduced])

  return (
    <AnimatePresence
      onExitComplete={() => {
        document.documentElement.style.overflow = ''
        onDone()
      }}
    >
      {visible && (
        <motion.div
          key="loader"
          className="fixed inset-0 z-[100] grid place-items-center bg-obsidian"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: reduced ? 0.15 : 0.8, ease: [0.22, 1, 0.36, 1] }}
          role="status"
          aria-live="polite"
          aria-label="Loading HYLIOX"
        >
          <div className="flex flex-col items-center gap-6">
            <span
              className="font-sans text-[13px] font-medium uppercase tracking-eyebrow"
              style={
                reduced
                  ? { color: 'rgba(250,250,250,0.6)', textIndent: '0.4em' }
                  : {
                      textIndent: '0.4em',
                      color: 'transparent',
                      backgroundImage:
                        'linear-gradient(100deg, rgba(250,250,250,0.18) 0%, rgba(250,250,250,0.18) 38%, #D4FF4F 50%, rgba(250,250,250,0.18) 62%, rgba(250,250,250,0.18) 100%)',
                      backgroundSize: '260% 100%',
                      WebkitBackgroundClip: 'text',
                      backgroundClip: 'text',
                      animation: 'shimmer 2.2s cubic-bezier(0.22, 1, 0.36, 1) infinite',
                    }
              }
            >
              HYLIOX
            </span>

            <span className="relative block h-px w-[120px] overflow-hidden bg-white/[0.08]">
              <motion.span
                className="absolute inset-y-0 left-0 block bg-lime"
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{
                  duration: (reduced ? REDUCED_HOLD_MS : HOLD_MS) / 1000,
                  ease: [0.22, 1, 0.36, 1],
                }}
              />
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
