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
async function extractGoogleResults(page, resultsSelector = "div#search div.g", debug = false) {
  console.error(`Extracting Google search results using selector: ${resultsSelector}...`);

  try {
    return await page.evaluate((selectorToUse, isDebug) => {
      let items = [];
      console.error(`Attempting to select elements with: ${selectorToUse}`); // Browser-side log
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
                              item.querySelector("div.IsZvec") || // Another known one
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
            console.log(`Found item: Title - ${title}, Link - ${link.substring(0,50)}...`);
          }

          // Basic filter: ensure we have at least a title and a valid-looking link
          if (title !== "N/A" && link !== "N/A" && link.startsWith("http")) {
            items.push({ title, link, description });
          }
        } catch (e) {
          if (isDebug) {
            console.error(`Error processing a Google result item: ${e.message}`);
          }
        }
      });

      if (items.length === 0 && isDebug) {
          console.warn("No Google results extracted. The page structure might have changed or results were not found.");
      }
      return items.slice(0, 10); // Return up to 10 results
    }, resultsSelector, debug); // Pass the selector and debug flag to page.evaluate
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
    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        const content = await page.evaluate(() => document.body.innerText);
        return content;
    } catch (error) {
        console.error(`Error scraping content from ${url}: ${error.message}`);
        return null;
    }
}

/**
 * Main function
 */
async function main() {
    const yargs = require('yargs/yargs');
    const { hideBin } = require('yargs/helpers');
    const argv = yargs(hideBin(process.argv))
        .option('query', {
            alias: 'q',
            type: 'string',
            description: 'Search query',
            demandOption: true,
        })
        .option('engine', {
            alias: 'e',
            type: 'string',
            default: 'google',
            description: 'Search engine (google or duckduckgo)',
        })
        .option('output', {
            alias: 'o',
            type: 'string',
            description: 'Output file path for search results JSON',
            demandOption: true,
        })
        .option('debug', {
            type: 'boolean',
            default: false,
            description: 'Enable debug mode (saves screenshots)',
        })
        .help()
        .alias('help', 'h')
        .argv;

    const { query, engine, output, debug } = argv;

    let browser;
    try {
        console.error(`Initializing Puppeteer...`);
        browser = await puppeteerExtra.launch({
            headless: !debug, // Run in headful mode when debugging
            executablePath: '/usr/bin/chromium-browser', 
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080'],
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        // Add a more human-like user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36');
        
        const results = await search(page, query, engine, debug);

        console.error(`Search completed. Saving ${results.length} results to ${output}...`);
        fs.writeFileSync(output, JSON.stringify(results, null, 2));
        console.error(`Results saved successfully.`);

    } catch (error) {
        console.error(`An error occurred in the main function: ${error.message}`);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Only run main() if this file is executed directly, not when required as a module
if (require.main === module) {
main();
}

// Add module exports at the end of the file
module.exports = {
  search,
  handleGoogleSearch,
  handleDuckDuckGoSearch,
  extractGoogleResults,
  extractDuckDuckGoResults,
  scrapePageContent
};