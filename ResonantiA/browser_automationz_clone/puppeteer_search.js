const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const CaptureManager = require('./capture_manager');
const https = require('https');
const { pipeline } = require('stream');
const { URL } = require('url');

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
    console.error(`Handling Google search... Debug mode is: ${debug}`); 

    // Expose a function to Node.js environment to capture click details
    await page.exposeFunction('reportClickDetailsToNode', (details) => {
      console.error('--- CLICK DETECTED (Learning Mode) ---');
      console.error(`Coordinates: X=${details.x}, Y=${details.y}`);
      console.error(`Target ID: ${details.id}`);
      console.error(`Target TagName: ${details.tagName}`);
      console.error(`Basic Selector: ${details.basicSelector}`);
      console.error(`OuterHTML (first 100 chars): ${details.outerHTML.substring(0,100)}`);
      console.error('--------------------------------------');
      // In a real scenario, you'd save this to a file or database
    });

    // --- Attempt to handle consent pop-ups ---
    if (debug) console.error("Attempting to find and click consent buttons using CSS selectors...");
    const consentButtonSelectorsCSS = [
      "button[jsname='higCR']", 
      "button[aria-label*='Accept all']",
      "button[aria-label*='Agree']",
      "button[aria-label*='I agree']",
      "button#L2AGLb", 
      "button.QS5gu.sy4vM", 
      "form[action*='consent.google.com'] button", 
      "div[aria-modal=\"true\"] button:not([aria-label*='Settings']):not([aria-label*='options']):not([aria-label*='Customize'])"
    ];

    let consentClicked = false;
    for (const selector of consentButtonSelectorsCSS) {
      try {
        if (debug) console.error(`Trying CSS consent selector: ${selector}`);
        const element = await page.$(selector);
        
        if (element && typeof element.click === 'function') {
          if (debug) console.error(`Found consent element with CSS selector: ${selector}. Clicking...`);
          await element.click();
          await page.waitForTimeout(2500); 
          if (debug) console.error("Consent button clicked (CSS). Taking screenshot...");
          const timestamp = new Date().toISOString().replace(/:/g, '-');
          await page.screenshot({ path: path.join(__dirname, `google-after-css-consent-click-${timestamp}.png`), fullPage: true });
          consentClicked = true;
          break; 
        } else if (element) {
          if (debug) console.error(`Found element with CSS selector ${selector}, but it does not have a click function.`);
        }
      } catch (consentError) {
        if (debug) console.error(`Error or element not found for CSS consent selector ${selector}: ${consentError.message}`);
      }
    }
    // --- End of consent handling ---

    // --- Attempt to handle reCAPTCHA (basic detection, no click yet in this version of the code) ---
    let onCaptchaPage = false;
    try {
      const recaptchaFrame = await page.$('iframe[title="reCAPTCHA"], iframe[src*="recaptcha"]');
      if (recaptchaFrame) {
        if (debug) console.error("reCAPTCHA iframe found. Assuming CAPTCHA page for learning.");
        onCaptchaPage = true;
      } else {
         // Check if we are on the "About this page" (unusual traffic) page
        const aboutPageTitle = await page.evaluate(() => {
          const h1 = document.querySelector('h1');
          return h1 ? h1.textContent.includes('About this page') : false;
        });
        if(aboutPageTitle) {
            console.error("Detected 'About this page' (unusual traffic). Assuming CAPTCHA or block page for learning.");
            onCaptchaPage = true; // Treat as a page where learning might be needed
        }
      }
    } catch (e) {
      if (debug) console.error("Error checking for reCAPTCHA iframe or 'About this page': " + e.message);
    }


    // Wait for search results to load OR if on a CAPTCHA page, enter learning mode
    const primarySelector = "div.MjjYud"; // Changed to the more reliable selector
    const fallbackSelector1 = "div#search div.g";
    const fallbackSelector2 = "div.g";
    
    console.error(`Waiting for Google results with primary selector: ${primarySelector}`);
    const timestamp = new Date().toISOString().replace(/:/g, '-');

    try {
      await page.waitForSelector(primarySelector, { timeout: 7000 }); // Adjusted timeout slightly
      console.error(`Found Google results with primary selector: ${primarySelector}`);
      if (debug) {
        const screenshotPath = path.join(__dirname, `google-search-found-${timestamp}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.error(`Google results page screenshot saved to ${screenshotPath}`);
      }
       return await extractGoogleResults(page, primarySelector, debug);

    } catch (e) {
      console.error(`Primary selector ${primarySelector} not found: ${e.message}`);
      console.error(`Trying fallback selector 1 for Google: ${fallbackSelector1}`);
      try {
        await page.waitForSelector(fallbackSelector1, { timeout: 5000});
        console.error(`Found Google results with fallback selector 1: ${fallbackSelector1}`);
        return await extractGoogleResults(page, fallbackSelector1, debug);
      } catch (e2) {
        console.error(`Fallback selector 1 ${fallbackSelector1} also not found: ${e2.message}`);
        console.error(`Trying fallback selector 2 for Google: ${fallbackSelector2}`);
        try {
            await page.waitForSelector(fallbackSelector2, { timeout: 5000 });
            console.error(`Found Google results with fallback selector 2: ${fallbackSelector2}`);
            return await extractGoogleResults(page, fallbackSelector2, debug);
        } catch (e3) {
            console.error(`Fallback selector 2 ${fallbackSelector2} also not found: ${e3.message}`);
            // If all selectors fail, then check for CAPTCHA and enter learning mode if applicable
            if (onCaptchaPage) {
                console.error("LEARNING MODE ACTIVATED: Main results not found and on potential CAPTCHA/block page.");
                console.error("Please click the element you want the script to target in the browser window.");
                console.error("The script will log details of your click and then wait for 30 seconds before exiting.");
        
                try {
                    console.error("Attempting to set up click listener for learning mode...");
                    const recaptchaFrameElement = await page.$('iframe[title="reCAPTCHA"], iframe[src*="recaptcha"]');
                    let targetFrame = page.mainFrame(); 
        
                    if (recaptchaFrameElement) {
                        console.error("reCAPTCHA iframe element found. Trying to get its content frame.");
                        const frame = await recaptchaFrameElement.contentFrame();
                        if (frame) {
                            console.error("Successfully got content frame of reCAPTCHA iframe. Will attach listener there.");
                            targetFrame = frame;
                        } else {
                            console.error("Could not get content frame of reCAPTCHA iframe. Listener will be on main page.");
                        }
                    } else {
                        console.error("No reCAPTCHA iframe element explicitly found by selector for listener attachment. Listener will be on main page.");
                    }
        
                    if (typeof page.exposeFunction === 'function') {
                        await page.exposeFunction('reportClickDetailsToNodeGlobal', (details) => {
                            console.error('--- CLICK DETECTED (Learning Mode via reportClickDetailsToNodeGlobal) ---');
                            console.error(`Coordinates: X=${details.x}, Y=${details.y}`);
                            console.error(`Target ID: ${details.id}`);
                            console.error(`Target TagName: ${details.tagName}`);
                            console.error(`Basic Selector: ${details.basicSelector}`);
                            console.error(`OuterHTML (first 100 chars): ${details.outerHTML ? details.outerHTML.substring(0,100) : 'N/A'}`);
                            console.error('--------------------------------------------------------------------');
                        }).catch(expErr => console.error("Error exposing function reportClickDetailsToNodeGlobal: " + expErr.message));
                    } else {
                         console.error("page.exposeFunction is not available. Cannot set up global click reporting function.");
                    }
        
                    await targetFrame.evaluate(() => {
                      console.log('[LEARN CLICK LISTENER]: Adding click listener to document (this context).');
                      document.addEventListener('click', (event) => {
                        console.log('[LEARN CLICK LISTENER]: Click event detected in browser context.');
                        const target = event.target;
                        const details = {
                          x: event.clientX,
                          y: event.clientY,
                          id: target.id || null,
                          tagName: target.tagName,
                          basicSelector: target.tagName.toLowerCase() + 
                                         (target.id ? '#' + target.id : 
                                         (target.className && typeof target.className === 'string' ? '.' + target.className.trim().split(/\s+/).join('.') : '')),
                          outerHTML: target.outerHTML || ''
                        };
                        if (typeof window.reportClickDetailsToNodeGlobal === 'function') {
                          console.log('[LEARN CLICK LISTENER]: Calling reportClickDetailsToNodeGlobal...');
                          window.reportClickDetailsToNodeGlobal(details);
                        } else if (typeof opener !== 'undefined' && opener && typeof opener.reportClickDetailsToNodeGlobal === 'function') {
                          console.log('[LEARN CLICK LISTENER]: Calling opener.reportClickDetailsToNodeGlobal...');
                          opener.reportClickDetailsToNodeGlobal(details);
                        } else {
                          console.error('[LEARN CLICK LISTENER]: reportClickDetailsToNodeGlobal is not accessible. Logging details to browser console only.');
                          console.log('[LEARN CLICK - BROWSER LOG]', JSON.stringify(details));
                        }
                      }, { once: true, capture: true }); 
                      console.log('[LEARN CLICK LISTENER]: Click listener added.');
                    }).catch(evalErr => console.error("Error evaluating page/frame to add click listener: " + evalErr.message));
        
                } catch (listenerSetupError) {
                    console.error(`Error setting up click listener: ${listenerSetupError.message}`);
                }
                
                if (debug) {
                    const learnPath = path.join(__dirname, `google-learn-mode-active-${timestamp}.png`);
                    try {
                        await page.screenshot({ path: learnPath, fullPage: true });
                        console.error(`Screenshot for 'learn mode active' saved to ${learnPath}`);
                    } catch (ssError) {
                        console.error(`Failed to take 'learn mode active' screenshot: ${ssError.message}`);
                    }
                }
                
                console.error("Learning mode: Waiting for 30 seconds for manual click...");
                try {
                    await new Promise(resolve => setTimeout(resolve, 30000)); 
                } catch (timeoutError) {
                    console.error(`Error during manual wait: ${timeoutError.message}. Continuing...`);
                }
        
                console.error("Learning mode finished waiting. Script will now exit (no results returned).");
                return []; 
            } else {
                // All selectors failed, and not on a CAPTCHA page (or CAPTCHA detection failed)
                if (debug) {
                    const screenshotPathFallback = path.join(__dirname, `google-search-all-fallbacks-failed-${timestamp}.png`);
                    await page.screenshot({ path: screenshotPathFallback, fullPage: true });
                    console.error(`Google results page screenshot (all fallbacks failed) saved to ${screenshotPathFallback}`);
                }
                return [];
            }
        }
      }
    }
  } catch (error) {
    console.error(`Google search error: ${error.message}`);
    if (debug && page) {
        try {
            const timestamp = new Date().toISOString().replace(/:/g, '-');
            const screenshotPath = path.join(__dirname, `google-search-error-${timestamp}.png`);
            console.error(`Debug: Attempting to save error screenshot to: ${screenshotPath}`);
            await page.screenshot({ path: screenshotPath, fullPage: true });
            console.error(`Google search error screenshot saved to ${screenshotPath}`);
        } catch (ssError){
            console.error(`Debug: FAILED to save error screenshot: ${ssError.message}`);
        }
    }
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

    await page.goto("https://duckduckgo.com/?q=" + encodeURIComponent(query), { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.error("handleDuckDuckGoSearch: DuckDuckGo page loaded.");

    // Capture screenshot and HTML immediately after page load if in debug mode
    if (debug) {
      const initialScreenshotPath = path.join(__dirname, 'duckduckgo-initial-page.png');
      await page.screenshot({ path: initialScreenshotPath, fullPage: true });
      console.error(`Initial screenshot saved to ${initialScreenshotPath}`);

      const initialHtmlContent = await page.content();
      const initialHtmlPath = path.join(__dirname, 'duckduckgo-initial-page.html');
      fs.writeFileSync(initialHtmlPath, initialHtmlContent);
      console.error(`Initial HTML content saved to ${initialHtmlPath}`);
    }

    console.error("handleDuckDuckGoSearch: Waiting for main results selector '.result'...");
    await page.waitForSelector(".result", { timeout: 30000 }); // Increased timeout
    console.error("handleDuckDuckGoSearch: '.result' selector found.");

    // Take screenshot if debugging
    if (debug) {
      const screenshotPath = path.join(__dirname, 'search-results-after-wait.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.error(`Screenshot of DuckDuckGo results page saved to ${screenshotPath}`);

      const htmlContent = await page.content();
      const htmlPath = path.join(__dirname, 'duckduckgo-page-content.html');
      fs.writeFileSync(htmlPath, htmlContent);
      console.error(`Full HTML content of DuckDuckGo page saved to ${htmlPath}`);
    }

    return await extractDuckDuckGoResults(page);
  } catch (e) {
    console.error(`Error in handleDuckDuckGoSearch: ${e.message}`);
    return [];
  }
}

/**
 * Extract Google search results
 * @param {Page} page - Puppeteer page object
 * @param {string} resultsSelector - CSS selector for results container
 * @param {boolean} debug - Whether to enable debug mode
 * @returns {Promise<Array>} - Array of search results
 */
async function extractGoogleResults(page, resultsSelector = "div#search div.g", debug = false) {
  console.error(`extractGoogleResults: Extracting Google search results using selector: ${resultsSelector}...`);

  try {
    return await page.evaluate((selectorToUse, isDebug) => {
      let items = [];
      console.error(`extractGoogleResults (browser context): Attempting to select elements with: ${selectorToUse}`); // Browser-side log
      document.querySelectorAll(selectorToUse).forEach(item => {
        try {
          const titleElement = item.querySelector("h3");
          const linkElement = item.querySelector("a");
          // Google often uses spans for snippets, sometimes within a div.
          // This tries a few common patterns for the description.
          const descElement = item.querySelector("div[data-sncf='pd']") || // Common for rich snippets
                              item.querySelector("div[role='web_search_result'] span[role='text']") || // More specific span
                              item.querySelector("div.VwiC3b span") || // Older structure
                              item.querySelector("span.st") || // Even older
                              item.querySelector("div.IsZvec") || // One more observation
                              item.querySelector("div.kb0PBd"); // One more observation

          const title = titleElement ? titleElement.textContent.trim() : "N/A";
          const link = linkElement ? linkElement.href : "N/A";
          let description = "N/A";
          if (descElement) {
            description = Array.from(descElement.childNodes)
                               .map(node => node.textContent)
                               .join('')
                               .trim();
          } else {
            // Fallback if specific description selectors fail, try to get any text within the result block
            // excluding the title and link URL if possible, though this is harder.
            // For now, if specific description not found, mark N/A.
          }
          
          if (isDebug) {
            console.log(`extractGoogleResults (browser context): Found item - Title: ${title}, Link: ${link.substring(0,50)}...`);
          }

          // Basic filter: ensure we have at least a title and a valid-looking link
          if (title !== "N/A" && link !== "N/A" && link.startsWith("http")) {
            items.push({ title, link, description });
          }
        } catch (e) {
          if (isDebug) {
            console.error(`extractGoogleResults (browser context): Error processing a Google result item: ${e.message}`);
          }
        }
      });

      if (items.length === 0 && isDebug) {
          console.warn("extractGoogleResults (browser context): No Google results extracted. The page structure might have changed or results were not found.");
      }
      return items.slice(0, 10); // Return up to 10 results
    }, resultsSelector, debug); // Pass the selector and debug flag to page.evaluate
  } catch (error) {
    console.error(`Error extracting Google results in extractGoogleResults: ${error.message}`);
    return [];
  }
}

/**
 * Extract DuckDuckGo search results
 * @param {Page} page - Puppeteer page object
 * @returns {Promise<Array>} - Array of search results
 */
async function extractDuckDuckGoResults(page) {
  console.error("extractDuckDuckGoResults: Starting extraction.");
  const results = await page.evaluate(() => {
    const data = [];
    const mainResultItems = document.querySelectorAll('article[data-testid="result"]'); // New Main Result Item selector

    mainResultItems.forEach(item => {
      let titleElement = item.querySelector('a[data-testid="result-title-a"]'); // New Title selector
      let linkElement = item.querySelector('a[data-testid="result-url-a"]');   // New Link selector
      let snippetElement = item.querySelector('span[data-testid="result-snippet"]'); // New Snippet selector

      const title = titleElement ? titleElement.innerText.trim() : null;
      const link = linkElement ? linkElement.href : null;
      const snippet = snippetElement ? snippetElement.innerText.trim() : null;

      if (title && link) { // Only add if we have at least a title and a link
        data.push({
          title: title,
          link: link,
          snippet: snippet,
          source: 'DuckDuckGo'
        });
      }
    });
    return data;
  });
  console.error(`extractDuckDuckGoResults: Found ${results.length} results.`);
  return results;
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
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error("Usage: node search.js <query> [numResults] [searchEngine] [outputDir] [--debug] [--text-content-dir <dir>] [--include-text-content] [--capture-all] [--capture-dir <dir>]");
    process.exit(1);
  }

  const query = args[0];
  const numResults = parseInt(args[1], 10) || 5;
  const searchEngine = args[2] || "google";
  const outputDir = args[3] || ".";
  const debug = args.includes("--debug");
  
  console.error(`DEBUG: Parsed debug flag: ${debug}`);

  const textContentDirArgIndex = args.indexOf("--text-content-dir");
  const textContentDir = textContentDirArgIndex !== -1 && args[textContentDirArgIndex + 1] ? args[textContentDirArgIndex + 1] : null;

  const includeTextContent = args.includes("--include-text-content");
  const captureAll = args.includes("--capture-all");
  
  const captureDirArgIndex = args.indexOf("--capture-dir");
  const captureDir = captureDirArgIndex !== -1 && args[captureDirArgIndex + 1] ? args[captureDirArgIndex + 1] : path.join(outputDir, 'captures');

  console.error(`Script arguments: query='${query}', numResults=${numResults}, searchEngine='${searchEngine}', outputDir='${outputDir}', debug=${debug}, textContentDir='${textContentDir}', includeTextContent=${includeTextContent}, captureAll=${captureAll}, captureDir='${captureDir}'`);

  let browser;
  try {
    const defaultChromePath = "/usr/bin/google-chrome"; 
    const executablePath = process.env.CHROME_BIN || defaultChromePath;

    // Initialize capture manager
    const captureManager = new CaptureManager({
      screenshotDir: path.join(captureDir, 'screenshots'),
      htmlDir: path.join(captureDir, 'html'),
      pdfDir: path.join(captureDir, 'pdf')
    });

    console.error(`DEBUG: Attempting to launch browser. Executable path: ${executablePath}`);

    if (!fs.existsSync(executablePath)) {
      console.warn(`Warning: Chrome executable not found at ${executablePath}. Puppeteer might try to download Chromium. Set CHROME_BIN if you have Chrome installed elsewhere or ensure it's at ${defaultChromePath}.`);
      browser = await puppeteer.launch({
        headless: "new",
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu'
        ],
        userDataDir: path.join(__dirname, '.chrome_dev_session'),
        ignoreHTTPSErrors: true,
      });
    } else {
      browser = await puppeteer.launch({
        executablePath: executablePath,
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
    }

    console.error(`DEBUG: Browser launched successfully.`);

    const page = await browser.newPage();
    console.error(`DEBUG: New page created.`);

    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');

    const results = await search(page, query, searchEngine, debug);
    let finalResults = results.slice(0, numResults);

    if (includeTextContent && finalResults.length > 0) {
      console.error("Fetching text content for results...");
      finalResults = await Promise.all(finalResults.map(async (result, index) => {
        if (result.link && result.link !== "N/A" && result.link.startsWith("http")) {
          try {
            const content = await scrapePageContent(page, result.link);
            result.content = content;

            if (textContentDir) {
              const safeQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50);
              const domain = new URL(result.link).hostname.replace(/[^a-zA-Z0-9]/g, '_');
              const contentFileName = `content_${safeQuery}_${index}_${domain}.txt`;
              const contentFilePath = path.join(textContentDir, contentFileName);
              
              if (!fs.existsSync(textContentDir)) {
                fs.mkdirSync(textContentDir, { recursive: true });
              }
              fs.writeFileSync(contentFilePath, content);
              result.content_file = contentFilePath;
              console.error(`Saved text content for ${result.link} to ${contentFilePath}`);
            }

            // Capture screenshots and HTML if requested
            if (captureAll) {
              try {
                const captures = await captureManager.captureAll(page, {
                  screenshot: true,
                  html: true,
                  pdf: true,
                  screenshotOptions: {
                    fullPage: true,
                    quality: 80
                  },
                  htmlOptions: {
                    includeStyles: true,
                    includeScripts: true,
                    format: true
                  },
                  pdfOptions: {
                    format: 'A4',
                    printBackground: true
                  }
                });

                result.captures = captures;
                console.error(`Captured screenshots and HTML for ${result.link}`);
              } catch (captureError) {
                console.error(`Error capturing content for ${result.link}: ${captureError.message}`);
                result.capture_error = captureError.message;
              }
            }
          } catch (scrapeError) {
            console.error(`Error scraping content for ${result.link}: ${scrapeError.message}`);
            result.content = "Error scraping content.";
          }
        } else {
          result.content = "Invalid or missing link, skipping content scraping.";
        }
        return result;
      }));
    }

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/:/g, '-');
    const randomSuffix = crypto.randomBytes(4).toString('hex');
    const resultsFilename = path.join(outputDir, `search_results_${searchEngine}_${timestamp}_${randomSuffix}.json`);

    fs.writeFileSync(resultsFilename, JSON.stringify(finalResults, null, 2));
    console.error(`Search results saved to ${resultsFilename}`);
    console.log(JSON.stringify(finalResults));

  } catch (error) {
    console.error(`Error in main: ${error.message}`);
    if (debug) {
      console.error(error.stack);
    }
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

if (require.main === module) {
  main();
}

module.exports = { search, scrapePageContent, handleGoogleSearch, handleDuckDuckGoSearch, extractGoogleResults, extractDuckDuckGoResults };