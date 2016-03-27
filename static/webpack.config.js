var webpack = require('webpack');
var path = require('path');

var BUILD_DIR = path.resolve(__dirname, 'js');
var ROOT_SRC_DIR = path.resolve(__dirname, 'src');

var APP_DIR = path.resolve(ROOT_SRC_DIR, 'js');

var config = {
  entry: APP_DIR + '/dimension/App.jsx',
  output: {
    path: BUILD_DIR + '/dimension',
    filename: 'bundle.js'
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
      {test: /\.css$/, loader: "style-loader!css-loader"},
      {test: /\.less$/, loader: "style-loader!css-loader!less-loader"},
      {test: /\.scss$/, loaders: ["style", "css", "sass"]}
    ]
  }
};

module.exports = config;