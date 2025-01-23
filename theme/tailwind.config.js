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
              'text-primary': '#333',
              'text-secondary': '#666',
          },
          typography: {
              DEFAULT: {
                  css: {
                      maxWidth: '100%',
                      color: '#333',
                      a: {
                          color: '#3498db',
                          textDecoration: 'underline',
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