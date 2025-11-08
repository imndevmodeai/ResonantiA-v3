require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const puppeteer = require('puppeteer-core'); // Changed to puppeteer-core
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Initialize bot
const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) {
    console.error('ERROR: TELEGRAM_BOT_TOKEN not found in environment variables.');
    console.error('Please create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here');
    process.exit(1);
}

const bot = new TelegramBot(token, { polling: true });

// Create saves directory
const directoryName = path.join(__dirname, 'saves');
if (!fs.existsSync(directoryName)) {
    fs.mkdirSync(directoryName, { recursive: true });
    console.log(`Created saves directory: ${directoryName}`);
}

// Helper function to find Chrome executable path
function findChromeExecutable() {
    const platform = os.platform();
    const possiblePaths = [];
    
    if (platform === 'linux') {
        possiblePaths.push(
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/snap/bin/chromium',
            '/usr/local/bin/chrome',
            '/usr/local/bin/chromium'
        );
    } else if (platform === 'darwin') {
        possiblePaths.push(
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium'
        );
    } else if (platform === 'win32') {
        possiblePaths.push(
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe'
        );
    }
    
    for (const chromePath of possiblePaths) {
        if (fs.existsSync(chromePath)) {
            console.log(`Found Chrome at: ${chromePath}`);
            return chromePath;
        }
    }
    
    return null;
}

// Helper function to slugify text
function slugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]+/g, '')
        .replace(/\-\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '')
        .trim();
}

// Enhanced scraping function with robust error handling
async function scrapeTextFile(url) {
    let browser = null;
    
    try {
        // Validate URL
        if (!url || (!url.includes('huggingface.co') && !url.includes('hf.co'))) {
            throw new Error('Invalid URL: Must be a Hugging Face URL');
        }
        
        // Find Chrome executable
        const chromePath = findChromeExecutable();
        if (!chromePath) {
            throw new Error('Chrome/Chromium not found. Please install Chrome or run: npx puppeteer browsers install chrome');
        }
        
        // Launch browser with explicit path
        console.log(`Launching browser with executable: ${chromePath}`);
        browser = await puppeteer.launch({
            headless: true, // Changed to true for production (set to false for debugging)
            executablePath: chromePath,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--incognito'
            ],
            timeout: 30000 // 30 second timeout
        });
        
        const page = await browser.newPage();
        
        // Set user agent to avoid detection
        await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        // Navigate with timeout
        console.log(`Navigating to: ${url}`);
        await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Wait for content to load
        await page.waitForTimeout(2000);
        
        // Get HTML content
        const html = await page.content();
        const $ = cheerio.load(html);
        
        // Extract title with multiple fallbacks
        let title = $('title').text().trim();
        if (!title || title === '') {
            title = $('h1').first().text().trim();
        }
        if (!title || title === '') {
            title = $('meta[property="og:title"]').attr('content') || '';
        }
        if (!title || title === '') {
            title = 'Untitled';
        }
        
        // Extract text content from multiple sources
        const paragraphs = [];
        
        // Try main content areas
        const contentSelectors = [
            'main p',
            'article p',
            '.content p',
            '[role="main"] p',
            'div[class*="message"]',
            'div[class*="chat"]',
            'p'
        ];
        
        for (const selector of contentSelectors) {
            $(selector).each((_, element) => {
                const text = $(element).text().trim();
                if (text && text.length > 10) { // Filter out very short text
                    paragraphs.push(text);
                }
            });
            if (paragraphs.length > 0) break; // Use first selector that finds content
        }
        
        // Fallback: extract all text if no paragraphs found
        if (paragraphs.length === 0) {
            const bodyText = $('body').text().trim();
            if (bodyText) {
                paragraphs.push(bodyText);
            }
        }
        
        // Join paragraphs with double newlines
        const text = paragraphs.join('\n\n');
        
        if (!text || text.trim().length === 0) {
            throw new Error('No text content found on the page');
        }
        
        // Generate filename with timestamp
        const currentTime = new Date();
        const epochTime = Math.floor(currentTime.getTime() / 1000);
        const dateString = currentTime.toISOString().replace(/T|Z/g, '').replace(/:/g, '-');
        const fileName = `${dateString}_hf-chat_${slugify(title)}_response.txt`;
        const filePath = path.join(directoryName, fileName);
        
        // Create file header with metadata
        const fileHeader = `URL: ${url}
Epoch Time: ${epochTime}
Date: ${currentTime.toISOString()}
Title: ${title}
Content Length: ${text.length} characters
Paragraphs Extracted: ${paragraphs.length}

${'='.repeat(80)}

`;
        
        // Write file with error handling
        await new Promise((resolve, reject) => {
            fs.writeFile(filePath, fileHeader + text, 'utf8', (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log(`Text saved to ${fileName} successfully!`);
                    console.log(`File size: ${(fileHeader.length + text.length) / 1024} KB`);
                    resolve();
                }
            });
        });
        
        await browser.close();
        browser = null;
        
        return { 
            filePath, 
            fileName,
            contentLength: text.length,
            paragraphsCount: paragraphs.length
        };
        
    } catch (error) {
        console.error('Error scraping text file:', error);
        
        // Clean up browser on error
        if (browser) {
            try {
                await browser.close();
            } catch (closeError) {
                console.error('Error closing browser:', closeError);
            }
        }
        
        // Return detailed error information
        return {
            error: true,
            message: error.message,
            stack: error.stack
        };
    }
}

