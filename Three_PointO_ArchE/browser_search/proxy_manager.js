class ProxyManager {
    constructor(config = {}) {
        this.config = {
            proxyList: config.proxyList || [],
            rotationInterval: config.rotationInterval || 300000,
            healthCheckInterval: config.healthCheckInterval || 60000,
            maxRetries: config.maxRetries || 3,
            timeout: config.timeout || 10000,
            healthCheckUrl: config.healthCheckUrl || 'https://www.google.com',
            logLevel: config.logLevel || 'info',
            metrics: config.metrics || { enabled: false }
        };

        this.currentProxyIndex = 0;
        this.healthScores = new Map();
        this.metrics = {
            requests: 0,
            errors: 0,
            responseTimes: []
        };

        this.initialize();
    }

    initialize() {
        if (this.config.proxyList.length === 0) {
            console.warn('No proxies configured. Running without proxy.');
            return;
        }

        // Initialize health scores
        this.config.proxyList.forEach(proxy => {
            this.healthScores.set(proxy.url, 100);
        });

        // Start rotation timer
        if (this.config.proxyList.length > 1) {
            this.rotationTimer = setInterval(() => this.rotateProxy(), this.config.rotationInterval);
        }

        // Start health check timer
        this.healthCheckTimer = setInterval(() => this.checkHealth(), this.config.healthCheckInterval);
    }

    getCurrentProxy() {
        if (this.config.proxyList.length === 0) {
            return null;
        }
        return this.config.proxyList[this.currentProxyIndex];
    }

    rotateProxy() {
        if (this.config.proxyList.length <= 1) return;

        const oldIndex = this.currentProxyIndex;
        this.currentProxyIndex = (this.currentProxyIndex + 1) % this.config.proxyList.length;

        console.log(`Rotating proxy from ${this.config.proxyList[oldIndex].url} to ${this.config.proxyList[this.currentProxyIndex].url}`);
    }

    async checkHealth() {
        for (const proxy of this.config.proxyList) {
            try {
                const startTime = Date.now();
                const response = await fetch(this.config.healthCheckUrl, {
                    agent: this.createProxyAgent(proxy),
                    timeout: this.config.timeout
                });

                if (response.ok) {
                    const responseTime = Date.now() - startTime;
                    const currentScore = this.healthScores.get(proxy.url) || 100;
                    const newScore = Math.min(100, currentScore + 10);
                    this.healthScores.set(proxy.url, newScore);
                    console.log(`Health check passed for ${proxy.url} (${responseTime}ms)`);
                } else {
                    this.decreaseHealthScore(proxy.url);
                }
            } catch (error) {
                console.error(`Health check failed for ${proxy.url}: ${error.message}`);
                this.decreaseHealthScore(proxy.url);
            }
        }
    }

    decreaseHealthScore(proxyUrl) {
        const currentScore = this.healthScores.get(proxyUrl) || 100;
        const newScore = Math.max(0, currentScore - 20);
        this.healthScores.set(proxyUrl, newScore);
    }

    createProxyAgent(proxy) {
        if (!proxy) return null;

        const proxyUrl = new URL(proxy.url);
        const options = {
            host: proxyUrl.hostname,
            port: proxyUrl.port,
            protocol: proxyUrl.protocol
        };

        if (proxy.username && proxy.password) {
            options.auth = `${proxy.username}:${proxy.password}`;
        }

        return options;
    }

    stop() {
        if (this.rotationTimer) {
            clearInterval(this.rotationTimer);
        }
        if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
        }
    }
}

module.exports = ProxyManager; 