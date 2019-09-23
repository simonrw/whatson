const path = require("path");

const MODE = process.env.NODE_ENV === "production" ? "production" : "development";

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
        use: [
          {
            loader: 'elm-webpack-loader',
            options: elmOptions,
          }
        ],
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
            },
          },
        ],
      }
    ],
  },
  devServer: {
    contentBase: path.join(__dirname, "./whatson"),
    publicPath: "/static/js/",
    watchContentBase: true,
    port: 9000,
    proxy: {
      '!(/static/**/*.*)': {
        target: 'http://127.0.0.1:5000',
      },
    },
  },
};
