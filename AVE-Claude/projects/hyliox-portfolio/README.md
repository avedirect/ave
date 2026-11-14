# HYLIOX — templates landing page

Single-page dark landing page. React 18 + Vite + TypeScript + Tailwind CSS,
with GSAP (ScrollTrigger) for scroll reveals, Framer Motion for micro
interactions, and hls.js for the hero video backdrop.

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # typecheck + production build
npm run preview
```

## Deployment

`.github/workflows/deploy-pages.yml` builds on every push to this branch and
publishes `dist` to GitHub Pages at **https://avedirect.github.io/ave/**.

Pages serves the repo under `/ave/` rather than a domain root, so the workflow
passes that prefix to the build as `BASE_PATH`; `vite.config.ts` normalises the
trailing slash. Local dev and any root-served host (Vercel, Netlify) need no
override.

One-time repository setup, which no workflow token can do for you — creating a
Pages site needs repo-admin rights that `GITHUB_TOKEN` does not have:

1. **Settings → Pages → Source: GitHub Actions.**
2. If the deploy job then fails with *"Branch is not allowed to deploy to
   github-pages due to environment protection rules"*, add this branch under
   **Settings → Environments → github-pages → Deployment branches**. It bites
   because the repository's default branch is not this one.

## Design system

Defined once in `tailwind.config.js` and consumed by name everywhere else.

| Token         | Value                                          |
| ------------- | ---------------------------------------------- |
| `obsidian`    | `#0A0A0A` — page ground                        |
| `lime`        | `#D4FF4F` — primary accent                     |
| `ink`         | `#FAFAFA` / `ink-muted` `rgba(250,250,250,.64)` |
| `hairline`    | `rgba(255,255,255,0.06)` — all borders          |
| `surface`     | `rgba(255,255,255,0.03)`, `.glass` = `.04` + `backdrop-blur-xl` |
| radius        | `16px` (`rounded-card`)                         |
| max width     | `1280px` (`.container-page`)                    |
| section pad   | `clamp(80px, 10vw, 160px)` (`.section`)         |
| grid          | 12 columns, 24px gutter (`.grid-12`)            |

Type scale lives in `theme.fontSize` as `display / h1 / h2 / h3 / body / mono`,
each with its line-height and tracking baked in. Fonts are Geist, Geist Mono and
Instrument Serif (italic for display), loaded from Google Fonts with
`Inter / JetBrains Mono / Georgia` fallbacks.

## Structure

`src/App.tsx` composes the page in order: loader → hero → templates → method →
proof → pricing → FAQ → final CTA → footer. All copy and list data is in
`src/data/content.ts`, so the sections stay presentational.

A minimal fixed nav was added on top of the nine specified sections — the hero
and pricing CTAs need anchor targets, and it gives keyboard users a way to jump
between sections.

## Motion

- **Loader** (`components/Loader.tsx`) — 3s monogram shimmer, then an ease-out
  fade. Scroll is locked while it is up.
- **Scroll reveals** (`lib/scrollReveal.ts`) — `ScrollTrigger.batch` on every
  `.reveal` element, staggered 80ms. GSAP is dynamically imported so it stays
  out of the critical path, and setup is gated on the loader finishing so
  nothing reveals behind it.
- **Parallax** — desktop only (`min-width: 1024px`), applied to the step
  artwork in the method section.
- **Marquee** — CSS keyframe translating a doubled track by `-50%`; pauses on
  hover and on focus-within.
- **`prefers-reduced-motion`** — reveals resolve immediately, the loader hold
  drops to 400ms, parallax is off, the dust canvas is not mounted and the hero
  video is never requested. A global CSS block also collapses every remaining
  transition and animation.

## Accessibility

- Skip link, then a logical tab order through nav → hero → sections.
- 2px lime focus ring at 2px offset on everything focusable.
- FAQ is a button/`aria-expanded`/`aria-controls` accordion. Collapsed panels
  use `inert` rather than `hidden`, which keeps them out of the tab order and
  the a11y tree without breaking the height transition.
- Body text runs at `rgba(250,250,250,0.64)` on `#0A0A0A` (≈11:1) and lime on
  obsidian (≈15:1); both clear AA. `ink-faint` is reserved for decorative
  labels.
- Decorative layers (video, dust canvas, glows, marquee track) are
  `aria-hidden`; the marquee's message is repeated in a visually hidden line.

## Media

The repo ships without binary assets, so `components/Artwork.tsx` renders a
deterministic SVG composition per template — no request, no layout shift, and a
distinct identity per card. Pass `src` to that component once real renders
exist; the box already emits AVIF and WebP `<source>`s with `loading="lazy"`,
`decoding="async"` and a fixed `aspect-ratio`.

The hero streams a public Mux test manifest by default. Point
`VITE_HERO_HLS_SRC` at your own (see `.env.example`). hls.js is only fetched
when the browser cannot play HLS natively, and the gradient underneath is a
complete fallback if playback fails.

## Performance

- `gsap`, `framer-motion` and `hls.js` are split into their own chunks; GSAP
  and hls.js are dynamically imported, so neither blocks first paint.
- Critical CSS for the shell and loader is inlined in `index.html`; the font
  stylesheet loads async with a `<noscript>` fallback.
- Every media box declares an `aspect-ratio`, so images and art cannot shift
  layout.
