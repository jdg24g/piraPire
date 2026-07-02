module.exports = {
  content: [
    './templates/**/*.html',
    './accounts/**/*.py',
    './wallets/**/*.py',
    './categories/**/*.py',
    './transactions/**/*.py',
    './installments/**/*.py',
    './reports/**/*.py',
    './exports/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        glass: {
          DEFAULT: 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.12)',
          hover: 'rgba(255, 255, 255, 0.15)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
