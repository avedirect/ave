import { useEffect, useState } from 'react'

const links = [
  { href: '#templates', label: 'Templates' },
  { href: '#method', label: 'Method' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#faq', label: 'FAQ' },
]

export function Nav() {
  const [solid, setSolid] = useState(false)

  useEffect(() => {
    const onScroll = () => setSolid(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-300 ease-out ${
        solid ? 'glass border-b border-hairline' : 'border-b border-transparent'
      }`}
    >
      <nav
        aria-label="Primary"
        className="container-page flex h-16 items-center justify-between gap-6"
      >
        <a
          href="#top"
          className="font-sans text-[13px] font-medium uppercase tracking-eyebrow text-ink"
          style={{ textIndent: '0.4em' }}
        >
          HYLIOX
        </a>

        <ul className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <li key={l.href}>
              <a href={l.href} className="link-quiet text-[14px]">
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        <a href="#templates" className="btn-ghost h-10 px-4 py-0 text-[14px]">
          Browse templates
        </a>
      </nav>
    </header>
  )
}
