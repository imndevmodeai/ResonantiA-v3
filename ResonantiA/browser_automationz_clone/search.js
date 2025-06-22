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

    // Type search query and submit
    await page.type("input[name=\"q\"]", query);
    await page.keyboard.press("Enter");

    // Wait for results to load, ensuring visibility
    try {
      // Use the more common '.result' selector, and ensure it's visible.
      await page.waitForSelector(".result", { visible: true, timeout: 30000 }); // Increased timeout for robustness
    } catch (e) {
      console.error(`Error waiting for DuckDuckGo results (.result selector): ${e.message}`);
      return [];
    }

    // Take screenshot if debugging
    if (debug) {
      const screenshotPath = path.join(__dirname, 'search-results.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.error(`Results screenshot saved to ${screenshotPath}`);
    }

    console.error("handleDuckDuckGoSearch: Calling extractDuckDuckGoResults...");
    return await extractDuckDuckGoResults(page);

  } catch (error) {
    console.error(`DuckDuckGo search error in handleDuckDuckGoSearch: ${error.message}`);
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
  console.error("extractDuckDuckGoResults: Starting extraction...");

  try {
    return await page.evaluate(() => {
      // Use '.result' consistently for querying all result items
      console.error("extractDuckDuckGoResults (browser context): Querying for '.result' elements.");
      const items = Array.from(document.querySelectorAll(".result")); // Changed selector back to .result
      console.error(`extractDuckDuckGoResults (browser context): Found ${items.length} .result items.`);

      return items.slice(0, 15).map(item => {
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

          console.error(`extractDuckDuckGoResults (browser context): Processed item - Title: ${title.substring(0, 150)}... Link: ${link.substring(0, 150)}...`);

        } catch (e) {
          console.error(`extractDuckDuckGoResults (browser context): Error processing item: ${e.message}`);
          // If there's an error extracting data from this item, return what we have
        }

        return { title, link, description, result_date_snippet }; // Added result_date_snippet
      });
    });
  } catch (error) {
    console.error(`Error extracting DuckDuckGo results in extractDuckDuckGoResults: ${error.message}`);
    return [];
  }
}

/**
 * Scrapes image URLs from the current page.
 * @param {Page} page - Puppeteer page object.
 * @returns {Promise<Array<string>>} - Array of image URLs.
 */
async function scrapeImageUrls(page) {
    return await page.evaluate(() => {
        const imageUrls = Array.from(document.querySelectorAll('img'))
            .map(img => img.src)
            .filter(src => src && src.startsWith('http') && !src.startsWith('data:')); // Filter out data URIs
        return [...new Set(imageUrls)]; // Return unique URLs
    });
}

/**
 * Scrapes video URLs from the current page.
 * @param {Page} page - Puppeteer page object.
 * @returns {Promise<Array<string>>} - Array of video URLs.
 */
async function scrapeVideoUrls(page) {
    return await page.evaluate(() => {
        const videoUrls = [];
        // Look for <video> sources
        Array.from(document.querySelectorAll('video source')).forEach(source => {
            if (source.src && source.src.startsWith('http')) {
                videoUrls.push(source.src);
            }
        });
        // Look for <video> src attribute directly
        Array.from(document.querySelectorAll('video')).forEach(video => {
            if (video.src && video.src.startsWith('http')) {
                videoUrls.push(video.src);
            }
        });
        // You might need to look at <a href> tags if they link directly to .mp4, .mov etc.
        // This is more complex and usually involves pattern matching on href.
        return [...new Set(videoUrls)]; // Return unique URLs
    });
}

/**
 * Downloads a file from a URL to a specified filepath.
 * @param {string} url - The URL of the file to download.
 * @param {string} filepath - The local path to save the file.
 * @returns {Promise<void>}
 */
