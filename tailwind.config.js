/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{html,js}",
    "./components/**/*.{html,js}",
    "./index.html",
    "./*.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary Colors - Warm orange evoking appetite and energy
        primary: {
          50: '#FEF3E7',
          100: '#FCE4CF',
          200: '#F9C9A0',
          300: '#F5AD70',
          400: '#F29241',
          500: '#EF7711',
          600: '#E67E22', // orange-600 - Main primary
          700: '#CA6D1E',
          800: '#9F5618',
          900: '#743F12',
          DEFAULT: '#E67E22',
        },
        // Secondary Colors - Professional blue building trust
        secondary: {
          50: '#E8F4F8',
          100: '#D1E9F1',
          200: '#A3D3E3',
          300: '#75BDD5',
          400: '#47A7C7',
          500: '#3596B9',
          600: '#2E86AB', // blue-600 - Main secondary
          700: '#267191',
          800: '#1E5B77',
          900: '#16465D',
          DEFAULT: '#2E86AB',
        },
        // Accent Colors - Vibrant highlight for calls-to-action
        accent: {
          50: '#FEF6E7',
          100: '#FDEDCF',
          200: '#FBDB9F',
          300: '#F9C96F',
          400: '#F7B73F',
          500: '#F5A50F',
          600: '#F39C12', // amber-500 - Main accent
          700: '#D4850F',
          800: '#A96D0C',
          900: '#7E5509',
          DEFAULT: '#F39C12',
        },
        // Background Colors
        background: '#FEFEFE', // neutral-50
        surface: '#FFFFFF', // white
        'on-primary': '#FFFFFF',
        'on-secondary': '#FFFFFF',
        'on-accent': '#1A1A1A',
        'on-background': '#1A1A1A',
        'on-surface': '#2C3E50', // slate-800
        // Text Colors
        'text-primary': '#2C3E50', // slate-800
        'text-secondary': '#5D6D7E', // slate-600
        'text-tertiary': '#95A5A6', // slate-400
        // Semantic Colors
        success: {
          50: '#E8F8F0',
          100: '#D1F1E1',
          200: '#A3E3C3',
          300: '#75D5A5',
          400: '#47C787',
          500: '#2FBB6F',
          600: '#27AE60', // green-600 - Main success
          700: '#219251',
          800: '#1A7642',
          900: '#145A33',
          DEFAULT: '#27AE60',
        },
        warning: {
          50: '#FEFBEA',
          100: '#FDF7D5',
          200: '#FBEFAB',
          300: '#F9E781',
          400: '#F7DF57',
          500: '#F5D72D',
          600: '#F4D03F', // yellow-400 - Main warning
          700: '#D4B436',
          800: '#A98F2B',
          900: '#7E6A20',
          DEFAULT: '#F4D03F',
        },
        error: {
          50: '#FDECEA',
          100: '#FBD9D5',
          200: '#F7B3AB',
          300: '#F38D81',
          400: '#EF6757',
          500: '#EB412D',
          600: '#E74C3C', // red-600 - Main error
          700: '#C74133',
          800: '#9F3429',
          900: '#77271F',
          DEFAULT: '#E74C3C',
        },
        'on-success': '#FFFFFF',
        'on-warning': '#1A1A1A',
        'on-error': '#FFFFFF',
        // Border Colors
        border: 'rgba(44, 62, 80, 0.12)', // slate-800 with opacity
      },
      fontFamily: {
        heading: ['Poppins', 'sans-serif'],
        body: ['Source Sans 3', 'sans-serif'],
        caption: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        poppins: ['Poppins', 'sans-serif'],
        source: ['Source Sans 3', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
        jetbrains: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        xs: ['0.875rem', { lineHeight: '1.4' }], // 14px
        sm: ['0.9375rem', { lineHeight: '1.65' }], // 15px - mobile
        base: ['1rem', { lineHeight: '1.6' }], // 16px - desktop
        lg: ['1.125rem', { lineHeight: '1.5' }], // 18px
        xl: ['1.25rem', { lineHeight: '1.4' }], // 20px
        '2xl': ['1.5rem', { lineHeight: '1.3' }], // 24px
        '3xl': ['1.875rem', { lineHeight: '1.25' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '1.2' }], // 36px
      },
      spacing: {
        xs: '0.5rem', // 8px
        sm: '1rem', // 16px
        md: '1.5rem', // 24px
        lg: '2rem', // 32px
        xl: '2.5rem', // 40px
        '2xl': '3rem', // 48px
        '3xl': '5rem', // 80px
      },
      borderRadius: {
        sm: '0.375rem', // 6px
        md: '0.75rem', // 12px
        lg: '1rem', // 16px
        xl: '1.5rem', // 24px
      },
      boxShadow: {
        'sm': '0 1px 3px rgba(230, 126, 34, 0.08)',
        'DEFAULT': '0 2px 4px rgba(230, 126, 34, 0.10)',
        'md': '0 4px 6px rgba(230, 126, 34, 0.12)',
        'lg': '0 8px 16px rgba(230, 126, 34, 0.12)',
        'xl': '0 20px 40px -8px rgba(230, 126, 34, 0.15)',
        'glow-primary': '0 0 20px rgba(230, 126, 34, 0.3)',
        'glow-secondary': '0 0 20px rgba(46, 134, 171, 0.3)',
      },
      transitionDuration: {
        fast: '150ms',
        base: '250ms',
        slow: '350ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      zIndex: {
        base: '0',
        card: '1',
        dropdown: '50',
        navigation: '100',
        modal: '200',
        toast: '300',
      },
      maxWidth: {
        'prose': '70ch',
      },
      letterSpacing: {
        caption: '0.025em',
      },
      animation: {
        'shimmer': 'shimmer 2s infinite',
        'dropdown-open': 'dropdownOpen 150ms cubic-bezier(0.4, 0, 0.2, 1)',
        'toast-slide': 'toastSlideIn 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        dropdownOpen: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        toastSlideIn: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      screens: {
        'xs': '480px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
  ],
}