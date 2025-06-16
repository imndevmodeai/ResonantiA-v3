const ProxyAgent = require('proxy-agent');
console.log('ProxyAgent loaded:', ProxyAgent);

// Test creating a proxy agent
const proxyUrl = 'http://127.0.0.1:8080';
const agent = new ProxyAgent(proxyUrl);
console.log('Proxy agent created:', agent); 