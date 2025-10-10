#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');

async function searchDuckDuckGo(query) {
    const browser = await puppeteer.launch({
        executablePath: '/usr/bin/chromium-browser',
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--window-size=1920,1080'
        ]
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Set a realistic User-Agent to avoid bot detection
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

        // Go to the main DuckDuckGo site
        await page.goto('https://duckduckgo.com/', { waitUntil: 'networkidle0', timeout: 30000 });
        
        // Search
        await page.type('#search_form_input_homepage', query);
        await page.click('#search_button_homepage');
        
        // Wait for results on the new page
        await page.waitForSelector('#links', { timeout: 15000 });
        
        // FOR DEBUGGING: Take a screenshot to see what the page looks like
        await page.screenshot({ path: '/tmp/search_debug.png', fullPage: true });

        // Extract results
        const results = await page.evaluate(() => {
            const items = [];
            // Use the new selector for the main site
            const resultElements = document.querySelectorAll('.results--main #links .result');
            
            resultElements.forEach((element, index) => {
                if (index >= 10) return; // Limit to 10 results
                
                // Updated selectors for the main site
                const titleElement = element.querySelector('.result__title a');
                const snippetElement = element.querySelector('.result__snippet');
                
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
        });
        
        return results;
        
    } finally {
        await browser.close();
    }
}

async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('Usage: node simple_search.js <query>');
        process.exit(1);
    }
    
    const query = args.join(' ');
    
    try {
        console.error(`Searching for: "${query}"`);
        const results = await searchDuckDuckGo(query);
        console.error(`Found ${results.length} results`);
        console.log(JSON.stringify(results, null, 2));
    } catch (error) {
        console.error('Search failed:', error.message);
        console.log('[]');
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { searchDuckDuckGo }; 