import { footerColumns } from '../data/content'

export function Footer() {
  return (
    <footer className="container-page pb-16 pt-24">
      <div className="grid-12 gap-y-14">
        {/* Brand mark */}
        <div className="col-span-4 md:col-span-12 lg:col-span-3">
          <span
            className="font-sans text-[13px] font-medium uppercase tracking-eyebrow text-ink"
            style={{ textIndent: '0.4em' }}
          >
            HYLIOX
          </span>
          <p className="mt-5 max-w-[28ch] text-[15px] leading-relaxed text-ink-muted">
            Premium templates for people who use AI to build, not to decide.
          </p>
        </div>

        {footerColumns.map((col) => (
          <nav
            key={col.title}
            aria-label={col.title}
            className="col-span-2 md:col-span-4 lg:col-span-3"
          >
            <h2 className="font-mono text-mono uppercase tracking-[0.18em] text-ink-faint">
              {col.title}
            </h2>
            <ul className="mt-5 flex flex-col gap-3">
              {col.links.map((link) => (
                <li key={link}>
                  <a href="#top" className="link-quiet text-[15px]">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        ))}
      </div>

      <div className="mt-20 flex flex-col gap-4 border-t border-hairline pt-8 font-mono text-mono text-ink-faint sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} Hyliox. All rights reserved.</p>
        <p>Built with AI · Not by AI</p>
      </div>
    </footer>
  )
}
