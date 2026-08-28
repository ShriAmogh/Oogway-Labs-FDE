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
        // #E3F2FD (Ice Blue / Crisp Tint)
        // #90CAF9 (Sky Azure / Soft Blue)
        // #2196F3 (Electric Blue / Azure Primary)
        // #0D47A1 (Deep Royal Navy / Cobalt)

        palette: {
          ice:   '#E3F2FD',
          sky:   '#90CAF9',
          azure: '#2196F3',
          navy:  '#0D47A1',
        },

        // Dark modern royal blue theme
        bg:         '#070F1E', // Deepest midnight navy
        panel:      '#0D1B33', // Royal blue container
        raised:     '#0D47A1', // Royal navy surface
        'input-bg': '#0A1528',

        brand: {
          DEFAULT: '#2196F3', // Electric blue for primary actions
          light:   '#90CAF9',
          dark:    '#0D47A1',
        },

        accent: {
          DEFAULT: '#90CAF9', // Sky blue for citations & secondary
          light:   '#E3F2FD',
          dark:    '#2196F3',
        },

        paper: {
          DEFAULT: '#E3F2FD',
          muted:   '#90CAF9',
        }
      },
      fontFamily: {
        sans:      ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display:   ['Syne', 'Inter', 'sans-serif'],
        mono:      ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-azure': '0 0 35px -8px rgba(33,150,243,0.45)',
        'glow-sky':   '0 0 35px -8px rgba(144,202,249,0.45)',
        'glow-navy':  '0 0 35px -8px rgba(13,71,161,0.6)',
      }
    },
  },
  plugins: [],
}
