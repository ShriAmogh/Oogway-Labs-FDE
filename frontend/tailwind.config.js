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
        // Palette from user selection:
        // #13005A (Deep Midnight / Dark Royal Navy)
        // #00337C (Classic Deep Blue / Sapphire)
        // #1C82AD (Electric Ocean Cyan / Cerulean Blue)
        // #03C988 (Vibrant Emerald Mint / Neon Jade)

        palette: {
          midnight: '#13005A',
          navy:     '#00337C',
          cyan:     '#1C82AD',
          emerald:  '#03C988',
        },

        // Dark modern theme background & panels using midnight & navy
        bg:         '#07021C', // Darkest midnight tint
        panel:      '#0E0630', // Deep midnight navy container
        raised:     '#13005A', // Midnight raised surface
        'input-bg': '#0A0322',

        brand: {
          DEFAULT: '#03C988', // Vibrant emerald mint for primary actions & highlights
          light:   '#44E5AB',
          dark:    '#029E6B',
        },

        accent: {
          DEFAULT: '#1C82AD', // Cerulean cyan for tools & citations
          light:   '#4FB1DC',
          dark:    '#00337C',
        },

        secondary: {
          DEFAULT: '#00337C',
          light:   '#1C82AD',
        }
      },
      fontFamily: {
        sans:      ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display:   ['Syne', 'Inter', 'sans-serif'],
        mono:      ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-emerald': '0 0 35px -8px rgba(3,201,136,0.45)',
        'glow-cyan':    '0 0 35px -8px rgba(28,130,173,0.45)',
        'glow-midnight':'0 0 35px -8px rgba(19,0,90,0.6)',
      }
    },
  },
  plugins: [],
}
