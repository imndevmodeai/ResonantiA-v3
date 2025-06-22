const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

async function searchWithPuppeteer(query, numResults = 5) {
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ],
        userDataDir: path.join(__dirname, '.chrome_dev_session'),
        ignoreHTTPSErrors: true,
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');

        // Search Google
        await page.goto('https://www.google.com');
        await page.type('input[name="q"]', query);
        await page.keyboard.press('Enter');
        await page.waitForSelector('div.g');

        const results = await page.evaluate(() => {
            const searchResults = [];
            const elements = document.querySelectorAll('div.g');
            elements.forEach(element => {
                const titleElement = element.querySelector('h3');
                const linkElement = element.querySelector('a');
                const snippetElement = element.querySelector('div.VwiC3b');
                
                if (titleElement && linkElement) {
                    searchResults.push({
                        title: titleElement.innerText,
                        link: linkElement.href,
                        snippet: snippetElement ? snippetElement.innerText : 'N/A'
                    });
                }
            });
            return searchResults;
        });

        return {
            results: results.slice(0, numResults),
            reflection: {
                confidence: 0.8,
                status: 'success',
                potential_issues: []
            }
        };
    } finally {
        await browser.close();
    }
}

async function searchWithDuckDuckGo(query, numResults = 5) {
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ],
        userDataDir: path.join(__dirname, '.chrome_dev_session'),
        ignoreHTTPSErrors: true,
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');

        // Search DuckDuckGo
        await page.goto('https://duckduckgo.com');
        await page.type('input[name="q"]', query);
        await page.keyboard.press('Enter');
        await page.waitForSelector('.result');

        const results = await page.evaluate(() => {
            const searchResults = [];
            const elements = document.querySelectorAll('.result');
            elements.forEach(element => {
                const titleElement = element.querySelector('.result__title');
                const linkElement = element.querySelector('.result__url');
                const snippetElement = element.querySelector('.result__snippet');
                
                if (titleElement && linkElement) {
                    searchResults.push({
                        title: titleElement.innerText,
                        link: linkElement.href,
                        snippet: snippetElement ? snippetElement.innerText : 'N/A'
                    });
                }
            });
            return searchResults;
        });

        return {
            results: results.slice(0, numResults),
            reflection: {
                confidence: 0.8,
                status: 'success',
                potential_issues: []
            }
        };
    } finally {
        await browser.close();
    }
}

async function compareSearches(query, numResults = 5) {
    console.log(`--- Search Comparison Workflow (v1.0) Initiated for: ${query} ---`);

    // Perform searches in parallel
    const [puppeteerResults, duckduckgoResults] = await Promise.all([
        searchWithPuppeteer(query, numResults),
        searchWithDuckDuckGo(query, numResults)
    ]);

    // Compare results
    const comparison = {
        puppeteer_search_results: puppeteerResults.results,
        puppeteer_search_reflection: puppeteerResults.reflection,
        duckduckgo_search_results: duckduckgoResults.results,
        duckduckgo_search_reflection: duckduckgoResults.reflection
    };

    // Save results
    const timestamp = new Date().toISOString().replace(/:/g, '-');
    const randomSuffix = crypto.randomBytes(4).toString('hex');
    const resultsDir = path.join(__dirname, 'comparison_results');
    
    if (!fs.existsSync(resultsDir)) {
        fs.mkdirSync(resultsDir, { recursive: true });
    }

    const resultsFile = path.join(resultsDir, `comparison_${timestamp}_${randomSuffix}.json`);
    fs.writeFileSync(resultsFile, JSON.stringify(comparison, null, 2));

    console.log(`Comparison results saved to: ${resultsFile}`);
    console.log('\nComparison Summary:');
    console.log(`Puppeteer (Google) found ${puppeteerResults.results.length} results`);
    console.log(`DuckDuckGo found ${duckduckgoResults.results.length} results`);

    return comparison;
}

// Run the comparison if this file is executed directly
if (require.main === module) {
    const query = process.argv[2] || "quantum computing applications";
    const numResults = parseInt(process.argv[3], 10) || 5;
    
    compareSearches(query, numResults)
        .then(() => process.exit(0))
        .catch(error => {
            console.error('Error:', error);
            process.exit(1);
        });
}

module.exports = { compareSearches }; 