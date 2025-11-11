import express from 'express';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import dotenv from 'dotenv';

dotenv.config();

puppeteer.use(StealthPlugin());

const app = express();
const port = 3001;

app.use(express.json());

// In-memory storage for transcript data (keyed by videoId)
const transcriptStore = new Map();

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

async function scrape(url) {
  let browser;
  
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--incognito', '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
      executablePath: CONFIG.executablePath
    });

    const page = await browser.newPage();

    // Handle page errors
    page.on('error', (err) => console.error('Page error:', err));
    page.on('pageerror', (err) => console.error('Page pageerror:', err));

    console.log('Navigating to the page...');
    await page.goto(url);
    await new Promise(resolve => setTimeout(resolve, CONFIG.waitTimes.pageLoad)); // Wait for initial page load

    // First, click the "More" button if available to reveal options like "Show transcript"
    await clickMoreButton(page);

    // Now, try to click the "Show transcript" button
    await clickShowTranscriptButton(page);

    // After clicking the "Show transcript" button, wait for the transcript to load
    await new Promise(resolve => setTimeout(resolve, CONFIG.waitTimes.transcriptLoad));

    const transcriptData = await getTranscriptText(page);
    if (!transcriptData) {
      console.error('Failed to get transcript text');
      return null;
    }

    const videoInfo = await getVideoInfo(page);

    return { transcriptData, videoInfo };
  } catch (error) {
    console.error('Error in scrape function:', error);
    return null;
  } finally {
    // CRITICAL: Always close the browser to prevent resource leaks
    if (browser) {
      try {
        await browser.close();
        console.log('Browser closed successfully');
      } catch (closeError) {
        console.error('Error closing browser:', closeError);
      }
    }
  }
}

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
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait after scroll
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

