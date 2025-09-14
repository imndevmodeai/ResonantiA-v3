#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const puppeteerExtra = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AnonymizeUaPlugin = require('puppeteer-extra-plugin-anonymize-ua');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const EventEmitter = require('events');

// Configure puppeteer-extra with stealth plugins
puppeteerExtra.use(StealthPlugin());
puppeteerExtra.use(AnonymizeUaPlugin());

/**
 * Unified Search Engine - Combines best features from all analyzed scripts
 * Features:
 * - Multi-engine support (Google, DuckDuckGo, Bing)
 * - Advanced anti-detection with stealth plugins
 * - Human CAPTCHA handoff with automatic resumption
 * - Learning mode for new selectors
 * - Comprehensive error handling and fallbacks
 * - Parallel search capabilities
 * - Result comparison and analysis
 * - Seamless mastermind.interact integration
 */
class UnifiedSearchEngine extends EventEmitter {
    constructor(options = {}) {
        super();
        this.options = {
            headless: options.headless !== false,
            debug: options.debug || false,
            timeout: options.timeout || 30000,
            maxResults: options.maxResults || 10,
            userAgent: options.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport: options.viewport || { width: 1920, height: 1080 },
            chromePath: options.chromePath || '/usr/bin/google-chrome-stable',
            enableStealth: options.enableStealth !== false,
            enableHumanHandoff: options.enableHumanHandoff !== false,
            handoffTimeout: options.handoffTimeout || 300000, // 5 minutes
            resultsDir: options.resultsDir || path.join(__dirname, 'search_results'),
            ...options
        };
        
        this.browser = null;
        this.page = null;
        this.handoffActive = false;
        this.searchState = {};
        this.learningMode = false;
        
        // Ensure results directory exists
        if (!fs.existsSync(this.options.resultsDir)) {
            fs.mkdirSync(this.options.resultsDir, { recursive: true });
        }
    }

