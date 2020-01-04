const purgecss = require('@fullhuman/postcss-purgecss')

const MODE = process.env.NODE_ENV === "production" ? "production" : "development";

module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    MODE === "production" && purgecss({
      content: ['./whatson/templates/**/*.html', './src/**/*.js', './src/**/*.elm'],
      defaultExtractor: content => content.match(/[A-Za-z0-9-_:/]+/g) || [],
    }),
  ]
}

