const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { isServer }) => {
    if (!isServer) {
      require('./webSocketServer');
    }
    return config;
  },
};

module.exports = nextConfig;