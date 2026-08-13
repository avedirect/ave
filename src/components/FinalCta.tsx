const PHRASE = ['Built with AI', 'Not by AI']

function Marquee() {
  // The track holds the phrase list twice; the keyframe translates -50%, so
  // the seam lands exactly where the loop restarts.
  const items = [...PHRASE, ...PHRASE, ...PHRASE, ...PHRASE]

  return (
    <div className="marquee select-none border-y border-hairline py-6">
      <p className="sr-only">Built with AI, not by AI.</p>
      <div className="marquee__track" aria-hidden="true">
        {[0, 1].map((copy) => (
          <div key={copy} className="flex shrink-0">
            {items.map((word, i) => (
              <span
                key={`${copy}-${i}`}
                className="flex shrink-0 items-center gap-8 whitespace-nowrap px-8 font-mono text-mono uppercase tracking-[0.32em] text-ink-muted"
              >
                {word}
                <span className="text-lime">·</span>
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export function FinalCta() {
  return (
    <section id="start" className="relative overflow-hidden scroll-mt-24">
      {/* Radial lime glow, bottom-centre. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-0 h-[70%]"
        style={{
          background:
            'radial-gradient(60% 100% at 50% 100%, rgba(212,255,79,0.16) 0%, rgba(212,255,79,0.04) 38%, rgba(10,10,10,0) 72%)',
        }}
      />

      <div className="container-page relative section pb-24 text-center">
        <p className="reveal eyebrow">Last step</p>

        <h2 className="reveal mt-8 mx-auto max-w-[20ch] text-h1 font-medium text-balance md:text-display">
          Ready to ship?
          <span className="mt-1 block font-display italic font-normal">
            Or still scrolling references?
          </span>
        </h2>

        <div className="reveal mt-11 flex justify-center">
          <a href="#templates" className="btn-primary">
            Browse templates <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      <div className="relative">
        <Marquee />
      </div>
    </section>
  )
}
