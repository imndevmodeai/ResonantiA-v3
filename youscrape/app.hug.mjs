import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import express from 'express';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import dotenv from 'dotenv';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config();

puppeteer.use(StealthPlugin());

const app = express();
const port = 3001;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.set('views', join(__dirname, 'views'));

const CONFIG = {
  executablePath: '/usr/bin/chromium-browser',
  waitTimes: {
    pageLoad: 3000,
    afterClick: 3500,
    transcriptLoad: 3000
  },
  outputDir: 'transcripts',
  defaultTitle: 'Default Video Title'
};

const TELEGRAM_BOT_TOKEN = process.env.YOU_SCRAPER_BOT_TOKEN;
const TELEGRAM_API_URL = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}`;

async function scrape(url) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--incognito', '--no-sandbox', '--disable-setuid-sandbox'],
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
    await browser.close();
    return null;
  }

  const videoInfo = await getVideoInfo(page);
  await browser.close();

  return { transcriptData, videoInfo };
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

app.get('/', (req, res) => {
  res.render('index');
});

app.post('/scrape', async (req, res) => {
  const url = req.body.url;
  try {
    const result = await scrape(url);
    if (result) {
      const transcriptText = result.transcriptData.map(segment => `${segment.timestamp}: ${segment.text}`).join('\n');
      const videoInfo = result.videoInfo;

      // Send the transcript to the Telegram user
      const telegramUserId = req.body.userId;
      const telegramMessage = `Transcript for ${videoInfo.title}:\n\n${transcriptText}`;
      await sendTelegramMessage(telegramUserId, telegramMessage);

      res.send('Transcript sent to Telegram user.');
    } else {
      res.send('Failed to scrape transcript.');
    }
  } catch (error) {
    console.error('Error scraping transcript:', error);
    res.send('An error occurred while scraping the transcript.');
  }
});

async function sendTelegramMessage(userId, message) {
  try {
    const response = await axios.post(`${TELEGRAM_API_URL}/sendMessage`, {
      chat_id: userId,
      text: message
    });

    if (response.status === 200) {
      console.log('Message sent to Telegram user.');
    } else {
      console.error('Error sending message to Telegram user:', response.data);
    }
  } catch (error) {
    console.error('Error sending message to Telegram user:', error);
  }
}

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});