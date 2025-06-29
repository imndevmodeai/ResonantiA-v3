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
        
        // Go to DuckDuckGo HTML version (more reliable for scraping)
        await page.goto('https://duckduckgo.com/html/', { waitUntil: 'networkidle0', timeout: 30000 });
        
        // Search
        await page.type('input[name="q"]', query);
        await page.click('input[type="submit"]');
        
        // Wait for results
        await page.waitForSelector('.result', { timeout: 15000 });
        
        // Extract results
        const results = await page.evaluate(() => {
            const items = [];
            const resultElements = document.querySelectorAll('.result');
            
            resultElements.forEach((element, index) => {
                if (index >= 10) return; // Limit to 10 results
                
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