// Bot message handler with comprehensive error handling
bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text || '';
    const username = msg.from?.username || msg.from?.first_name || 'Unknown';
    
    console.log(`[${new Date().toISOString()}] Received message from ${username}: ${text.substring(0, 100)}`);
    
    // Check if message contains Hugging Face URL
    if (text.includes('huggingface.co') || text.includes('hf.co')) {
        try {
            // Send processing message
            await bot.sendMessage(chatId, '🔄 Processing your Hugging Face chat...', {
                parse_mode: 'HTML'
            });
            
            // Extract URL from message (handle cases where URL might be part of longer text)
            const urlMatch = text.match(/(https?:\/\/[^\s]+(?:huggingface\.co|hf\.co)[^\s]*)/);
            const url = urlMatch ? urlMatch[1] : text.trim();
            
            console.log(`Extracted URL: ${url}`);
            
            // Scrape the content
            const result = await scrapeTextFile(url);
            
            if (result && !result.error) {
                const { filePath, fileName, contentLength, paragraphsCount } = result;
                
                // Verify file exists before sending
                if (!fs.existsSync(filePath)) {
                    throw new Error('File was created but cannot be found');
                }
                
                // Get file stats
                const stats = fs.statSync(filePath);
                const fileSizeKB = (stats.size / 1024).toFixed(2);
                
                // Send document with informative caption
                try {
                    await bot.sendDocument(chatId, filePath, {
                        caption: `✅ Successfully saved chat!\n\n📄 File: ${fileName}\n📊 Size: ${fileSizeKB} KB\n📝 Content: ${contentLength} characters\n📑 Paragraphs: ${paragraphsCount}`,
                        parse_mode: 'HTML'
                    });
                    console.log(`Successfully sent file to chat ${chatId}`);
                } catch (sendError) {
                    console.error('Error sending file:', sendError);
                    
                    // Fallback: send file info if document send fails
                    await bot.sendMessage(chatId, 
                        `⚠️ File saved but couldn't send as document.\n\n` +
                        `File: ${fileName}\n` +
                        `Path: ${filePath}\n` +
                        `Size: ${fileSizeKB} KB\n\n` +
                        `Please check the saves directory manually.`,
                        { parse_mode: 'HTML' }
                    );
                }
            } else {
                // Handle error result
                const errorMsg = result?.message || 'Unknown error occurred';
                console.error(`Scraping failed: ${errorMsg}`);
                
                await bot.sendMessage(chatId, 
                    `❌ Error processing your request:\n\n<code>${errorMsg}</code>\n\n` +
                    `Please check:\n` +
                    `1. URL is valid and accessible\n` +
                    `2. Chrome/Chromium is installed\n` +
                    `3. Network connection is stable`,
                    { parse_mode: 'HTML' }
                );
            }
        } catch (error) {
            console.error('Error in message handler:', error);
            await bot.sendMessage(chatId, 
                `❌ Unexpected error: ${error.message}\n\nPlease try again or contact support.`,
                { parse_mode: 'HTML' }
            );
        }
    } else {
        // Send helpful message for non-URL messages
        await bot.sendMessage(chatId, 
            `👋 Hi! Send me a Hugging Face chat URL (huggingface.co or hf.co) and I'll scrape and save it for you.\n\n` +
            `Example: https://hf.co/chat/r/ZTqJv4Y`,
            { parse_mode: 'HTML' }
        );
    }
});

// Handle bot errors
bot.on('error', (error) => {
    console.error('Telegram Bot Error:', error);
});

bot.on('polling_error', (error) => {
    console.error('Polling Error:', error);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down gracefully...');
    bot.stopPolling();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down gracefully...');
    bot.stopPolling();
    process.exit(0);
});

console.log('🤖 Telegram Bot started successfully!');
console.log('📁 Saves directory:', directoryName);
console.log('⏳ Waiting for messages...');
