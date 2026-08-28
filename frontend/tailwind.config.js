/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg:         '#07090F',
        panel:      '#0C0F1A',
        raised:     '#111727',
        'input-bg': '#0A0D16',

        // Brand palette
        violet: {
          DEFAULT: '#7C3AED',
          lite:    '#A78BFA',
          deep:    '#5B21B6',
          glow:    'rgba(124,58,237,0.4)',
        },
        orange: {
          DEFAULT: '#F97316',
          lite:    '#FB923C',
          glow:    'rgba(249,115,22,0.35)',
        },
        cyan: {
          DEFAULT: '#06B6D4',
          lite:    '#67E8F9',
          glow:    'rgba(6,182,212,0.35)',
        },
        emerald: {
          DEFAULT: '#10B981',
          lite:    '#6EE7B7',
          glow:    'rgba(16,185,129,0.3)',
        },
        pink: {
          DEFAULT: '#EC4899',
          lite:    '#F9A8D4',
        }
      },
      fontFamily: {
        sans:      ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display:   ['Syne', 'Inter', 'sans-serif'],
        mono:      ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-violet': '0 0 40px -8px rgba(124,58,237,0.5)',
        'glow-orange': '0 0 40px -8px rgba(249,115,22,0.4)',
        'glow-cyan':   '0 0 40px -8px rgba(6,182,212,0.4)',
        'glow-sm':     '0 0 20px -4px rgba(124,58,237,0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-up':    'fadeUp 0.25s ease forwards',
        'shimmer':    'shimmer 3s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        }
      }
    },
  },
  plugins: [],
}