async function clickShowTranscriptButton(page) {
  console.log("Looking for Show transcript button...");
  try {
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for menu to expand

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
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait after scroll

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

async function getTranscriptText(page) {
  console.log("Getting transcript text...");
  try {
    await new Promise(resolve => setTimeout(resolve, 2000));

    const found = await scrollPageToFindElement(page, 'ytd-transcript-segment-renderer');
    if (!found) {
      console.log("Could not find transcript container");
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

    return transcriptData;
  } catch (error) {
    console.error('Error getting transcript text:', error);
    return null;
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

async function scrollPageToFindElement(page, selector) {
  return await page.evaluate(async (selector) => {
    const maxScrolls = 10;
    const scrollStep = 500;

    for (let i = 0; i < maxScrolls; i++) {
      // Check if element exists
      const element = document.querySelector(selector);
      if (element) {
        element.scrollIntoView({ behavior:'smooth', block: 'center' });
        return true;
      }

      // Scroll down if element not found
      window.scrollBy(0, scrollStep);
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    return false;
  }, selector);
}

app.post('/api/scrape', async (req, res) => {
  const url = req.body.url;
  try {
    const result = await scrape(url);
    if (result) {
      res.json({ success: true, transcriptData: result.transcriptData, videoInfo: result.videoInfo });
    } else {
      res.json({ success: false });
    }
  } catch (error) {
    console.error('Error scraping transcript:', error);
    res.json({ success: false });
  }
});

// Store transcript data for the web viewer
app.post('/api/scrape/store', (req, res) => {
  const { videoId, transcriptData, videoInfo } = req.body;
  if (videoId && transcriptData) {
    transcriptStore.set(videoId, {
      transcriptData,
      videoInfo: videoInfo || {},
      storedAt: new Date().toISOString()
    });
    console.log(`Stored transcript data for video: ${videoId}`);
    res.json({ success: true, message: 'Transcript data stored' });
  } else {
    res.status(400).json({ success: false, message: 'Missing videoId or transcriptData' });
  }
});

// Helper function to convert timestamp to seconds
function timestampToSeconds(timestamp) {
  const parts = timestamp.split(':').reverse();
  let seconds = 0;
  for (let i = 0; i < parts.length; i++) {
    seconds += parseInt(parts[i] || 0) * Math.pow(60, i);
  }
  return seconds;
}

// Serve the web viewer page
app.get('/view/:videoId', (req, res) => {
  const { videoId } = req.params;
  const storedData = transcriptStore.get(videoId);
  
  if (!storedData) {
    res.status(404).send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Transcript Not Found</title>
        <style>
          body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        </style>
      </head>
      <body>
        <h1>Transcript Not Found</h1>
        <p>The transcript for this video is not available. Please scrape it first via the Telegram bot.</p>
      </body>
      </html>
    `);
    return;
  }
  
  const { transcriptData, videoInfo } = storedData;
  const videoUrl = videoInfo.url || `https://www.youtube.com/watch?v=${videoId}`;
  const videoTitle = videoInfo.title || 'YouTube Video';
  
  // Generate HTML with embedded video and clickable transcript
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${videoTitle} - Transcript Viewer</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }
    
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }
    
    .header h1 {
      font-size: 24px;
      margin-bottom: 10px;
      word-wrap: break-word;
    }
    
    .video-container {
      position: relative;
      padding-bottom: 56.25%; /* 16:9 aspect ratio */
      height: 0;
      overflow: hidden;
      background: #000;
    }
    
    .video-container iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border: none;
    }
    
    .transcript-container {
      padding: 30px;
      max-height: 60vh;
      overflow-y: auto;
    }
    
    .transcript-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 20px;
      color: #333;
      border-bottom: 2px solid #667eea;
      padding-bottom: 10px;
    }
    
    .transcript-text {
      line-height: 1.8;
      font-size: 16px;
      color: #444;
    }
    
    .timestamp-link {
      color: #667eea;
      text-decoration: none;
      cursor: pointer;
      padding: 2px 6px;
      border-radius: 4px;
      transition: all 0.2s;
      display: inline-block;
      margin-right: 8px;
      font-weight: 500;
    }
    
    .timestamp-link:hover {
      background: #667eea;
      color: white;
      transform: translateY(-1px);
    }
    
    .timestamp-link:active {
      transform: translateY(0);
    }
    
    .text-segment {
      margin-bottom: 12px;
      display: inline;
    }
    
    @media (max-width: 768px) {
      .container {
        margin: 10px;
        border-radius: 8px;
      }
      
      .header {
        padding: 20px;
      }
      
      .header h1 {
        font-size: 18px;
      }
      
      .transcript-container {
        padding: 20px;
        max-height: 50vh;
      }
      
      .transcript-text {
        font-size: 14px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>${videoTitle}</h1>
    </div>
    
    <div class="video-container">
      <iframe 
        id="youtube-player"
        src="https://www.youtube.com/embed/${videoId}?enablejsapi=1&origin=${req.protocol}://${req.get('host')}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
      </iframe>
    </div>
    
    <div class="transcript-container">
      <div class="transcript-title">📝 Transcript</div>
      <div class="transcript-text" id="transcript-text">
        ${transcriptData.map(segment => {
          const timestamp = segment.timestamp || '';
          const text = segment.text || '';
          const seconds = timestamp ? timestampToSeconds(timestamp) : 0;
          
          if (timestamp) {
            return `<span class="text-segment"><a href="#" class="timestamp-link" data-time="${seconds}">[${timestamp}]</a>${text} </span>`;
          } else {
            return `<span class="text-segment">${text} </span>`;
          }
        }).join('')}
      </div>
    </div>
  </div>
  
  <script>
    // YouTube IFrame API
    let player;
    
    // Load YouTube IFrame API
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    
    // This function will be called by YouTube IFrame API when ready
    window.onYouTubeIframeAPIReady = function() {
      player = new YT.Player('youtube-player', {
        events: {
          'onReady': onPlayerReady
        }
      });
    };
    
    function onPlayerReady(event) {
      // Add click handlers to timestamp links
      const timestampLinks = document.querySelectorAll('.timestamp-link');
      timestampLinks.forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const time = parseFloat(link.getAttribute('data-time'));
          if (player && typeof player.seekTo === 'function') {
            player.seekTo(time, true);
            player.playVideo();
          }
        });
      });
    }
    
    // Fallback method using URL manipulation if API fails to load
    setTimeout(() => {
      if (!player) {
        console.log('YouTube API not loaded, using fallback method');
        const timestampLinks = document.querySelectorAll('.timestamp-link');
        timestampLinks.forEach(link => {
          link.addEventListener('click', (e) => {
            e.preventDefault();
            const time = parseFloat(link.getAttribute('data-time'));
            const iframe = document.getElementById('youtube-player');
            if (iframe) {
              // Update iframe src with timestamp
              const baseUrl = iframe.src.split('?')[0];
              const origin = window.location.origin;
              iframe.src = baseUrl + '?enablejsapi=1&start=' + Math.floor(time) + '&autoplay=1&origin=' + origin;
            }
          });
        });
      }
    }, 2000);
  </script>
</body>
</html>
  `;
  
  res.send(html);
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server listening on port ${port} (accessible from all interfaces)`);
  console.log(`Web viewer available at:`);
  console.log(`  - Local: http://localhost:${port}/view/:videoId`);
  console.log(`  - Remote: http://YOUR_IP:${port}/view/:videoId`);
  console.log(`  (Replace YOUR_IP with your machine's IP address for remote access)`);
});