    /**
     * Initialize browser and page
     */
    async initialize() {
        try {
            const launchOptions = {
                headless: this.options.headless,
                executablePath: this.options.chromePath,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--window-size=1920,1080',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions-except',
                    '--disable-plugins-discovery',
                    '--disable-default-apps',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ],
                ignoreHTTPSErrors: true,
                userDataDir: path.join(__dirname, '.chrome_session_' + crypto.randomBytes(8).toString('hex'))
            };

            this.browser = await puppeteerExtra.launch(launchOptions);
            this.page = await this.browser.newPage();
            
            // Set viewport and user agent
            await this.page.setViewport(this.options.viewport);
            await this.page.setUserAgent(this.options.userAgent);
            
            // Additional stealth measures
            await this.page.evaluateOnNewDocument(() => {
                // Remove webdriver property
                delete navigator.__proto__.webdriver;
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            });

            // Set up event listeners
            this.setupEventListeners();
            
            this.emit('initialized');
            return true;
            
        } catch (error) {
            this.emit('error', `Failed to initialize browser: ${error.message}`);
            throw error;
        }
    }

    /**
     * Set up page event listeners
     */
    setupEventListeners() {
        if (!this.page) return;

        // Console logging for debug mode
        if (this.options.debug) {
            this.page.on('console', msg => {
                console.error(`[PAGE] ${msg.type()}: ${msg.text()}`);
            });
        }

        // Request interception for debugging
        if (this.options.debug) {
            this.page.setRequestInterception(true);
            this.page.on('request', request => {
                console.error(`[REQUEST] ${request.method()} ${request.url()}`);
                request.continue();
            });
        }

        // Error handling
        this.page.on('error', error => {
            this.emit('error', `Page error: ${error.message}`);
        });

        this.page.on('pageerror', error => {
            this.emit('error', `Page JavaScript error: ${error.message}`);
        });
    }

    /**
     * Main search function - supports multiple engines and parallel execution
     */
    async search(query, engines = ['duckduckgo'], options = {}) {
        const searchOptions = { ...this.options, ...options };
        
        try {
            if (!this.browser || !this.page) {
                await this.initialize();
            }

            this.emit('search_started', { query, engines });
            
            const results = {};
            const searchPromises = engines.map(engine => 
                this.searchSingleEngine(query, engine, searchOptions)
            );

            // Execute searches in parallel
            const searchResults = await Promise.allSettled(searchPromises);
            
            // Process results
            searchResults.forEach((result, index) => {
                const engine = engines[index];
                if (result.status === 'fulfilled') {
                    results[engine] = result.value;
                } else {
                    results[engine] = { error: result.reason.message, results: [] };
                }
            });

            // Save results
            const timestamp = new Date().toISOString().replace(/:/g, '-');
            const resultsFile = path.join(this.options.resultsDir, `search_${timestamp}_${crypto.randomBytes(4).toString('hex')}.json`);
            fs.writeFileSync(resultsFile, JSON.stringify({
                query,
                engines,
                timestamp,
                results,
                metadata: {
                    userAgent: this.options.userAgent,
                    viewport: this.options.viewport,
                    options: searchOptions
                }
            }, null, 2));

            this.emit('search_completed', { results, file: resultsFile });
            return results;

        } catch (error) {
            this.emit('error', `Search failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Search single engine with comprehensive error handling
     */
    async searchSingleEngine(query, engine, options) {
        try {
            this.emit('engine_search_started', { engine, query });
            
            const engineHandlers = {
                'google': this.handleGoogleSearch.bind(this),
                'duckduckgo': this.handleDuckDuckGoSearch.bind(this),
                'bing': this.handleBingSearch.bind(this)
            };

            const handler = engineHandlers[engine.toLowerCase()];
            if (!handler) {
                throw new Error(`Unsupported search engine: ${engine}`);
            }

            const results = await handler(query, options);
            
            this.emit('engine_search_completed', { engine, results });
            return results;

        } catch (error) {
            this.emit('engine_search_failed', { engine, error: error.message });
            throw error;
        }
    }

    /**
     * Handle Google search with advanced CAPTCHA detection and handoff
     */
    async handleGoogleSearch(query, options) {
        try {
            const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
            await this.page.goto(searchUrl, { 
                waitUntil: 'domcontentloaded', 
                timeout: options.timeout 
            });

            // Handle consent popups
            await this.handleGoogleConsent(options);

            // Check for CAPTCHA or blocking
            const captchaStatus = await this.detectCaptcha('google');
            if (captchaStatus.detected) {
                return await this.handleCaptchaChallenge(captchaStatus, 'google', query, options);
            }

            // Extract results with multiple fallback selectors
            const results = await this.extractGoogleResults(options);
            
            if (options.debug && results.length > 0) {
                await this.takeScreenshot(`google_search_${Date.now()}.png`);
            }

            return {
                engine: 'google',
                query,
                results,
                count: results.length,
                status: 'success',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            throw new Error(`Google search failed: ${error.message}`);
        }
    }

    /**
     * Handle DuckDuckGo search
     */
    async handleDuckDuckGoSearch(query, options) {
        try {
            await this.page.goto('https://duckduckgo.com/html/', { 
                waitUntil: 'domcontentloaded', 
                timeout: options.timeout 
            });

            // Enter search query
            await this.page.type('input[name="q"]', query);
            await this.page.click('input[type="submit"]');

            // Wait for results
            await this.page.waitForSelector('.result', { timeout: 10000 });

            const results = await this.extractDuckDuckGoResults(options);

            if (options.debug && results.length > 0) {
                await this.takeScreenshot(`duckduckgo_search_${Date.now()}.png`);
            }

            return {
                engine: 'duckduckgo',
                query,
                results,
                count: results.length,
                status: 'success',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            throw new Error(`DuckDuckGo search failed: ${error.message}`);
        }
    }

    /**
     * Handle Bing search
     */
    async handleBingSearch(query, options) {
        try {
            const searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
            await this.page.goto(searchUrl, { 
                waitUntil: 'domcontentloaded', 
                timeout: options.timeout 
            });

            // Wait for results
            await this.page.waitForSelector('#b_results', { timeout: 10000 });

            const results = await this.extractBingResults(options);

            if (options.debug && results.length > 0) {
                await this.takeScreenshot(`bing_search_${Date.now()}.png`);
            }

            return {
                engine: 'bing',
                query,
                results,
                count: results.length,
                status: 'success',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            throw new Error(`Bing search failed: ${error.message}`);
        }
    }

    /**
     * Handle Google consent popups
     */
    async handleGoogleConsent(options) {
        const consentSelectors = [
            "button[jsname='higCR']",
            "button[aria-label*='Accept all']",
            "button[aria-label*='Agree']",
            "button[aria-label*='I agree']",
            "button#L2AGLb",
            "button.QS5gu.sy4vM",
            "form[action*='consent.google.com'] button",
            "div[aria-modal=\"true\"] button:not([aria-label*='Settings']):not([aria-label*='options']):not([aria-label*='Customize'])"
        ];

        for (const selector of consentSelectors) {
            try {
                const element = await this.page.$(selector);
                if (element) {
                    if (options.debug) {
                        console.error(`Clicking consent button: ${selector}`);
                    }
                    await element.click();
                    await this.page.waitForTimeout(2000);
                    break;
                }
            } catch (e) {
                // Continue to next selector
            }
        }
    }

    /**
     * Detect CAPTCHA and blocking mechanisms
     */
    async detectCaptcha(engine) {
        const detection = {
            detected: false,
            type: null,
            selectors: [],
            message: null
        };

        try {
            // Check for reCAPTCHA
            const recaptchaFrame = await this.page.$('iframe[title="reCAPTCHA"], iframe[src*="recaptcha"]');
            if (recaptchaFrame) {
                detection.detected = true;
                detection.type = 'recaptcha';
                detection.selectors = ['iframe[title="reCAPTCHA"]', 'iframe[src*="recaptcha"]'];
                detection.message = 'reCAPTCHA detected';
                return detection;
            }

            // Check for "About this page" (unusual traffic)
            const aboutPageTitle = await this.page.evaluate(() => {
                const h1 = document.querySelector('h1');
                return h1 ? h1.textContent.includes('About this page') : false;
            });
            
            if (aboutPageTitle) {
                detection.detected = true;
                detection.type = 'unusual_traffic';
                detection.message = 'Unusual traffic detected';
                return detection;
            }

            // Check for other blocking indicators
            const blockingIndicators = [
                'Our systems have detected unusual traffic',
                'Please complete the security check',
                'Verify you are human',
                'Access denied',
                'Blocked'
            ];

            const pageContent = await this.page.content();
            for (const indicator of blockingIndicators) {
                if (pageContent.includes(indicator)) {
                    detection.detected = true;
                    detection.type = 'blocking';
                    detection.message = `Blocking detected: ${indicator}`;
                    return detection;
                }
            }

        } catch (error) {
            if (this.options.debug) {
                console.error(`CAPTCHA detection error: ${error.message}`);
            }
        }

        return detection;
    }

    /**
     * Handle CAPTCHA challenge with human handoff
     */
    async handleCaptchaChallenge(captchaStatus, engine, query, options) {
        if (!this.options.enableHumanHandoff) {
            throw new Error(`CAPTCHA detected but human handoff is disabled: ${captchaStatus.message}`);
        }

        this.handoffActive = true;
        this.searchState = { engine, query, options, captchaStatus };

        this.emit('captcha_detected', {
            type: captchaStatus.type,
            message: captchaStatus.message,
            engine,
            query
        });

        // Switch to non-headless mode for human interaction
        if (this.options.headless) {
            await this.switchToInteractiveMode();
        }

        // Wait for human to solve CAPTCHA
        const solved = await this.waitForHumanSolution(options.handoffTimeout);
        
        if (!solved) {
            throw new Error('CAPTCHA handoff timeout - human did not solve within time limit');
        }

        // Resume automated search
        this.handoffActive = false;
        this.emit('captcha_solved', { engine, query });

        // Re-extract results after CAPTCHA is solved
        const results = await this.extractResultsAfterCaptcha(engine, options);

        return {
            engine,
            query,
            results,
            count: results.length,
            status: 'success_after_captcha',
            captcha_solved: true,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Switch to interactive mode for human CAPTCHA solving
     */
    async switchToInteractiveMode() {
        // This would require browser restart in non-headless mode
        // For now, we'll emit an event to notify the user
        this.emit('human_handoff_required', {
            message: 'Please solve the CAPTCHA in the browser window',
            instructions: [
                '1. Look for the CAPTCHA challenge in the browser',
                '2. Complete the verification',
                '3. Wait for the search results to load',
                '4. The script will automatically resume'
            ]
        });
    }

    /**
     * Wait for human to solve CAPTCHA
     */
    async waitForHumanSolution(timeout) {
        return new Promise((resolve) => {
            const timeoutId = setTimeout(() => {
                resolve(false);
            }, timeout);

            // Check periodically if CAPTCHA is solved
            const checkInterval = setInterval(async () => {
                try {
                    const captchaStatus = await this.detectCaptcha('any');
                    if (!captchaStatus.detected) {
                        clearInterval(checkInterval);
                        clearTimeout(timeoutId);
                        resolve(true);
                    }
                } catch (error) {
                    // Continue checking
                }
            }, 2000);

            // Listen for manual completion signal
            this.once('captcha_manually_solved', () => {
                clearInterval(checkInterval);
                clearTimeout(timeoutId);
                resolve(true);
            });
        });
    }

    /**
     * Extract results after CAPTCHA is solved
     */
    async extractResultsAfterCaptcha(engine, options) {
        const extractors = {
            'google': this.extractGoogleResults.bind(this),
            'duckduckgo': this.extractDuckDuckGoResults.bind(this),
            'bing': this.extractBingResults.bind(this)
        };

        const extractor = extractors[engine];
        if (extractor) {
            return await extractor(options);
        }

        return [];
    }

    /**
     * Extract Google search results with multiple fallback selectors
     */
    async extractGoogleResults(options) {
        const selectors = [
            'div.MjjYud',
            'div#search div.g',
            'div.g',
            'div.tF2Cxc',
            'div[data-sokoban-container]'
        ];

        for (const selector of selectors) {
            try {
                await this.page.waitForSelector(selector, { timeout: 5000 });
                const results = await this.page.evaluate((sel, maxResults) => {
                    const items = [];
                    document.querySelectorAll(sel).forEach(item => {
                        try {
                            const titleElement = item.querySelector('h3');
                            const linkElement = item.querySelector('a');
                            const descElement = item.querySelector('div[data-sncf="pd"]') || 
                                              item.querySelector('div.VwiC3b span') || 
                                              item.querySelector('span.st') ||
                                              item.querySelector('div.IsZvec');

                            const title = titleElement ? titleElement.textContent.trim() : '';
                            const link = linkElement ? linkElement.href : '';
                            const description = descElement ? descElement.textContent.trim() : '';

                            if (title && link && link.startsWith('http')) {
                                items.push({ title, link, description });
                            }
                        } catch (e) {
                            // Skip malformed results
                        }
                    });
                    return items.slice(0, maxResults);
                }, selector, options.maxResults);

                if (results.length > 0) {
                    return results;
                }
            } catch (e) {
                // Try next selector
            }
        }

        return [];
    }

    /**
     * Extract DuckDuckGo search results
     */
    async extractDuckDuckGoResults(options) {
        try {
            return await this.page.evaluate((maxResults) => {
                const items = [];
                document.querySelectorAll('.result').forEach((element, index) => {
                    if (index >= maxResults) return;

                    const titleElement = element.querySelector('.result__title a');
                    const snippetElement = element.querySelector('.result__snippet');
                    const urlElement = element.querySelector('.result__url');

                    if (titleElement) {
                        const title = titleElement.textContent.trim();
                        const link = titleElement.href;
                        const description = snippetElement ? snippetElement.textContent.trim() : '';

                        if (title && link) {
                            items.push({ title, link, description });
                        }
                    }
                });
                return items;
            }, options.maxResults);
        } catch (error) {
            return [];
        }
    }

    /**
     * Extract Bing search results
     */
    async extractBingResults(options) {
        try {
            return await this.page.evaluate((maxResults) => {
                const items = [];
                document.querySelectorAll('#b_results .b_algo').forEach((element, index) => {
                    if (index >= maxResults) return;

                    const titleElement = element.querySelector('h2 a');
                    const snippetElement = element.querySelector('.b_caption p');

                    if (titleElement) {
                        const title = titleElement.textContent.trim();
                        const link = titleElement.href;
                        const description = snippetElement ? snippetElement.textContent.trim() : '';

                        if (title && link) {
                            items.push({ title, link, description });
                        }
                    }
                });
                return items;
            }, options.maxResults);
        } catch (error) {
            return [];
        }
    }

    /**
     * Take screenshot for debugging
     */
    async takeScreenshot(filename) {
        try {
            const screenshotPath = path.join(this.options.resultsDir, filename);
            await this.page.screenshot({ 
                path: screenshotPath, 
                fullPage: true 
            });
            return screenshotPath;
        } catch (error) {
            if (this.options.debug) {
                console.error(`Screenshot failed: ${error.message}`);
            }
        }
    }

    /**
     * Enable learning mode for new selectors
     */
    async enableLearningMode() {
        this.learningMode = true;
        
        await this.page.exposeFunction('reportClickDetails', (details) => {
            this.emit('learning_click', {
                coordinates: { x: details.x, y: details.y },
                target: {
                    id: details.id,
                    tagName: details.tagName,
                    selector: details.selector,
                    outerHTML: details.outerHTML?.substring(0, 200)
                },
                timestamp: new Date().toISOString()
            });
        });

        await this.page.evaluate(() => {
            document.addEventListener('click', (event) => {
                const target = event.target;
                const details = {
                    x: event.clientX,
                    y: event.clientY,
                    id: target.id || '',
                    tagName: target.tagName,
                    selector: target.tagName.toLowerCase() + (target.id ? '#' + target.id : ''),
                    outerHTML: target.outerHTML
                };
                
                if (window.reportClickDetails) {
                    window.reportClickDetails(details);
                }
            });
        });

        this.emit('learning_mode_enabled');
    }

    /**
     * Disable learning mode
     */
    async disableLearningMode() {
        this.learningMode = false;
        this.emit('learning_mode_disabled');
    }

    /**
     * Compare results from multiple engines
     */
    async compareResults(results) {
        const comparison = {
            engines: Object.keys(results),
            total_results: 0,
            unique_urls: new Set(),
            common_results: [],
            engine_specific: {},
            analysis: {}
        };

        // Collect all results
        const allResults = [];
        Object.entries(results).forEach(([engine, data]) => {
            if (data.results && Array.isArray(data.results)) {
                comparison.total_results += data.results.length;
                data.results.forEach(result => {
                    allResults.push({ ...result, engine });
                    comparison.unique_urls.add(result.link);
                });
            }
        });

        // Find common results across engines
        const urlCounts = {};
        allResults.forEach(result => {
            urlCounts[result.link] = (urlCounts[result.link] || 0) + 1;
        });

        comparison.common_results = Object.entries(urlCounts)
            .filter(([url, count]) => count > 1)
            .map(([url, count]) => ({
                url,
                engines: allResults.filter(r => r.link === url).map(r => r.engine),
                count
            }))
            .sort((a, b) => b.count - a.count);

        // Engine-specific analysis
        Object.entries(results).forEach(([engine, data]) => {
            comparison.engine_specific[engine] = {
                result_count: data.results?.length || 0,
                success_rate: data.status === 'success' ? 1 : 0,
                avg_title_length: data.results ? 
                    data.results.reduce((sum, r) => sum + r.title.length, 0) / data.results.length : 0
            };
        });

        // Overall analysis
        comparison.analysis = {
            coverage: comparison.unique_urls.size,
            overlap_rate: comparison.common_results.length / Math.max(comparison.total_results, 1),
            most_common_engine: Object.entries(comparison.engine_specific)
                .sort((a, b) => b[1].result_count - a[1].result_count)[0]?.[0]
        };

        return comparison;
    }

    /**
     * Clean up resources
     */
    async cleanup() {
        try {
            if (this.page) {
                await this.page.close();
                this.page = null;
            }
            if (this.browser) {
                await this.browser.close();
                this.browser = null;
            }
            this.emit('cleanup_completed');
        } catch (error) {
            this.emit('error', `Cleanup failed: ${error.message}`);
        }
    }

    /**
     * Signal that CAPTCHA has been manually solved
     */
    signalCaptchaSolved() {
        this.emit('captcha_manually_solved');
    }
}

/**
 * Factory function for easy instantiation
 */
function createUnifiedSearchEngine(options = {}) {
    return new UnifiedSearchEngine(options);
}

/**
 * Convenience function for quick searches
 */
async function quickSearch(query, engines = ['duckduckgo'], options = {}) {
    const searchEngine = createUnifiedSearchEngine(options);
    
    try {
        await searchEngine.initialize();
        const results = await searchEngine.search(query, engines, options);
        return results;
    } finally {
        await searchEngine.cleanup();
    }
}

/**
 * Mastermind.interact integration function
 */
async function mastermindSearch(query, options = {}) {
    const searchEngine = createUnifiedSearchEngine({
        debug: true,
        enableHumanHandoff: true,
        headless: false, // Allow human interaction
        ...options
    });

    // Set up event listeners for mastermind integration
    searchEngine.on('captcha_detected', (data) => {
        console.error(`[MASTERMIND] CAPTCHA detected: ${data.message}`);
        console.error(`[MASTERMIND] Please solve the CAPTCHA in the browser window`);
    });

    searchEngine.on('captcha_solved', (data) => {
        console.error(`[MASTERMIND] CAPTCHA solved, resuming search`);
    });

    searchEngine.on('search_completed', (data) => {
        console.error(`[MASTERMIND] Search completed, results saved to: ${data.file}`);
    });

    searchEngine.on('error', (error) => {
        console.error(`[MASTERMIND] Search error: ${error}`);
    });

    try {
        await searchEngine.initialize();
        const results = await searchEngine.search(query, ['google', 'duckduckgo'], options);
        return results;
    } finally {
        await searchEngine.cleanup();
    }
}

// Export for use in mastermind.interact
module.exports = {
    UnifiedSearchEngine,
    createUnifiedSearchEngine,
    quickSearch,
    mastermindSearch
};

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('Usage: node unified_search_engine.js <query> [engines] [options]');
        console.error('Examples:');
        console.error('  node unified_search_engine.js "quantum computing"');
        console.error('  node unified_search_engine.js "AI trends" google,duckduckgo');
        console.error('  node unified_search_engine.js "python tutorial" duckduckgo --debug');
        process.exit(1);
    }

    const query = args[0];
    const engines = args[1] ? args[1].split(',') : ['duckduckgo'];
    const debug = args.includes('--debug');

    mastermindSearch(query, { debug })
        .then(results => {
            console.log(JSON.stringify(results, null, 2));
            process.exit(0);
        })
        .catch(error => {
            console.error('Search failed:', error.message);
            process.exit(1);
        });
} 