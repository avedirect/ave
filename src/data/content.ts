export type Template = {
  id: string
  name: string
  subtitle: string
  tag: string
  /** 12-col span at the `md` breakpoint and up. */
  span: 4 | 6 | 8 | 12
  featured?: boolean
}

export const templates: Template[] = [
  {
    id: 'monolith',
    name: 'Monolith',
    subtitle: 'Dark editorial agency site with a cinematic opener.',
    tag: 'Agency',
    span: 8,
    featured: true,
  },
  { id: 'vantage', name: 'Vantage', subtitle: 'SaaS landing with live pricing logic.', tag: 'SaaS', span: 4 },
  { id: 'atelier', name: 'Atelier', subtitle: 'Image-first studio showcase, zero chrome.', tag: 'Studio', span: 4 },
  { id: 'ledger', name: 'Ledger', subtitle: 'Fintech marketing with data-dense proof.', tag: 'Fintech', span: 4 },
  { id: 'signal', name: 'Signal', subtitle: 'Creator page built around one CTA.', tag: 'Creator', span: 4 },
  { id: 'prism', name: 'Prism', subtitle: 'Product launch microsite with a countdown.', tag: 'Launch', span: 6 },
  { id: 'cadence', name: 'Cadence', subtitle: 'Motion-heavy personal portfolio.', tag: 'Portfolio', span: 6 },
  { id: 'foundry', name: 'Foundry', subtitle: 'Docs, changelog and API reference kit.', tag: 'Docs', span: 12 },
]

export type Step = {
  n: string
  title: string
  body: string
  note: string
}

export const steps: Step[] = [
  {
    n: '01',
    title: 'Pick the template that fits the job',
    body: 'Eight directions, none of them a variation of the same hero. Every template ships with a written art direction — type scale, motion budget, spacing rhythm — so the design decisions are already made before you open the editor.',
    note: 'Figma file + React source, both included',
  },
  {
    n: '02',
    title: 'Hand it to your AI, not a blank prompt',
    body: 'Each template includes a context pack: component map, design tokens, and the prompts that produced it. Drop it into Cursor, v0 or Lovable and the model extends the system instead of inventing a new one every message.',
    note: 'Cursor · v0 · Lovable · Claude Code ready',
  },
  {
    n: '03',
    title: 'Ship the same day',
    body: 'Swap the copy, point it at your data, deploy. No build step to reverse-engineer, no design system to negotiate, no half-finished dark mode. It looks intentional because the intent was written down first.',
    note: 'Deploy on Vercel, Netlify or your own box',
  },
]

export type Testimonial = {
  quote: string
  name: string
  role: string
}

export const testimonials: Testimonial[] = [
  {
    quote:
      'I stopped being able to tell which parts I built and which parts shipped with the template. That is the whole point.',
    name: 'Mara Weiss',
    role: 'Founder, Northbound',
  },
  {
    quote: 'Two days from purchase to a live site my investors actually complimented.',
    name: 'Dev Anand',
    role: 'Solo founder',
  },
  {
    quote:
      'The context pack is the real product. Cursor finally stops drifting after the third prompt.',
    name: 'Lena Kovács',
    role: 'Staff engineer',
  },
  {
    quote: 'Our landing page bounce dropped 31% on the redesign. Same copy, different craft.',
    name: 'Tomás Ferreira',
    role: 'Growth lead, Kettle',
  },
  {
    quote: 'I have bought a lot of templates. This is the first one I did not have to rebuild.',
    name: 'Priya Raman',
    role: 'Design engineer',
  },
  {
    quote: 'It reads like a studio made it on a good week, not like a model made it in a second.',
    name: 'Jonas Brandt',
    role: 'Creative director',
  },
]

export const stats = [
  { value: '8', label: 'Premium templates' },
  { value: '2.4k', label: 'Sites shipped' },
  { value: '4.9', label: 'Average rating' },
  { value: '<1d', label: 'Median time to ship' },
]

