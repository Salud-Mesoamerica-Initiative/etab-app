var webpack = require('webpack');
const merge = require('webpack-merge');
var path = require('path');
const NpmInstallPlugin = require('npm-install-webpack-plugin');

const TARGET = process.env.npm_lifecycle_event;

var BUILD_DIR = path.resolve(__dirname, 'js');
var ROOT_SRC_DIR = path.resolve(__dirname, 'src');

var APP_DIR = path.resolve(ROOT_SRC_DIR, 'js');

process.env.BABEL_ENV = TARGET;

var folder = 'location_list';

var config = {
  entry: path.join(APP_DIR, folder),
  output: {
    path: path.join(BUILD_DIR, folder),
    filename: 'bundle.js'
  },
  resolve: {
    extensions: ['', '.js', '.jsx']
  },
  externals: {
    Urls: 'Urls',
    jquery: "jQuery"
  },
  module: {
    loaders: [
      {
        test: /\.jsx?/,
        include: APP_DIR,
        loader: 'babel'
      },
      {
        test: /\.css$/,
        include: ROOT_SRC_DIR,
        loader: "style-loader!css-loader"
      },
      {
        test: /\.less$/,
        include: ROOT_SRC_DIR,
        loader: "style-loader!css-loader!less-loader"
      },
      {
        test: /\.scss$/,
        include: ROOT_SRC_DIR,
        loaders: ["style", "css", "sass"]
      }
    ]
  }
};

if (TARGET === 'start' || !TARGET) {
  module.exports = merge(config, {
    devtool: 'eval-source-map',
    devServer: {
      contentBase: path.join(BUILD_DIR, folder),

      historyApiFallback: true,
      hot: true,
      inline: true,
      progress: true,

      // display only errors to reduce the amount of output
      stats: 'errors-only',

      // parse host and port from env so this is easy
      // to customize
      host: process.env.HOST,
      port: process.env.PORT
    },
    plugins: [
      new webpack.optimize.OccurenceOrderPlugin(),
      new webpack.HotModuleReplacementPlugin(),
      new webpack.NoErrorsPlugin(),
      new NpmInstallPlugin({
        save: true, // --save,
        saveDev: true  // --save-dev
      })
    ]
  });
}

if (TARGET === 'build') {
  module.exports = merge(config, {});
}