const path = require("path");

const MODE = process.env.npm_lifecycle_event == "prod" ? "production" : "development";

var elmOptions;
if (MODE === "production") {
  elmOptions = {
    debug: false,
    optimize: true,
  };
} else {
  elmOptions = {
    debug: true,
  };
}

module.exports = {
  mode: MODE,
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "whatson/static/js"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        test: /\.elm$/,
        exclude: [/elm-stuff/, /node_modules/],
        use: {
          loader: 'elm-webpack-loader',
          options: elmOptions,
        },
      },
      {
        test: /\.css$/,
        exclude: [/elm-stuff/, /node_modules/],
        use: [
          'style-loader',
          {
            loader: 'postcss-loader',
            options: {
              ident: 'postcss',
              plugins: [
                require('tailwindcss'),
                require('autoprefixer'),
              ],
            },
          },
        ],
      }
    ],
  },
};
