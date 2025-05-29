const puppeteer = require('puppeteer-core'); // Using puppeteer-core as it's likely intended for a package
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

// Import puppeteer-extra and plugins
const puppeteerExtra = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteerExtra.use(StealthPlugin());

const AnonymizeUaPlugin = require('puppeteer-extra-plugin-anonymize-ua');
puppeteerExtra.use(AnonymizeUaPlugin());


/**
 * Performs a search on a given search engine and extracts the results.
 * @param {Page} page - Puppeteer page object
 * @param {string} query - Search query
 * @param {string} searchEngine - Search engine to use (google or duckduckgo)
 * @param {boolean} debug - Whether to enable debug mode
 * @returns {Promise<Array>} - Array of search results
 */
async function search(page, query, searchEngine = "duckduckgo", debug = false) {
  try {
    console.error(`Searching for \"${query}\" on ${searchEngine}...`);

    // Navigate to the search engine
    const searchUrl = searchEngine === "google" ? "https://www.google.com/search?q=" + encodeURIComponent(query) : "https://duckduckgo.com/html/";
    console.error(`Navigating to ${searchUrl}`);
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });


    if (searchEngine === "google") {
      return await handleGoogleSearch(page, query, debug);
    } else if (searchEngine === "duckduckgo") {
      return await handleDuckDuckGoSearch(page, query, debug);
    } else {
      throw new Error(`Unsupported search engine: ${searchEngine}`);
    }

  } catch (error) {
    console.error(`Search error: ${error.message}`);
    return [];
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
    console.error("Handling Google search...");

    // Wait for search results to load
    const selectors = [
      "div.g",
      "div.tF2Cxc",
      "div[data-sokoban-container]",
      "div.v7W49e",
      "div.MjjYud"
    ];

    let resultsFound = false;
    for (const selector of selectors) {
      try {
        console.error(`Waiting for selector: ${selector}`);
        await page.waitForSelector(selector, { timeout: 5000 });
        console.error(`Found results with selector: ${selector}`);
        resultsFound = true;
        break;
      } catch (e) {
        console.error(`Selector ${selector} not found: ${e.message}`);
      }
    }

    if (!resultsFound) {
      console.error("Could not find search results with any selector");
      if (debug) {
        const screenshotPath = path.join(__dirname, 'search-results.png');
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.error(`Results page screenshot saved to ${screenshotPath}`);
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
    console.error("Handling DuckDuckGo search...");

    // Type search query and submit
    await page.type("input[name=\"q\"]", query);
    await page.keyboard.press("Enter");

    // Wait for results to load
    try {
      await page.waitForSelector(".result", { timeout: 10000 });
    } catch (e) {
      console.error(`Error waiting for DuckDuckGo results: ${e.message}`);
      return [];
    }

    // Take screenshot if debugging
    if (debug) {
      const screenshotPath = path.join(__dirname, 'search-results.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.error(`Results screenshot saved to ${screenshotPath}`);
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
  console.error("Extracting Google search results...");

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
          // If there\'s an error extracting data from this item, return what we have
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
  console.error("Extracting DuckDuckGo search results...");

  try {
    return await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll(".result"));

      return items.slice(0, 5).map(item => {
        let title = "N/A";
        let link = "N/A";
        let description = "N/A";
        let result_date_snippet = null; // New field

        try {
          const titleElement = item.querySelector(".result__title a");
          const linkElement = item.querySelector("a[href]") || item.querySelector(".result__url a");
          const descElement = item.querySelector(".result__snippet");

          // Attempt to find a date snippet associated with the result
          // This is highly dependent on DDG's structure and might need refinement
          const dateSnippetElement = item.querySelector(".result__timestamp") || 
                                     item.querySelector(".result__age"); // Hypothetical selectors

          title = titleElement ? titleElement.textContent.trim() : "N/A";
          link = linkElement ? linkElement.href : "N/A";
          description = descElement ? descElement.textContent.trim() : "N/A";
          result_date_snippet = dateSnippetElement ? dateSnippetElement.textContent.trim() : null;

        } catch (e) {
          // If there's an error extracting data from this item, return what we have
        }

        return { title, link, description, result_date_snippet }; // Added result_date_snippet
      });
    });
  } catch (error) {
    console.error(`Error extracting DuckDuckGo results: ${error.message}`);
    return [];
  }
  }

/**
 * Scrape content from a given URL.
 * @param {Page} page - Puppeteer page object
 * @param {string} url - URL to scrape
 * @returns {Promise<string>} - Scraped content
 */
async function scrapePageContent(page, url) {
  let attempts = 0;
  const maxAttempts = 2;
  let lastError = null;

  while (attempts < maxAttempts) {
    try {
      console.error(`Scraping content from ${url} (Attempt ${attempts + 1}/${maxAttempts})`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

      // Wait for a bit to let dynamic content load, if any (optional, adjust as needed)
      // await new Promise(resolve => setTimeout(resolve, 1000));

      const pageData = await page.evaluate(() => {
        let content = document.body.innerText || "N/A";
        let publication_date = null;
        const metaSelectors = [
          'meta[property="article:published_time"]',
          'meta[name="date"]',
          'meta[name="Date"]',
          'meta[name="pubdate"]',
          'meta[name="publishdate"]',
          'meta[name="article.created"]',
          'meta[name="article.published"]',
          'meta[itemprop="datePublished"]',
        ];
        for (const selector of metaSelectors) {
          const el = document.querySelector(selector);
          if (el && el.content) {
            publication_date = el.content;
            break;
          }
        }
        if (!publication_date) {
          const timeEl = document.querySelector('time[datetime]');
          if (timeEl && timeEl.getAttribute('datetime')) {
            publication_date = timeEl.getAttribute('datetime');
          }
        }
        // Add more sophisticated date extraction logic here if needed (e.g., JSON-LD)

        const fullHtml = document.documentElement.outerHTML;
        return { content, publication_date, fullHtml };
      });
      
      console.error(`Successfully scraped ${url}`);
      return pageData; // Return object with content, publication_date, fullHtml

  } catch (error) {
      lastError = error;
      console.error(`Error scraping ${url} (Attempt ${attempts + 1}): ${error.message}`);
      attempts++;
      if (attempts < maxAttempts) {
        console.error(`Retrying in 2 seconds...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        console.error(`Failed to scrape ${url} after ${maxAttempts} attempts.`);
        return { content: "Error: Could not scrape content.", publication_date: null, fullHtml: "", error: error.message };
  }
    }
  }
  // Should not be reached if loop logic is correct, but as a fallback:
  return { content: "Error: Max retries reached, unknown error.", publication_date: null, fullHtml: "", error: lastError ? lastError.message : "Unknown error" };
}

/**
 * Main function to orchestrate the search and scraping process.
 */
async function main() {
  let browser = null;
  let tempDir = null;
  try {
    const query = process.argv[2];
    const numResults = parseInt(process.argv[3] || '3', 10);
    const searchEngine = process.argv[4] || "duckduckgo"; // Default to duckduckgo
    const outputDirArg = process.argv[5]; // Optional base directory for archives from Python
    const debug = process.argv.includes('--debug');

    if (!query) {
      console.error("Usage: node search.js <query> [numResults] [searchEngine] [outputDir] [--debug]");
      process.exit(1);
    }

    // Create a unique temporary directory for this run's archives
    // This temp dir will be created inside the script's own directory or a system temp if outputDirArg is not specified
    const baseTempPath = outputDirArg ? path.join(outputDirArg, 'search_archives') : os.tmpdir();
    fs.mkdirSync(baseTempPath, { recursive: true }); // Ensure base archive dir exists
    tempDir = fs.mkdtempSync(path.join(baseTempPath, 'run-'));
    console.error(`Archives for this run will be stored in: ${tempDir}`);

    // const executablePath = process.env.PUPPETEER_EXECUTABLE_PATH || puppeteer.executablePath(); // Let puppeteer-extra handle this
    // console.error(`Using browser executable: ${executablePath}`);

    browser = await puppeteerExtra.launch({
      headless: true, // Consider 'new' for future Puppeteer versions
      // executablePath: executablePath, // Removed to let puppeteer-extra find it
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const searchResults = await search(page, query, searchEngine, debug);
    const processedResults = [];

    for (let i = 0; i < Math.min(searchResults.length, numResults); i++) {
      const result = searchResults[i];
      if (!result.link || result.link === "N/A" || result.link.startsWith('javascript:')) continue;

      console.error(`Processing URL (${i+1}/${Math.min(searchResults.length, numResults)}): ${result.link}`);
      const pageData = await scrapePageContent(page, result.link);
      
      let archived_html_path = null;
      let archived_screenshot_path = null;

      if (pageData.fullHtml) {
        const urlHash = crypto.createHash('md5').update(result.link).digest('hex');
        const htmlFilename = `page_${urlHash}_${i}.html`;
        archived_html_path = path.join(tempDir, htmlFilename);
        try {
          fs.writeFileSync(archived_html_path, pageData.fullHtml);
          console.error(`Saved HTML for ${result.link} to ${archived_html_path}`);
        } catch (e) {
          console.error(`Error saving HTML for ${result.link}: ${e.message}`);
          archived_html_path = null; // Reset path if save failed
        }
      }

      try {
        const screenshotFilename = `screenshot_${crypto.createHash('md5').update(result.link).digest('hex')}_${i}.png`;
        archived_screenshot_path = path.join(tempDir, screenshotFilename);
        await page.screenshot({ path: archived_screenshot_path, fullPage: true });
        console.error(`Saved screenshot for ${result.link} to ${archived_screenshot_path}`);
      } catch (e) {
        console.error(`Error taking/saving screenshot for ${result.link}: ${e.message}`);
        archived_screenshot_path = null;
      }

      processedResults.push({
        title: result.title,
        link: result.link,
        description: result.description,
        result_date_snippet: result.result_date_snippet, // From initial search result page
        content: pageData.content, // Main text from scraped page
        publication_date: pageData.publication_date, // From scraped page
        archived_html_path: archived_html_path ? path.relative(outputDirArg || process.cwd(), archived_html_path) : null, // Relative path
        archived_screenshot_path: archived_screenshot_path ? path.relative(outputDirArg || process.cwd(), archived_screenshot_path) : null, // Relative path
        error_scraping: pageData.error || null
      });
    }

    console.log(JSON.stringify(processedResults, null, 2));

  } catch (error) {
    console.error(`Critical error in main: ${error.message}\nStack: ${error.stack}`);
    // Output an empty array or error structure in case of critical failure before/during processing results
    console.log(JSON.stringify([{ error: "Main process_failed", details: error.message }], null, 2));
    process.exitCode = 1; // Indicate failure
  } finally {
    if (browser) {
      try {
      await browser.close();
      } catch (e) {
        console.error(`Error closing browser: ${e.message}`);
      }
    }
    // Do not delete tempDir here; Python side will be responsible for cleanup after copying.
    // if (tempDir) {
    //   fs.rmSync(tempDir, { recursive: true, force: true });
    //   console.error(`Cleaned up temporary archive directory: ${tempDir}`);
    // }
  }
}

// Ensure OS module is required if not already (for os.tmpdir())
const os = require('os');

main();