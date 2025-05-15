const puppeteer = require("puppeteer");
const puppeteerExtra = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const ExtraPluginAnonymizeUa = require("puppeteer-extra-plugin-anonymize-ua");
const fs = require('fs').promises;
const path = require('path');

puppeteerExtra.use(StealthPlugin());
puppeteerExtra.use(ExtraPluginAnonymizeUa());

/**
 * Search the web using DuckDuckGo or Google
 * @param {string} query - The search query
 * @param {string} searchEngine - The search engine to use (duckduckgo or google)
 * @param {boolean} debug - Whether to enable debug mode
 * @returns {Promise<Array>} - Array of search results
 */
async function search(query, searchEngine = "duckduckgo", debug = false) {
  let browser;
  try {
    console.log(`Searching for "${query}" on ${searchEngine}...`);
    
    // Configure browser launch options
    const launchOptions = {
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process"
      ]
    };
    
    // Launch browser
    browser = await puppeteerExtra.launch(launchOptions);
    const page = await browser.newPage();
    
    // Set a realistic user agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
    
    // Set viewport to a common desktop resolution
    await page.setViewport({ width: 1280, height: 800 });
    
    // Enable debug logging if requested
    if (debug) {
      page.on('console', msg => console.log('PAGE LOG:', msg.text()));
      
      // Log all requests
      await page.setRequestInterception(true);
      page.on('request', request => {
        console.log(`Request: ${request.url()}`);
        request.continue();
      });
    }
    
    // Determine search URL based on engine
    let searchUrl;
    if (searchEngine.toLowerCase() === "google") {
      const encodedQuery = encodeURIComponent(query);
      searchUrl = `https://www.google.com/search?q=${encodedQuery}`;
      console.log("Warning: Google search may be blocked by CAPTCHA");
    } else {
      // Default to DuckDuckGo
      searchUrl = "https://duckduckgo.com/html/";
    }
    
    // Navigate to search page
    console.log(`Navigating to ${searchUrl}`);
    await page.goto(searchUrl, { 
      waitUntil: "networkidle2",
      timeout: 30000 
    });
    
    // Take screenshot if debugging
    if (debug) {
      const screenshotPath = path.join(path.dirname(require.main.filename), 'search-page.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Screenshot saved to ${screenshotPath}`);
    }
    
    // Handle search based on engine
    let results = [];
    
    if (searchEngine.toLowerCase() === "google") {
      results = await handleGoogleSearch(page, query, debug);
    } else {
      results = await handleDuckDuckGoSearch(page, query, debug);
    }
    
    return results;
    
  } catch (error) {
    console.error(`Search error: ${error.message}`);
    return { error: error.message };
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

/**
 * Handle Google search
 * @param {Page} page - Puppeteer page object
 * @param {string} query - Search query
 * @param {boolean} debug - Whether to enable debug mode
 * @returns {Promise<Array>} - Array of search results
 */
async function handleGoogleSearch(page, query, debug) {
  try {
    console.log("Handling Google search...");
    
    // Check for and handle consent dialog
    try {
      const consentSelectors = [
        'button[aria-label="Accept all"]',
        'button[aria-label="Reject all"]',
        '#L2AGLb',
        'button.tHlp8d'
      ];
      
      for (const selector of consentSelectors) {
        try {
          console.log(`Looking for consent button with selector: ${selector}`);
          const consentButtonExists = await page.$(selector) !== null;
          
          if (consentButtonExists) {
            console.log(`Found consent button with selector: ${selector}`);
            await page.click(selector);
            console.log("Clicked consent button");
            
            // Wait for navigation or timeout
            await Promise.race([
              page.waitForNavigation({ timeout: 5000 }),
              new Promise(resolve => setTimeout(resolve, 5000))
            ]);
            
            break;
          }
        } catch (e) {
          console.log(`Error with selector ${selector}: ${e.message}`);
        }
      }
    } catch (e) {
      console.log(`Error handling consent: ${e.message}`);
    }
    
    // Check if we're on a CAPTCHA page
    const pageContent = await page.content();
    if (pageContent.includes("recaptcha") || pageContent.includes("Our systems have detected unusual traffic")) {
      console.log("CAPTCHA detected! Google is blocking automated access.");
      return { error: "CAPTCHA detected. Google search is not available." };
    }
    
    // Wait for search results with multiple possible selectors
    const searchResultSelectors = [
      "div#search",
      "div.g",
      "div.tF2Cxc",
      "div[data-sokoban-container]",
      "div.v7W49e"
    ];
    
    let resultsFound = false;
    for (const selector of searchResultSelectors) {
      try {
        console.log(`Waiting for selector: ${selector}`);
        await page.waitForSelector(selector, { timeout: 5000 });
        console.log(`Found results with selector: ${selector}`);
        resultsFound = true;
        break;
      } catch (e) {
        console.log(`Selector ${selector} not found: ${e.message}`);
      }
    }
    
    if (!resultsFound) {
      console.log("Could not find search results with any selector");
      if (debug) {
        const screenshotPath = path.join(path.dirname(require.main.filename), 'search-results.png');
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Results page screenshot saved to ${screenshotPath}`);
      }
      return [];
    }
    
    // Extract search results
    return await extractGoogleResults(page);
    
  } catch (error) {
    console.error(`Google search error: ${error.message}`);
    return [];
  }
}

/**
 * Handle DuckDuckGo search
 * @param {Page} page - Puppeteer page object
 * @param {string} query - Search query
 * @param {boolean} debug - Whether to enable debug mode
 * @returns {Promise<Array>} - Array of search results
 */
async function handleDuckDuckGoSearch(page, query, debug) {
  try {
    console.log("Handling DuckDuckGo search...");
    
    // Type search query and submit
    await page.type("input[name=\"q\"]", query);
    await page.keyboard.press("Enter");
    
    // Wait for results to load
    try {
      await page.waitForSelector(".result", { timeout: 10000 });
    } catch (e) {
      console.log(`Error waiting for DuckDuckGo results: ${e.message}`);
      return [];
    }
    
    // Take screenshot if debugging
    if (debug) {
      const screenshotPath = path.join(path.dirname(require.main.filename), 'search-results.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Results screenshot saved to ${screenshotPath}`);
    }
    
    // Extract search results
    return await extractDuckDuckGoResults(page);
    
  } catch (error) {
    console.error(`DuckDuckGo search error: ${error.message}`);
    return [];
  }
}

/**
 * Extract Google search results
 * @param {Page} page - Puppeteer page object
 * @returns {Promise<Array>} - Array of search results
 */
async function extractGoogleResults(page) {
  console.log("Extracting Google search results...");
  
  try {
    return await page.evaluate(() => {
      let items = [];
      
      // Try multiple selectors for Google
      const selectors = [
        "div.g",
        "div.tF2Cxc",
        "div[data-sokoban-container]",
        "div.v7W49e",
        "div.MjjYud"
      ];
      
      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        if (elements && elements.length > 0) {
          items = Array.from(elements);
          break;
        }
      }
      
      // If still no results, try a more generic approach
      if (items.length === 0) {
        // Look for any div containing an h3 (likely a search result)
        const h3Elements = document.querySelectorAll("h3");
        if (h3Elements && h3Elements.length > 0) {
          items = Array.from(h3Elements).map(h3 => h3.closest('div'));
          items = items.filter(item => item !== null);
        }
      }
      
      return items.slice(0, 5).map(item => {
        let title = "N/A";
        let link = "N/A";
        let description = "N/A";
        
        try {
          // Try multiple selectors for Google result components
          const titleElement = item.querySelector("h3") || 
                              item.querySelector(".LC20lb");
          
          const linkElement = item.querySelector("a");
          
          const descElement = item.querySelector("div[data-content-feature='1']") || 
                             item.querySelector(".VwiC3b") || 
                             item.querySelector(".IsZvec") ||
                             item.querySelector(".lEBKkf");
          
          title = titleElement ? titleElement.textContent.trim() : "N/A";
          link = linkElement ? linkElement.href : "N/A";
          description = descElement ? descElement.textContent.trim() : "N/A";
        } catch (e) {
          // If there's an error extracting data from this item, return what we have
        }
        
        return { title, link, description };
      });
    });
  } catch (error) {
    console.error(`Error extracting Google results: ${error.message}`);
    return [];
  }
}

/**
 * Extract DuckDuckGo search results
 * @param {Page} page - Puppeteer page object
 * @returns {Promise<Array>} - Array of search results
 */
async function extractDuckDuckGoResults(page) {
  console.log("Extracting DuckDuckGo search results...");
  
  try {
    return await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll(".result"));
      
      return items.slice(0, 5).map(item => {
        let title = "N/A";
        let link = "N/A";
        let description = "N/A";
        
        try {
          const titleElement = item.querySelector(".result__title a");
          const linkElement = item.querySelector(".result__url a");
          const descElement = item.querySelector(".result__snippet");
          
          title = titleElement ? titleElement.textContent.trim() : "N/A";
          link = linkElement ? linkElement.href : "N/A";
          description = descElement ? descElement.textContent.trim() : "N/A";
        } catch (e) {
          // If there's an error extracting data from this item, return what we have
        }
        
        return { title, link, description };
      });
    });
  } catch (error) {
    console.error(`Error extracting DuckDuckGo results: ${error.message}`);
    return [];
  }
}

/**
 * Main function
 */
(async () => {
  try {
    // Get command line arguments
    const query = process.argv[2] || "ResonantiA AI";
    const searchEngine = process.argv[3] || "duckduckgo";
    const debug = process.argv.includes("--debug");
    
    // Perform search
    const results = await search(query, searchEngine, debug);
    
    // Output results
    console.log(JSON.stringify(results, null, 2));
    
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }, null, 2));
    process.exit(1);
  }
