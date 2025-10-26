require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// Initialize bot
const token = process.env.YOU_SCRAPER_BOT_TOKEN;
const bot = new TelegramBot(token, { polling: true });

// Create transcripts directory
const transcriptsDir = path.join(__dirname, 'transcripts');
try {
    if (!fs.existsSync(transcriptsDir)) {
        fs.mkdirSync(transcriptsDir, { recursive: true });
        console.log(`Created directory: ${transcriptsDir}`);
    }
} catch (error) {
    console.error(`Could not create transcripts directory: ${error.message}`);
    console.log('Bot will continue but files may not be saved properly.');
}

// Helper function to slugify text
function slugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')           // Replace spaces with hyphens
        .replace(/[^\w\-]+/g, '')       // Remove non-word characters
        .replace(/\-\-+/g, '-')         // Replace multiple hyphens with one
        .trim();                        // Remove leading/trailing whitespace
}

// Scraping function
async function scrapeTextFile(url) {
    const browser = await puppeteer.launch({ 
        headless: true, 
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--incognito'] 
    });
    const page = await browser.newPage();
    try {
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    } catch (error) {
        if (error.name === 'TimeoutError') {
            throw new Error('TimeoutError');
        }
        throw error;
    }

    // Extract title
    let title = await page.title();
    if (!title) title = "Untitled";

    let extractedText = '';

    // Check if it's a YouTube URL and try to get transcript
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        try {
            console.log('Detected YouTube URL, attempting to extract transcript...');
            
            // Wait for page to fully load
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Try multiple approaches to find transcript
            let transcriptFound = false;
            
            // Approach 1: Try to find and click More button, then transcript
            try {
                console.log('Trying approach 1: More button method...');
                
                // Scroll down to find the More button
                await page.evaluate(() => {
                    window.scrollTo(0, 1000);
                });
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Try to find More button with more comprehensive selectors
                const moreButtonClicked = await page.evaluate(() => {
                    const selectors = [
                        '#expand',
                        'button[aria-label="More actions"]',
                        'ytd-button-renderer #button[aria-label="More actions"]',
                        '#more',
                        'button[aria-label*="More"]',
                        'ytd-menu-renderer button',
                        'button[aria-label*="actions"]',
                        'ytd-button-renderer button',
                        '.ytd-video-primary-info-renderer button',
                        'button[aria-label*="Show more"]'
                    ];
                    
                    for (const selector of selectors) {
                        const button = document.querySelector(selector);
                        if (button && button.offsetParent !== null && button.offsetWidth > 0) {
                            console.log('Found More button with selector:', selector);
                            button.click();
                            return true;
                        }
                    }
                    return false;
                });
                
                if (moreButtonClicked) {
                    console.log('Clicked More button');
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    
                    // Try to find transcript button
                    const transcriptClicked = await page.evaluate(() => {
                        const selectors = [
                            '[aria-label*="transcript"]',
                            'tp-yt-paper-item',
                            'ytd-menu-service-item-renderer',
                            'button[aria-label*="transcript"]',
                            'button[aria-label*="Show transcript"]'
                        ];
                        
                        for (const selector of selectors) {
                            const button = document.querySelector(selector);
                            if (button && button.offsetParent !== null) {
                                console.log('Found transcript button with selector:', selector);
                                button.click();
                                return true;
                            }
                        }
                        
                        // Try to find by text content
                        const allElements = document.querySelectorAll('button, tp-yt-paper-item, ytd-menu-service-item-renderer, [role="menuitem"]');
                        for (const element of allElements) {
                            if (element.textContent && element.textContent.toLowerCase().includes('transcript')) {
                                console.log('Found transcript button by text:', element.textContent);
                                element.click();
                                return true;
                            }
                        }
                        return false;
                    });
                    
                    if (transcriptClicked) {
                        console.log('Clicked transcript button');
                        await new Promise(resolve => setTimeout(resolve, 5000));
                        
                        // Extract transcript
                        const transcriptText = await page.evaluate(() => {
                            const selectors = [
                                'ytd-transcript-segment-renderer',
                                '.segment-text',
                                '[data-testid="transcript"] .segment',
                                '.ytd-transcript-segment-renderer'
                            ];
                            
                            for (const selector of selectors) {
                                const segments = document.querySelectorAll(selector);
                                if (segments.length > 0) {
                                    return Array.from(segments).map(segment => {
                                        const timestamp = segment.querySelector('.segment-timestamp')?.textContent?.trim() || 
                                                       segment.querySelector('[data-testid="timestamp"]')?.textContent?.trim() || '';
                                        const text = segment.querySelector('.segment-text')?.textContent?.trim() || 
                                                   segment.textContent?.trim() || '';
                                        return `${timestamp}: ${text}`;
                                    }).join('\n');
                                }
                            }
                            return null;
                        });
                        
                        if (transcriptText && transcriptText.length > 100) {
                            // Process transcript to get clean text without timestamps or HTML
                            const cleanTextSegments = [];
                            transcriptText.split('\n').forEach(line => {
                                // Match timestamp patterns like "0:15" or "1:23:45" and extract only the text
                                const timestampMatch = line.match(/^(\d{1,2}:\d{2}(?::\d{2})?)\s*:\s*(.+)$/);
                                if (timestampMatch) {
                                    const [, , text] = timestampMatch;
                                    cleanTextSegments.push(text.trim());
                                }
                            });
                            
                            // Join with spaces for a more natural, paragraph-like flow
                            extractedText = cleanTextSegments.join(' ');
                            transcriptFound = true;
                            console.log('Successfully extracted and cleaned YouTube transcript.');
                        }
                    }
                }
            } catch (error) {
                console.log('Approach 1 failed:', error.message);
            }
            
            // Approach 2: Try direct transcript extraction without clicking buttons
            if (!transcriptFound) {
                try {
                    console.log('Trying approach 2: Direct transcript extraction...');
                    
                    const directTranscript = await page.evaluate(() => {
                        // Look for any transcript-related elements
                        const transcriptSelectors = [
                            'ytd-transcript-body-renderer',
                            '.ytd-transcript-body-renderer',
                            '[data-testid="transcript"]',
                            '.transcript',
                            'ytd-transcript-segment-renderer'
                        ];
                        
                        for (const selector of transcriptSelectors) {
                            const container = document.querySelector(selector);
                            if (container) {
                                const segments = container.querySelectorAll('ytd-transcript-segment-renderer, .segment');
                                if (segments.length > 0) {
                                    return Array.from(segments).map(segment => {
                                        const timestamp = segment.querySelector('.segment-timestamp')?.textContent?.trim() || '';
                                        const text = segment.querySelector('.segment-text')?.textContent?.trim() || 
                                                   segment.textContent?.trim() || '';
                                        return `${timestamp}: ${text}`;
                                    }).join('\n');
                                } else {
                                    return container.textContent || '';
                                }
                            }
                        }
                        return null;
                    });
                    
                    if (directTranscript && directTranscript.length > 100) {
                        extractedText = directTranscript;
                        transcriptFound = true;
                        console.log('Successfully extracted transcript using direct method');
                    }
                } catch (error) {
                    console.log('Approach 2 failed:', error.message);
                }
            }
            
            // Approach 3: Try to find transcript in page source or meta tags
            if (!transcriptFound) {
                try {
                    console.log('Trying approach 3: Meta tags and page source...');
                    
                    const metaTranscript = await page.evaluate(() => {
                        // Check for transcript in meta tags
                        const metaTags = document.querySelectorAll('meta[name*="transcript"], meta[property*="transcript"]');
                        for (const meta of metaTags) {
                            if (meta.content && meta.content.length > 100) {
                                return meta.content;
                            }
                        }
                        
                        // Check for JSON-LD structured data
                        const jsonLd = document.querySelector('script[type="application/ld+json"]');
                        if (jsonLd) {
                            try {
                                const data = JSON.parse(jsonLd.textContent);
                                if (data.transcript || data.description) {
                                    return data.transcript || data.description;
                                }
                            } catch (e) {
                                // Ignore JSON parse errors
                            }
                        }
                        
                        return null;
                    });
                    
                    if (metaTranscript && metaTranscript.length > 100) {
                        extractedText = metaTranscript;
                        transcriptFound = true;
                        console.log('Successfully extracted transcript from meta tags');
                    }
                } catch (error) {
                    console.log('Approach 3 failed:', error.message);
                }
            }
            
            if (!transcriptFound) {
                console.log('All transcript extraction approaches failed, falling back to general content extraction');
            }
            
        } catch (error) {
            console.log('Error in YouTube transcript extraction:', error.message);
        }
    }

    // If no transcript found or not YouTube, extract general content
    if (!extractedText) {
        const html = await page.content();
        const $ = cheerio.load(html);

        // Extract text from multiple tags
        const textElements = $('h1, h2, h3, h4, h5, h6, p, li');
        const texts = [];
        textElements.each((_, element) => {
            const text = $(element).text().trim();
            if (text) texts.push(text);
        });
        if (texts.length === 0) {
            throw new Error('No content found');
        }
        extractedText = texts.join('\n\n');
    }

    const currentTime = new Date();
    const epochTime = Math.floor(currentTime.getTime() / 1000);
    const dateString = currentTime.toISOString().replace(/T|Z/g, '');
    
    await browser.close();

    // For YouTube transcripts, return clean content without headers
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        let savedFilePath = null;
        try {
            const fileName = `youtube_transcript_${dateString.replace(/[:.]/g, '-')}_${title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50)}.txt`;
            const filePath = path.join(transcriptsDir, fileName);
            
            // Create file content with the cleaned transcript
            const fileContent = `YouTube Transcript
URL: ${url}
Date: ${dateString}
Title: ${title}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${extractedText}`;
            
            fs.writeFileSync(filePath, fileContent, 'utf8');
            console.log(`✅ Transcript saved to: ${filePath}`);
            savedFilePath = filePath;
            
        } catch (error) {
            console.log(`⚠️ Could not save transcript to file in ${transcriptsDir}:`, error.message);
        }
        
        // Create the plain text content for the Telegram message
        const messageContent = `📄 Scraped Transcript
🔗 URL: ${url}
📅 Date: ${dateString}
📝 Title: ${title}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${extractedText}`;

        return { content: messageContent, title: title, isYouTube: true, videoUrl: url, savedFilePath: savedFilePath };
    } else {
        // For other URLs, keep the original header format
        const contentHeader = `📄 <b>Scraped Content</b>
🔗 <b>URL:</b> ${url}
📅 <b>Date:</b> ${dateString}
📝 <b>Title:</b> ${title}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`;
        return { content: contentHeader + extractedText, title: title, isYouTube: false, videoUrl: url };
    }
}

