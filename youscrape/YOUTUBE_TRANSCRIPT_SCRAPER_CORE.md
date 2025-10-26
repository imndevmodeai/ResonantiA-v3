# YouTube Transcript Scraper - Core Browser Automation Logic

## Overview
This document contains the essential browser automation logic for scraping YouTube video transcripts using Puppeteer. This is the core functionality that can be fed to an LLM to recreate the transcript scraping capability.

## Dependencies
```javascript
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());
```

## Configuration
```javascript
const CONFIG = {
    executablePath: '/usr/bin/google-chrome', // or '/usr/bin/chromium-browser'
    waitTimes: {
        pageLoad: 3000,
        afterClick: 3500,
        transcriptLoad: 3000
    }
};

// Utility function for delays
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
```

## Core Scraping Function
```javascript
async function scrapeYouTubeTranscript(url) {
    const browser = await puppeteer.launch({
        headless: false, // Set to true for production
        args: ['--incognito', '--no-sandbox', '--disable-setuid-sandbox'],
        executablePath: CONFIG.executablePath
    });
    
    const page = await browser.newPage();
    
    // Handle page errors
    page.on('error', (err) => console.error('Page error:', err));
    page.on('pageerror', (err) => console.error('Page pageerror:', err));
    
    console.log('Navigating to the page...');
    await page.goto(url);
    await wait(CONFIG.waitTimes.pageLoad);
    
    // Step 1: Click the "More" button
    await clickMoreButton(page);
    
    // Step 2: Click the "Show transcript" button
    await clickShowTranscriptButton(page);
    
    // Step 3: Wait for transcript to load
    await wait(CONFIG.waitTimes.transcriptLoad);
    
    // Step 4: Extract transcript data
    const transcriptData = await getTranscriptText(page);
    
    // Step 5: Get video information
    const videoInfo = await getVideoInfo(page);
    
    await browser.close();
    
    return { transcriptData, videoInfo };
}
```

## Key Automation Functions

### 1. Scroll and Find Element Function
```javascript
async function scrollPageToFindElement(page, selector) {
    return await page.evaluate(async (selector) => {
        const maxScrolls = 10;
        const scrollStep = 500;
        
        for (let i = 0; i < maxScrolls; i++) {
            // Check if element exists
            const element = document.querySelector(selector);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return true;
            }
            
            // Scroll down if element not found
            window.scrollBy(0, scrollStep);
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        return false;
    }, selector);
}
```

### 2. Click "More" Button
```javascript
async function clickMoreButton(page) {
    console.log("Looking for More button...");
    try {
        const moreButtonSelectors = [
            '#expand',
            'button[aria-label="More actions"]',
            'ytd-button-renderer #button[aria-label="More actions"]',
            '#more'
        ];

        for (const selector of moreButtonSelectors) {
            // Scroll page to find More button
            const found = await scrollPageToFindElement(page, selector);
            if (found) {
                await wait(1000); // Wait after scroll
                const moreButton = await page.$(selector);
                if (moreButton) {
                    await moreButton.click();
                    console.log("Successfully clicked More button");
                    return true;
                }
            }
        }
        
        console.log("Could not find More button with any selector");
        return false;
    } catch (error) {
        console.error('Error with More button:', error);
        return false;
    }
}
```

### 3. Click "Show Transcript" Button
```javascript
async function clickShowTranscriptButton(page) {
    console.log("Looking for Show transcript button...");
    try {
        await wait(2000); // Wait for menu to expand

        const transcriptSelectors = [
            '[aria-label*="transcript"]',
            'tp-yt-paper-item:has-text("Show transcript")',
            'ytd-menu-service-item-renderer'
        ];

        for (const selector of transcriptSelectors) {
            // Scroll page to find transcript button
            const found = await scrollPageToFindElement(page, selector);
            if (found) {
                await wait(1000); // Wait after scroll
                
                // Try to click using JavaScript first
                const clicked = await page.evaluate((selector) => {
                    const button = document.querySelector(selector);
                    if (button) {
                        button.click();
                        return true;
                    }
                }, selector);

                if (clicked) {
                    console.log("Successfully clicked Show transcript button");
                    return true;
                }

                // Fallback to Puppeteer click
                const button = await page.$(selector);
                if (button) {
                    await button.click();
                    console.log("Successfully clicked Show transcript button (fallback)");
                    return true;
                }
            }
        }

        console.log("Could not find Show transcript button");
        return false;
    } catch (error) {
        console.error('Error with Show transcript button:', error);
        return false;
    }
}
```

