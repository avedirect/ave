/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        obsidian: '#0A0A0A',
        lime: {
          DEFAULT: '#D4FF4F',
          soft: 'rgba(212,255,79,0.12)',
          line: 'rgba(212,255,79,0.32)',
        },
        ink: {
          DEFAULT: '#FAFAFA',
          muted: 'rgba(250,250,250,0.64)',
          faint: 'rgba(250,250,250,0.40)',
        },
        hairline: 'rgba(255,255,255,0.06)',
        surface: {
          DEFAULT: 'rgba(255,255,255,0.03)',
          raised: 'rgba(255,255,255,0.04)',
          hover: 'rgba(255,255,255,0.06)',
        },
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Instrument Serif"', 'Georgia', 'ui-serif', 'serif'],
        mono: ['"Geist Mono"', '"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        display: ['clamp(48px, 7vw, 88px)', { lineHeight: '1.02', letterSpacing: '-0.02em' }],
        h1: ['clamp(36px, 5vw, 64px)', { lineHeight: '1.06', letterSpacing: '-0.02em' }],
        h2: ['clamp(24px, 3vw, 32px)', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
        h3: ['clamp(20px, 2.5vw, 28px)', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        body: ['16px', { lineHeight: '1.6' }],
        mono: ['13px', { lineHeight: '1.7' }],
      },
      letterSpacing: {
        eyebrow: '0.4em',
      },
      borderRadius: {
        DEFAULT: '16px',
        card: '16px',
        pill: '999px',
      },
      maxWidth: {
        content: '1280px',
      },
      spacing: {
        gutter: '24px',
        section: 'clamp(80px, 10vw, 160px)',
      },
      transitionTimingFunction: {
        out: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
      keyframes: {
        marquee: {
          from: { transform: 'translate3d(0,0,0)' },
          to: { transform: 'translate3d(-50%,0,0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-140% 0' },
          '100%': { backgroundPosition: '240% 0' },
        },
        drift: {
          from: { transform: 'translate3d(0,0,0)' },
          to: { transform: 'translate3d(0,-40px,0)' },
        },
      },
      animation: {
        marquee: 'marquee 28s linear infinite',
        shimmer: 'shimmer 2.2s cubic-bezier(0.22, 1, 0.36, 1) infinite',
      },
    },
  },
  plugins: [],
}
