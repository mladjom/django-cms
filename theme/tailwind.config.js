/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "../templates/**/*.html",
    ],
    theme: {
      extend: {
          fontFamily: {
              'sans': ['Inter', 'system-ui', 'sans-serif'],
          },
          colors: {
              'brand-primary': '#2c3e50',
              'brand-accent': '#3498db',
          },
          typography: {
              DEFAULT: {
                  css: {
                      a: {
                          color: '#3498db',
                          '&:hover': {
                              color: '#2980b9'
                          }
                      }
                  }
              }
          }
      }
  },
  plugins: [
      require('@tailwindcss/typography'),
      require('@tailwindcss/forms'),
      require('@tailwindcss/aspect-ratio')
  ]
  }