export type Tier = {
  eyebrow: string
  name: string
  price: string
  blurb: string
  cta: string
  features: { label: string; included: boolean }[]
  highlight?: boolean
}

export const tiers: Tier[] = [
  {
    eyebrow: 'Single build',
    name: 'Express',
    price: '€297',
    blurb: 'One template, one site, out the door this week.',
    cta: 'Start with Express',
    features: [
      { label: '1 template of your choice', included: true },
      { label: 'React + Tailwind source', included: true },
      { label: 'Figma file', included: true },
      { label: 'AI context pack', included: true },
      { label: 'Copy & brand pass', included: false },
      { label: 'Custom sections', included: false },
    ],
  },
  {
    eyebrow: 'Most picked',
    name: 'Standard',
    price: '€597',
    blurb: 'The full library plus the system that keeps it coherent.',
    cta: 'Get the full library',
    highlight: true,
    features: [
      { label: 'All 8 templates', included: true },
      { label: 'React + Tailwind source', included: true },
      { label: 'Figma files', included: true },
      { label: 'AI context packs', included: true },
      { label: 'Copy & brand pass', included: true },
      { label: 'Custom sections', included: false },
    ],
  },
  {
    eyebrow: 'Built with you',
    name: 'Custom',
    price: '€1,499',
    blurb: 'We adapt a template to your brand and hand over the keys.',
    cta: 'Book a build',
    features: [
      { label: 'All 8 templates', included: true },
      { label: 'React + Tailwind source', included: true },
      { label: 'Figma files', included: true },
      { label: 'AI context packs', included: true },
      { label: 'Copy & brand pass', included: true },
      { label: 'Custom sections & motion', included: true },
    ],
  },
]

export type FaqItem = { q: string; a: string }

export const faq: FaqItem[] = [
  {
    q: 'What exactly do I get when I buy?',
    a: 'The full React + TypeScript + Tailwind source, the Figma file it was designed in, and an AI context pack: component map, design tokens, and the prompt history that produced the build. No obfuscated bundle, no license server.',
  },
  {
    q: 'Do I need to know React to use these?',
    a: 'It helps, but the context pack is written so an AI editor can do the heavy lifting. If you can read a component and change a string, you can ship one of these.',
  },
  {
    q: 'Why does AI-generated design usually look generic?',
    a: 'Because the model is asked to invent a system on every prompt, and it defaults to the median of its training data. These templates fix the system first — type scale, spacing, motion budget — so the model extends a point of view instead of averaging one.',
  },
  {
    q: 'Which AI tools are supported?',
    a: 'Cursor, v0, Lovable, Claude Code and anything else that reads a repository. The context pack is plain markdown and JSON, so it is not tied to a single vendor.',
  },
  {
    q: 'Can I use these for client work?',
    a: 'Yes. Every tier includes a commercial licence covering unlimited client projects. The only thing you cannot do is resell the templates themselves as templates.',
  },
  {
    q: 'Is there a subscription?',
    a: 'No. Every price is one-shot and includes lifetime updates to the templates you own. If we ship a ninth template, Standard and Custom owners get it.',
  },
  {
    q: 'How long does a build actually take?',
    a: 'Median time from purchase to a deployed site is under a day. The Express tier is scoped so that a focused afternoon is enough; Custom runs one to two weeks depending on scope.',
  },
  {
    q: 'What if it is not right for me?',
    a: 'Fourteen days, full refund, no interrogation. If the template did not save you time, it did not do its job.',
  },
]

export const footerColumns = [
  {
    title: 'Templates',
    links: ['Monolith', 'Vantage', 'Atelier', 'Ledger', 'Browse all'],
  },
  {
    title: 'Company',
    links: ['The method', 'Pricing', 'Licence', 'Changelog'],
  },
  {
    title: 'Elsewhere',
    links: ['X / Twitter', 'GitHub', 'Dribbble', 'hello@hyliox.com'],
  },
]
