/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette matching the visualizer
        'glass': {
          'light': 'rgba(31, 41, 55, 0.3)',   // bg-gray-800/30
          'medium': 'rgba(31, 41, 55, 0.5)',  // bg-gray-800/50
          'dark': 'rgba(31, 41, 55, 0.6)',    // bg-gray-800/60
        },
        'accent': {
          'cyan': {
            'light': '#67e8f9',   // cyan-400
            'medium': '#06b6d4',  // cyan-500
            'dark': '#0891b2',    // cyan-600
          },
          'purple': {
            'light': '#a78bfa',   // purple-400
          }
        }
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(to right, #a78bfa, #67e8f9)',
        'gradient-card': 'linear-gradient(to bottom right, rgba(22, 78, 99, 0.5), rgba(88, 28, 135, 0.5))',
      },
      backdropBlur: {
        'sm': '4px',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.1)',
        'glow-cyan-lg': '0 10px 40px rgba(6, 182, 212, 0.2)',
        'glow-purple': '0 0 20px rgba(167, 139, 250, 0.1)',
      }
    },
  },
  plugins: [],
}