async function downloadFile(url, filepath) {
    return new Promise((resolve, reject) => {
        const dir = path.dirname(filepath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        const file = fs.createWriteStream(filepath);
        https.get(url, response => {
            if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
                // Handle redirects
                console.error(`Redirecting to ${response.headers.location}`);
                return downloadFile(response.headers.location, filepath).then(resolve).catch(reject);
            } else if (response.statusCode !== 200) {
                return reject(new Error(`Failed to download ${url}, status code: ${response.statusCode}`));
            }
            response.pipe(file);
            file.on('finish', () => {
                file.close(() => resolve());
            });
        }).on('error', err => {
            fs.unlink(filepath, () => {}); // Delete the file asynchronously
            reject(err);
        });
    });
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
    console.error("Usage: node search.js <query> [numResults] [searchEngine] [outputDir] [--debug] [--include-text-content] [--download-media] [--media-dir <dir>]");
    process.exit(1);
  }

  const query = args[0];
  const numResults = parseInt(args[1], 10) || 5;
  const searchEngine = args[2] || "google";
  const outputDir = args[3] || ".";
  const debug = args.includes("--debug");
  const includeTextContent = args.includes("--include-text-content");
  const downloadMedia = args.includes("--download-media");
  
  const mediaDirArgIndex = args.indexOf("--media-dir");
  const mediaDir = mediaDirArgIndex !== -1 && args[mediaDirArgIndex + 1] ? args[mediaDirArgIndex + 1] : path.join(outputDir, 'media');

  let browser;
  let page;
  try {
    const defaultChromePath = "/usr/bin/google-chrome"; 
    const executablePath = process.env.CHROME_BIN || defaultChromePath;

    // Initialize capture manager
    const captureManager = new CaptureManager({
      screenshotDir: path.join(mediaDir, 'screenshots'),
      htmlDir: path.join(mediaDir, 'html'),
      pdfDir: path.join(mediaDir, 'pdf')
    });

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

    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36');

    const results = await search(page, query, searchEngine, debug);
    let finalResults = results.slice(0, numResults);

    if ((includeTextContent || downloadMedia) && finalResults.length > 0) {
      console.error("Fetching additional content for results...");
      finalResults = await Promise.all(finalResults.map(async (result, index) => {
        if (result.link && result.link !== "N/A" && result.link.startsWith("http")) {
          try {
            // Scrape the content first (this navigates the page to the result's link)
            const pageData = await scrapePageContent(page, result.link);
            result.content = pageData.content;
            result.publication_date = pageData.publication_date;
            
            // --- ADD THIS BLOCK TO HANDLE MEDIA DOWNLOADS ---
            if (downloadMedia) {
                console.error(`Downloading media for: ${result.link}`);
                result.downloaded_media = { images: [], videos: [] };

                const imageUrls = await scrapeImageUrls(page);
                const videoUrls = await scrapeVideoUrls(page);
                
                // Create a unique subdirectory for this result's media
                const safeDomain = new URL(result.link).hostname.replace(/[^a-zA-Z0-9]/g, '_');
                const resultMediaDir = path.join(mediaDir, `result_${index}_${safeDomain}`);

                // Download images
                for (const [i, imageUrl] of imageUrls.entries()) {
                    try {
                        const filename = path.basename(new URL(imageUrl).pathname) || `image_${i}.jpg`;
                        const filepath = path.join(resultMediaDir, filename);
                        await downloadFile(imageUrl, filepath);
                        result.downloaded_media.images.push(filepath);
                    } catch (downloadError) {
                        console.error(`Failed to download image ${imageUrl}: ${downloadError.message}`);
                    }
                }
                // Download videos
                for (const [i, videoUrl] of videoUrls.entries()) {
                    try {
                        const filename = path.basename(new URL(videoUrl).pathname) || `video_${i}.mp4`;
                        const filepath = path.join(resultMediaDir, filename);
                        await downloadFile(videoUrl, filepath);
                        result.downloaded_media.videos.push(filepath);
                    } catch (downloadError) {
                        console.error(`Failed to download video ${videoUrl}: ${downloadError.message}`);
                    }
                }
            }
            // --- END OF MEDIA DOWNLOAD BLOCK ---

          } catch (scrapeError) {
            console.error(`Error processing link ${result.link}: ${scrapeError.message}`);
            result.content = "Error scraping content.";
          }
        } else {
          result.content = "Invalid or missing link, skipping content scraping.";
        }
        return result;
      }));
    }

    const outputFilePath = path.join(outputDir, `search_results_${searchEngine}_${new Date().toISOString().replace(/:/g, '-')}_${Math.random().toString(36).substring(2, 10)}.json`);
    fs.writeFileSync(outputFilePath, JSON.stringify(finalResults, null, 2));
    console.log(`Search results saved to ${outputFilePath}`);
    console.log(JSON.stringify(finalResults)); // Output final results as JSON

  } catch (error) {
    console.error(`Error in main: ${error.message}`);
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

module.exports = { search, scrapePageContent, handleGoogleSearch, handleDuckDuckGoSearch, extractGoogleResults, extractDuckDuckGoResults, scrapeImageUrls, scrapeVideoUrls, downloadFile };