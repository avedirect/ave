import { useState } from 'react'
import { Loader } from './components/Loader'
import { Nav } from './components/Nav'
import { Hero } from './components/Hero'
import { Templates } from './components/Templates'
import { HowItWorks } from './components/HowItWorks'
import { SocialProof } from './components/SocialProof'
import { Pricing } from './components/Pricing'
import { Faq } from './components/Faq'
import { FinalCta } from './components/FinalCta'
import { Footer } from './components/Footer'
import { usePrefersReducedMotion } from './lib/hooks'
import { useScrollReveal } from './lib/scrollReveal'

export default function App() {
  const [ready, setReady] = useState(false)
  const reduced = usePrefersReducedMotion()

  useScrollReveal({ started: ready, reduced })

  return (
    <>
      <Loader onDone={() => setReady(true)} />

      <a
        href="#templates"
        className="sr-only focus:not-sr-only focus:fixed focus:left-6 focus:top-6 focus:z-[110] focus:rounded-pill focus:bg-lime focus:px-5 focus:py-3 focus:text-[14px] focus:font-medium focus:text-obsidian"
      >
        Skip to content
      </a>

      <Nav />

      <main>
        <Hero ready={ready} />
        <Templates />
        <HowItWorks />
        <SocialProof />
        <Pricing />
        <Faq />
        <FinalCta />
      </main>

      <Footer />
    </>
  )
}
