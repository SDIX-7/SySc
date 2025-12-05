module.exports = {
  transpileDependencies: ['/@yabby-business/'],
  devServer: {
    // host: 'localhost',
    port: 8080,
    proxy: {
      '/api' : {
        target: 'http://127.0.0.1:5000',
        ws: true,
        changeOrigin: true
      },
    },
    // disableHostCheck: true,
  }
}