### 4. Extract Transcript Text
```javascript
async function getTranscriptText(page) {
    console.log("Getting transcript text...");
    try {
        await wait(2000);

        const found = await scrollPageToFindElement(page, 'ytd-transcript-segment-renderer');
        if (!found) {
            console.log("Could not find transcript container");
            return null;
        }

        // Extract transcript segments with timestamps and text
        const transcriptData = await page.evaluate(() => {
            const segments = document.querySelectorAll('ytd-transcript-segment-renderer');
            if (!segments.length) return null;

            return Array.from(segments).map(segment => ({
                timestamp: segment.querySelector('.segment-timestamp')?.textContent?.trim() || '',
                text: segment.querySelector('.segment-text')?.textContent?.trim() || ''
            }));
        });

        return transcriptData;
    } catch (error) {
        console.error('Error getting transcript text:', error);
        return null;
    }
}
```

### 5. Get Video Information
```javascript
async function getVideoInfo(page) {
    return await page.evaluate(() => {
        const videoId = window.location.href.split('v=')[1]?.split('&')[0] || '';
        return {
            title: document.querySelector('h1.ytd-video-primary-info-renderer')?.textContent.trim() || 'Default Video Title',
            url: window.location.href,
            thumbnail: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
            videoId
        };
    });
}
```

## Usage Example
```javascript
// Example usage
const url = 'https://www.youtube.com/watch?v=VIDEO_ID';
const result = await scrapeYouTubeTranscript(url);

if (result.transcriptData) {
    console.log('Transcript extracted successfully!');
    console.log('Video title:', result.videoInfo.title);
    console.log('Number of segments:', result.transcriptData.length);
    
    // Process transcript data
    result.transcriptData.forEach(segment => {
        console.log(`${segment.timestamp}: ${segment.text}`);
    });
} else {
    console.log('Failed to extract transcript');
}
```

## Key Success Factors

### 1. **Stealth Plugin**
- Use `puppeteer-extra-plugin-stealth` to bypass YouTube's bot detection
- Essential for avoiding CAPTCHAs and blocking

### 2. **Multiple Selector Strategies**
- Always provide multiple CSS selectors for each element
- YouTube's interface changes frequently, so fallback selectors are crucial

### 3. **Scrolling Logic**
- YouTube's interface is dynamic and elements may not be immediately visible
- The `scrollPageToFindElement` function ensures elements are found even if they're off-screen

### 4. **Wait Times**
- Adequate wait times between actions are crucial
- YouTube's interface is heavily JavaScript-based and needs time to load

### 5. **Error Handling**
- Robust error handling for each step
- Graceful fallbacks when elements aren't found

### 6. **JavaScript Click Fallback**
- Sometimes Puppeteer's click doesn't work on YouTube's dynamic elements
- Using `page.evaluate()` to trigger clicks directly in the page context

## Common Issues and Solutions

### Issue: "More" button not found
**Solution**: Try different selectors and ensure the page has fully loaded

### Issue: "Show transcript" button not appearing
**Solution**: 
- Make sure the "More" button was clicked successfully
- Wait longer for the menu to expand
- Check if the video actually has a transcript available

### Issue: Transcript segments not found
**Solution**:
- Wait longer for the transcript panel to load
- Scroll to find the transcript container
- Verify the video has auto-generated or manual transcripts

### Issue: Bot detection
**Solution**:
- Use stealth plugin
- Add random delays between actions
- Use incognito mode
- Rotate user agents if needed

## Output Format
The scraper returns an object with:
- `transcriptData`: Array of objects with `timestamp` and `text` properties
- `videoInfo`: Object containing `title`, `url`, `thumbnail`, and `videoId`

This core logic can be adapted and extended for different use cases while maintaining the essential browser automation steps needed to successfully scrape YouTube transcripts. 