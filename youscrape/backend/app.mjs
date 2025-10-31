import dotenv from 'dotenv';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

dotenv.config();

puppeteer.use(StealthPlugin());

const CONFIG = {
    executablePath: '/usr/bin/google-chrome',
    waitTimes: {
        pageLoad: 3000,
        afterClick: 3500,
        transcriptLoad: 3000
    },
    outputDir: 'transcripts',
    defaultTitle: 'Default Video Title'
};

// Custom promise-based timeout function
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Add this before the saveData function
const styles = `
    body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.6;
    }
    
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .header a {
        text-decoration: none;
        color: inherit;
    }
    
    .thumbnail {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .timestamps {
        margin: 20px 0;
    }
    
    .timestamp {
        display: inline-block;
        margin: 5px;
        padding: 5px 10px;
        background-color: #f0f0f0;
        border-radius: 4px;
        text-decoration: none;
        color: #333;
    }
    
    .timestamp:hover {
        background-color: #e0e0e0;
    }
    
    .transcript-text {
        margin-top: 30px;
    }
    
    button {
        padding: 10px 20px;
        margin: 10px 0;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    button:hover {
        background-color: #0056b3;
    }
    
    button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    
    input[type="text"] {
        padding: 10px;
        margin-right: 10px;
        width: 300px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    form {
        margin-bottom: 20px;
    }
`;

