#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const puppeteerExtra = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AnonymizeUaPlugin = require('puppeteer-extra-plugin-anonymize-ua');
const fs = require('fs');
const path = require('path');

// Use stealth plugins
puppeteerExtra.use(StealthPlugin());
puppeteerExtra.use(AnonymizeUaPlugin());

/**
 * Standalone search function for Python integration
 */
async function performSearch(query, engine = 'duckduckgo', debug = false) {
    let browser;
    try {
        // Launch browser
        browser = await puppeteerExtra.launch({
            headless: !debug,
            executablePath: '/usr/bin/google-chrome-stable',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--window-size=1920,1080',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ],
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36');

        let results = [];

        if (engine === 'google') {
            results = await searchGoogle(page, query, debug);
        } else if (engine === 'duckduckgo') {
            results = await searchDuckDuckGo(page, query, debug);
        } else {
            throw new Error(`Unsupported search engine: ${engine}`);
        }

        return results;

    } catch (error) {
        console.error(`Search error: ${error.message}`);
        return [];
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

/**
 * Search Google
 */
async function searchGoogle(page, query, debug) {
    try {
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

        // Handle consent if present
        await handleGoogleConsent(page, debug);

        // Wait for results
        const selectors = ['div.MjjYud', 'div#search div.g', 'div.g'];
        let results = [];

        for (const selector of selectors) {
            try {
                await page.waitForSelector(selector, { timeout: 5000 });
                results = await extractGoogleResults(page, selector, debug);
                if (results.length > 0) break;
            } catch (e) {
                continue;
            }
        }

        if (debug && results.length > 0) {
            const timestamp = new Date().toISOString().replace(/:/g, '-');
            await page.screenshot({ 
                path: path.join(__dirname, `google-search-${timestamp}.png`),
                fullPage: true 
            });
        }

        return results;

    } catch (error) {
        console.error(`Google search error: ${error.message}`);
        return [];
    }
}

/**
 * Search DuckDuckGo
 */
async function searchDuckDuckGo(page, query, debug) {
    try {
        await page.goto('https://duckduckgo.com/html/', { waitUntil: 'domcontentloaded', timeout: 30000 });

        // Enter search query
        await page.type('input[name="q"]', query);
        await page.click('input[type="submit"]');

        // Wait for results
        await page.waitForSelector('.result', { timeout: 10000 });

        const results = await extractDuckDuckGoResults(page);

        if (debug && results.length > 0) {
            const timestamp = new Date().toISOString().replace(/:/g, '-');
            await page.screenshot({ 
                path: path.join(__dirname, `duckduckgo-search-${timestamp}.png`),
                fullPage: true 
            });
        }

        return results;

    } catch (error) {
        console.error(`DuckDuckGo search error: ${error.message}`);
        return [];
    }
}

/**
 * Handle Google consent popups
 */
async function handleGoogleConsent(page, debug) {
    const consentSelectors = [
        "button[jsname='higCR']",
        "button[aria-label*='Accept all']",
        "button[aria-label*='Agree']",
        "button#L2AGLb",
        "button.QS5gu.sy4vM",
        "form[action*='consent.google.com'] button"
    ];

    for (const selector of consentSelectors) {
        try {
            const element = await page.$(selector);
            if (element) {
                if (debug) console.error(`Clicking consent button: ${selector}`);
                await element.click();
                await page.waitForTimeout(2000);
                break;
            }
        } catch (e) {
            // Continue to next selector
        }
    }
}

/**
 * Extract Google search results
 */
async function extractGoogleResults(page, selector, debug) {
    try {
        return await page.evaluate((sel, isDebug) => {
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
                    if (isDebug) console.error(`Error processing result: ${e.message}`);
                }
            });
            return items.slice(0, 10);
        }, selector, debug);
    } catch (error) {
        console.error(`Error extracting Google results: ${error.message}`);
        return [];
    }
}

/**
 * Extract DuckDuckGo search results
 */
async function extractDuckDuckGoResults(page) {
    try {
        return await page.evaluate(() => {
            const items = [];
            document.querySelectorAll('.result').forEach(item => {
                try {
                    const titleElement = item.querySelector('.result__title a');
                    const linkElement = item.querySelector('a[href]');
                    const descElement = item.querySelector('.result__snippet');

                    const title = titleElement ? titleElement.textContent.trim() : '';
                    const link = linkElement ? linkElement.href : '';
                    const description = descElement ? descElement.textContent.trim() : '';

                    if (title && link && link.startsWith('http')) {
                        items.push({ title, link, description });
                    }
                } catch (e) {
                    // Skip this result
                }
            });
            return items.slice(0, 10);
        });
    } catch (error) {
        console.error(`Error extracting DuckDuckGo results: ${error.message}`);
        return [];
    }
}

/**
 * Main function for command line usage
 */
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('Usage: node standalone_search.js <query> [engine] [debug]');
        console.error('  query: Search query string');
        console.error('  engine: google or duckduckgo (default: duckduckgo)');
        console.error('  debug: true/false (default: false)');
        process.exit(1);
    }

    const query = args[0];
    const engine = args[1] || 'duckduckgo';
    const debug = args[2] === 'true';

    console.error(`Searching for: "${query}" on ${engine}`);
    
    const results = await performSearch(query, engine, debug);
    
    // Output results as JSON
    console.log(JSON.stringify(results, null, 2));
}

// Run main if this script is executed directly
if (require.main === module) {
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

module.exports = { performSearch }; 