// Bot message handler
bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text || '';

    console.log('Received message:', text);

    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = text.match(urlRegex);
    if (urls && urls.length > 0) {
        const url = urls[0]; // Process the first URL
        try {
            // Validate URL
            new URL(url);
            await bot.sendMessage(chatId, '🔄 Processing your URL...');
            const { content, title, isYouTube, videoUrl, savedFilePath } = await scrapeTextFile(url);
            
            // Define send options based on content type
            const sendOptions = isYouTube ? {} : { parse_mode: 'HTML' };

            // Always split content if it's too long for Telegram (4096 char limit)
            const maxLength = 4096;
            if (content.length > maxLength) {
                console.log(`Content is too long (${content.length} chars), splitting into chunks...`);
                const chunks = [];
                let currentChunk = '';
                // Split by lines for non-YouTube, by sentences/words for YouTube to avoid breaking words
                const splitter = isYouTube ? /(?<=[.?!])\s+/ : /\r?\n/;
                const lines = content.split(splitter);
                
                for (const line of lines) {
                    if (currentChunk.length + line.length + 1 > maxLength) {
                        chunks.push(currentChunk);
                        currentChunk = line;
                    } else {
                        currentChunk += (currentChunk ? (isYouTube ? ' ' : '\n') : '') + line;
                    }
                }
                if (currentChunk) chunks.push(currentChunk);
                
                console.log(`Sending content in ${chunks.length} chunks.`);
                for (let i = 0; i < chunks.length; i++) {
                    const chunkContent = chunks[i];
                    await bot.sendMessage(chatId, chunkContent, sendOptions);
                    
                    // Add a small delay between messages
                    if (i < chunks.length - 1) {
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                }

            } else {
                await bot.sendMessage(chatId, content, sendOptions);
            }

            // Inform user about saved file if it's a YouTube transcript, regardless of chunking
            if (isYouTube && savedFilePath) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                try {
                    if (fs.existsSync(savedFilePath)) {
                        // Send the file to Telegram
                        await bot.sendDocument(chatId, savedFilePath, {
                            caption: `💾 <b>Transcript saved and ready for download!</b>\n📁 <b>File:</b> <code>${path.basename(savedFilePath)}</code>`,
                            parse_mode: 'HTML'
                        });
                    } else {
                        await bot.sendMessage(chatId, `💾 <b>Transcript saved to file:</b> <code>${path.basename(savedFilePath)}</code>\n⚠️ File could not be located for sending`, { parse_mode: 'HTML' });
                    }
                } catch (error) {
                    console.log('Could not send file:', error.message);
                    await bot.sendMessage(chatId, `💾 <b>Transcript saved to file:</b> <code>${path.basename(savedFilePath)}</code>\n⚠️ File could not be sent directly`, { parse_mode: 'HTML' });
                }
            }

        } catch (error) {
            if (error.message === 'Invalid URL') {
                await bot.sendMessage(chatId, 'The provided URL is invalid.');
            } else if (error.message === 'TimeoutError') {
                await bot.sendMessage(chatId, 'The page took too long to load. Please try again later.');
            } else if (error.message === 'No content found') {
                await bot.sendMessage(chatId, 'No readable content was found on the page.');
            } else {
                console.error('Error:', error);
                await bot.sendMessage(chatId, 'An error occurred while processing your request.');
            }
        }
    }
});

console.log('Bot is active and waiting for URLs...');
