/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        accent: {
          from: '#78c8ff',
          mid: '#8aa3ff',
          to: '#b084ff',
        },
        dark: {
          bg: '#0b1020',
          card: '#141b2d',
          border: '#2d3748',
          hover: '#1a2332',
        },
        text: {
          primary: '#e8f0ff',
          secondary: '#b8c5d1',
          muted: '#8a9ba8',
        },
        neon: {
          blue: '#78c8ff',
          purple: '#b084ff',
          green: '#4ade80',
          red: '#f87171',
          yellow: '#fbbf24',
        }
      },
      backgroundImage: {
        'gradient-accent': 'linear-gradient(135deg, #78c8ff 0%, #8aa3ff 50%, #b084ff 100%)',
        'gradient-glass': 'linear-gradient(135deg, rgba(120, 200, 255, 0.1) 0%, rgba(138, 163, 255, 0.1) 50%, rgba(176, 132, 255, 0.1) 100%)',
        'glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
        'glass-hover': 'linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%)',
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        'neon-blue': '0 0 20px rgba(120, 200, 255, 0.3)',
        'neon-purple': '0 0 20px rgba(176, 132, 255, 0.3)',
        'neon-green': '0 0 20px rgba(74, 222, 128, 0.3)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1)',
        'glass-hover': '0 12px 40px rgba(0, 0, 0, 0.15)',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #78c8ff, 0 0 10px #78c8ff, 0 0 15px #78c8ff' },
          '100%': { boxShadow: '0 0 10px #78c8ff, 0 0 20px #78c8ff, 0 0 30px #78c8ff' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 5px rgba(120, 200, 255, 0.3), 0 0 10px rgba(120, 200, 255, 0.2)' },
          '50%': { boxShadow: '0 0 20px rgba(120, 200, 255, 0.4), 0 0 30px rgba(120, 200, 255, 0.3)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
