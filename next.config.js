/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ResonantiA Protocol v3.1-CA Enhancement:
  // Making protocol-specific environment variables available to the client-side application.
  // This allows components to dynamically connect to the correct WebSocket server
  // and be aware of the operational mode.
  env: {
    WEBSOCKET_URL: process.env.WEBSOCKET_URL || `ws://localhost:${process.env.ARCHE_PORT || 3004}`,
    PROTOCOL_VERSION: 'ResonantiA v3.1-CA',
    KEYHOLDER_OVERRIDE_ACTIVE: process.env.KEYHOLDER_OVERRIDE_ACTIVE || 'true', // Default to true for dev
  },
  webpack: (config, { isServer }) => {
    // Protocol-specific webpack aliases for clean imports
    config.resolve.alias = {
      ...config.resolve.alias,
      '@protocol': require('path').resolve(__dirname, 'types/protocol.ts'),
      '@components': require('path').resolve(__dirname, 'components'),
      '@hooks': require('path').resolve(__dirname, 'hooks'),
      '@utils': require('path').resolve(__dirname, 'utils'),
      '@iar': require('path').resolve(__dirname, 'utils/iarProcessor.ts'),
      '@spr': require('path').resolve(__dirname, 'utils/sprDetector.ts'),
      '@temporal': require('path').resolve(__dirname, 'utils/temporalAnalyzer.ts'),
      '@metacognitive': require('path').resolve(__dirname, 'utils/metaCognitiveTracker.ts'),
    };
    
    // Support for .protocol file types (for future protocol definitions)
    config.module.rules.push({
      test: /\.protocol$/,
      use: 'raw-loader',
    });
    
    if (!isServer) {
      require('./webSocketServer');
    }
    return config;
  },
  // Enable experimental features for enhanced protocol support
  experimental: {
    serverComponentsExternalPackages: ['ws'],
  },
};

module.exports = nextConfig;