async function scrape(url) {
    console.log(`[ACTION] Initializing scrape for URL: ${url}`);
    let browser;
    try {
        console.log('[ACTION] Launching browser...');
        browser = await puppeteer.launch({
            headless: false,
            args: [
                '--incognito', 
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ],
            executablePath: CONFIG.executablePath,
            timeout: 60000
        });
            
        const page = await browser.newPage();

        // Handle page errors
        page.on('error', (err) => console.error('Page error:', err));
        page.on('pageerror', (err) => console.error('Page pageerror:', err));

        console.log(`[INFO] Navigating to the page: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        await wait(CONFIG.waitTimes.pageLoad);

        // Context-Aware Execution
        console.log('[ACTION] Analyzing URL type...');
        const isVideoPage = url.includes('/watch');
        const isChannelPage = url.includes('/videos') || url.includes('/@');

        if (isChannelPage) {
            console.log('[INFO] Channel page detected. Initiating video list reconnaissance...');
            const videoLinks = await getVideoLinksFromChannel(page);
            if (videoLinks && videoLinks.length > 0) {
                console.log(`[SUCCESS] Found ${videoLinks.length} videos on the channel page.`);
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const safeTitle = "channel_video_list";
                const filename = `${safeTitle}.${timestamp}.json`;
                const filePath = path.join(CONFIG.outputDir, filename);
                if (!fs.existsSync(CONFIG.outputDir)) {
                    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
                }
                fs.writeFileSync(filePath, JSON.stringify(videoLinks, null, 2), 'utf8');
                console.log(`[SUCCESS] Video list saved to ${filePath}`);
            } else {
                console.log('[WARNING] Could not extract any video links from the channel page.');
            }
        } else if (isVideoPage) {
            console.log('[INFO] Video page detected. Initiating transcript extraction protocol...');
            // First, click the "More" button if available to reveal options like "Show transcript"
            await clickMoreButton(page);

            // Now, try to click the "Show transcript" button
            await clickShowTranscriptButton(page);

            // After clicking the "Show transcript" button, wait for the transcript to load
            await wait(CONFIG.waitTimes.transcriptLoad);

            const transcriptData = await getTranscriptText(page);
            if (!transcriptData) {
                console.error('[ERROR] Failed to get transcript text');
                await browser.close();
                return;
            }

            const videoInfo = await getVideoInfo(page);
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            saveData(transcriptData, videoInfo, timestamp);
        } else {
            console.log('[WARNING] URL is not a recognized YouTube video or channel page.');
        }

        console.log('[ACTION] Closing browser...');
        await browser.close();
    } catch (error) {
        console.error('[ERROR] Error during scraping:', error);
        if (browser) {
            await browser.close();
        }
        throw error;
    }
}

async function scrollPageToFindElement(page, selector) {
    try {
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
    } catch (error) {
        console.error('Error in scrollPageToFindElement:', error);
        return false;
    }
}

async function clickMoreButton(page) {
    console.log("[ACTION] Looking for 'More' button...");
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
                    console.log("[SUCCESS] Clicked 'More' button.");
                    return true;
                }
            }
        }
        
        console.log("[WARNING] Could not find 'More' button with any selector.");
        return false;
    } catch (error) {
        console.error("[ERROR] Exception in clickMoreButton:", error);
        return false;
    }
}

async function clickShowTranscriptButton(page) {
    console.log("[ACTION] Looking for 'Show transcript' button...");
    try {
        await wait(2000); // Wait for menu to expand

        // Scroll to find transcript button
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
                    console.log("[SUCCESS] Clicked 'Show transcript' button via page evaluation.");
                    return true;
                }

                // Fallback to Puppeteer click
                const button = await page.$(selector);
                if (button) {
                    await button.click();
                    console.log("[SUCCESS] Clicked 'Show transcript' button via Puppeteer fallback.");
                    return true;
                }
            }
        }

        console.log("[WARNING] Could not find 'Show transcript' button.");
        return false;
    } catch (error) {
        console.error("[ERROR] Exception in clickShowTranscriptButton:", error);
        return false;
    }
}

async function getTranscriptText(page) {
    console.log("[ACTION] Extracting transcript text segments...");
    try {
        await wait(2000);

        const found = await scrollPageToFindElement(page, 'ytd-transcript-segment-renderer');
        if (!found) {
            console.log("[WARNING] Could not find transcript container.");
            return null;
        }

        // Modified to return an array of objects with timestamps and text
        const transcriptData = await page.evaluate(() => {
            const segments = document.querySelectorAll('ytd-transcript-segment-renderer');
            if (!segments.length) return null;

            return Array.from(segments).map(segment => ({
                timestamp: segment.querySelector('.segment-timestamp')?.textContent?.trim() || '',
                text: segment.querySelector('.segment-text')?.textContent?.trim() || ''
            }));
        });

        console.log(`[SUCCESS] Extracted ${transcriptData ? transcriptData.length : 0} transcript segments.`);
        return transcriptData;
    } catch (error) {
        console.error('[ERROR] Exception in getTranscriptText:', error);
        return null;
    }
}

async function getVideoLinksFromChannel(page) {
    console.log("[ACTION] Extracting video links from channel page...");
    try {
        await page.waitForSelector('a#video-title-link');
        return await page.evaluate(() => {
            const links = document.querySelectorAll('a#video-title-link');
            return Array.from(links).map(link => ({
                title: link.getAttribute('title'),
                href: link.getAttribute('href')
            }));
        });
    } catch (error) {
        console.error('[ERROR] Exception in getVideoLinksFromChannel:', error);
        return [];
    }
}

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

function saveData(data, videoInfo, timestamp) {
    const safeTitle = videoInfo.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const htmlFilename = `${safeTitle}.${timestamp}.html`;
    const txtFilename = `${safeTitle}.${timestamp}.txt`;
    const directoryPath = CONFIG.outputDir;

    if (!fs.existsSync(directoryPath)) {
        fs.mkdirSync(directoryPath, { recursive: true });
    }

    // --- Save TXT file ---
    const transcriptTextOnly = data.map(segment => segment.text).join(' ');
    const txtFilePath = path.join(directoryPath, txtFilename);
    fs.writeFileSync(txtFilePath, transcriptTextOnly, 'utf8');
    console.log(`[SUCCESS] Plain text transcript saved to ${txtFilePath}`);

    // Create HTML content with React components
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>${videoInfo.title} - Transcript</title>
    <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/babel-standalone@6/babel.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 10px 0;
        }
        .header a {
            color: #000;
            text-decoration: none;
        }
        .header a:hover {
            text-decoration: underline;
        }
        .thumbnail {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .timestamps {
            margin-bottom: 30px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .timestamp {
            display: inline-block;
            margin: 5px;
            padding: 8px 12px;
            background: #e0e0e0;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            color: #333;
            transition: background 0.2s;
        }
        .timestamp:hover {
            background: #d0d0d0;
        }
        .transcript-text {
            text-align: justify;
            padding: 20px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="${videoInfo.url}" target="_blank">
            <h1>${videoInfo.title}</h1>
            <img class="thumbnail" src="${videoInfo.thumbnail}" alt="${videoInfo.title}">
                        </a>
                    </div>
                    
    <div class="timestamps">
                        <h2>Timestamps:</h2>
        ${data.map(segment => {
            const timeInSeconds = convertTimestampToSeconds(segment.timestamp);
            return `<a class="timestamp" 
                      href="${videoInfo.url}&t=${timeInSeconds}" 
                      target="_blank">${segment.timestamp}</a>`;
        }).join('')}
                    </div>

    <div class="transcript-text">
                        <h2>Full Transcript:</h2>
        <p>${data.map(segment => segment.text).join(' ')}</p>
                </div>
            );
        };

        // Render the App
        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
    `;

    const htmlFilePath = path.join(directoryPath, htmlFilename);
    fs.writeFileSync(htmlFilePath, htmlContent, 'utf8');
    console.log(`[SUCCESS] Transcript data saved to ${htmlFilePath}`);
}

// Helper function to convert timestamp to seconds
function convertTimestampToSeconds(timestamp) {
    const parts = timestamp.split(':').reverse();
    let seconds = 0;
    for (let i = 0; i < parts.length; i++) {
        seconds += parseInt(parts[i]) * Math.pow(60, i);
    }
    return seconds;
}

(async () => {
    try {
        const url = process.argv[2];
        if (!url) {
            console.error('Please provide a YouTube URL as a command-line argument.');
            process.exit(1);
        }
        await scrape(url);
    } catch (error) {
        console.error('Error during scraping process:', error);
    }
})();
