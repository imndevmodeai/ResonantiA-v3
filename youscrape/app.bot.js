// bot.js
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
require('dotenv').config();

const TELEGRAM_BOT_TOKEN = process.env.YOU_SCRAPER_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN;
const API_URL = process.env.YOUSCRAPE_API_URL || 'http://localhost:3001/api/scrape';
const WEB_VIEWER_URL = process.env.WEB_VIEWER_URL || 'http://localhost:3001/view';
const ENABLE_TELEGRAM_BOT = process.env.ENABLE_TELEGRAM_BOT === 'true' || process.env.ENABLE_TELEGRAM_BOT === '1';

if (!TELEGRAM_BOT_TOKEN) {
  console.error('ERROR: YOU_SCRAPER_BOT_TOKEN or TELEGRAM_BOT_TOKEN not set in environment variables');
  console.error('Please set the token in your .env file:');
  console.error('  YOU_SCRAPER_BOT_TOKEN=your_bot_token_here');
  console.error('  ENABLE_TELEGRAM_BOT=true');
  process.exit(1);
}

if (!ENABLE_TELEGRAM_BOT) {
  console.log('ENABLE_TELEGRAM_BOT not set to true. Bot disabled.');
  console.log('To enable: Set ENABLE_TELEGRAM_BOT=true in your .env file');
  process.exit(0);
}

// Function to close any existing bot instances
async function closeExistingBotInstances() {
  try {
    // Get current process ID to avoid killing ourselves
    const currentPid = process.pid;
    
    // Find all node processes running app.bot.js
    const { stdout } = await execAsync('ps aux | grep "app.bot.js" | grep -v grep');
    
    if (stdout) {
      const lines = stdout.trim().split('\n').filter(line => line.trim());
      const pidsToKill = [];
      
      lines.forEach(line => {
        const parts = line.trim().split(/\s+/);
        const pid = parseInt(parts[1]);
        if (pid && pid !== currentPid) {
          pidsToKill.push(pid);
        }
      });
      
      if (pidsToKill.length > 0) {
        console.log(`Found ${pidsToKill.length} existing bot instance(s), closing them...`);
        for (const pid of pidsToKill) {
          try {
            process.kill(pid, 'SIGTERM');
            console.log(`Sent SIGTERM to process ${pid}`);
          } catch (err) {
            // If SIGTERM fails, try SIGKILL
            try {
              process.kill(pid, 'SIGKILL');
              console.log(`Sent SIGKILL to process ${pid}`);
            } catch (killErr) {
              console.log(`Could not kill process ${pid}: ${killErr.message}`);
            }
          }
        }
        // Wait a bit for processes to close
        await new Promise(resolve => setTimeout(resolve, 2000));
        console.log('Existing instances closed.');
      }
    }
  } catch (error) {
    // If grep doesn't find anything, that's fine - no existing instances
    if (error.code !== 1) { // Exit code 1 means no matches found
      console.log('Could not check for existing instances:', error.message);
    }
  }
}

// Close existing instances before starting
let bot = null;

function setupBotHandlers(bot) {
  // Command: /start
  bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const welcomeMessage = `
🤖 *YouTube Transcript Scraper Bot*

Welcome! I can help you extract transcripts from YouTube videos.

*How to use:*
• Send me a YouTube URL directly
• Or use: \`/scrape <YouTube URL>\`

*Example:*
\`/scrape https://www.youtube.com/watch?v=VIDEO_ID\`

*Commands:*
/start - Show this welcome message
/help - Show help information
/scrape <URL> - Scrape transcript from YouTube URL
    `;
    
    bot.sendMessage(chatId, welcomeMessage, { parse_mode: 'Markdown' });
  });

  // Command: /help
  bot.onText(/\/help/, (msg) => {
    const chatId = msg.chat.id;
    const helpMessage = `
📖 *Help - YouTube Transcript Scraper Bot*

*Usage:*
1. Send a YouTube URL directly in a message
2. Or use the command: \`/scrape <YouTube URL>\`

*Supported URL formats:*
• https://www.youtube.com/watch?v=VIDEO_ID
• https://youtu.be/VIDEO_ID
• www.youtube.com/watch?v=VIDEO_ID

*Note:* The backend server must be running on port 3001 for this bot to work.

For issues or questions, check the server logs.
    `;
    
    bot.sendMessage(chatId, helpMessage, { parse_mode: 'Markdown' });
  });

  // Command: /scrape <URL>
  bot.onText(/\/scrape (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
  const url = match[1];
    
    // Validate URL
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
      bot.sendMessage(chatId, '❌ Please provide a valid YouTube URL');
      return;
    }
    
    // Send "processing" message
    const processingMsg = await bot.sendMessage(chatId, '⏳ Scraping transcript... This may take a moment.');
    
    try {
      // Call the backend API
      const response = await axios.post(API_URL, { url }, {
        timeout: 120000 // 2 minute timeout
      });
      
      if (response.data.success) {
        const { transcriptData, videoInfo } = response.data;
        
        // Extract only text (no timestamps)
        const textOnly = extractTextOnly(transcriptData);
        
        // Get video ID for the viewer link
        const videoId = extractVideoId(videoInfo?.url || url);
        
        // Delete processing message
        bot.deleteMessage(chatId, processingMsg.message_id);
        
        // Format message with title and text transcript
        let message = '';
        if (videoInfo && videoInfo.title) {
          message += `📹 <b>${videoInfo.title}</b>\n\n`;
        }
        
        message += `<b>Transcript:</b>\n\n${textOnly}`;
        
        // Create inline keyboard button for the viewer link
        let replyMarkup = null;
        if (videoId) {
          const viewerLink = `${WEB_VIEWER_URL}/${videoId}`;
          replyMarkup = {
            inline_keyboard: [[
              {
                text: '🎬 View Video with Clickable Timestamps',
                url: viewerLink
              }
            ]]
          };
        }
        
        // Send transcript data to server for storage (for the viewer)
        try {
          await axios.post(`${API_URL}/store`, {
            videoId: videoId,
            transcriptData: transcriptData,
            videoInfo: videoInfo
          });
        } catch (storeError) {
          console.error('Failed to store transcript data:', storeError.message);
        }
        
        // Split message into chunks, but limit to 5 chunks max in Telegram
        const chunks = splitMessage(message);
        const totalChunks = chunks.length;
        const maxTelegramChunks = 5;
        const chunksToSend = chunks.slice(0, maxTelegramChunks);
        const hasMoreChunks = totalChunks > maxTelegramChunks;
        
        console.log(`Transcript has ${totalChunks} chunks. Sending first ${chunksToSend.length} chunks to Telegram...`);
        
        // Send up to 5 chunks with minimal delays
        for (let i = 0; i < chunksToSend.length; i++) {
          const chunk = chunksToSend[i];
          const isLastTelegramChunk = (i === chunksToSend.length - 1);
          
          // Format chunk message - use HTML for continuation header
          const chunkMessage = i === 0 
            ? chunk 
            : `<b>[Continued ${i + 1}/${chunksToSend.length}]</b>\n\n${chunk}`;
          
          let sent = false;
          let retries = 0;
          const maxRetries = 3;
          
          while (!sent && retries < maxRetries) {
            try {
              const parseMode = chunkMessage.includes('<b>') ? 'HTML' : 'Markdown';
              await bot.sendMessage(chatId, chunkMessage, { 
                parse_mode: parseMode,
                disable_web_page_preview: false
              });
              sent = true;
              console.log(`✅ Sent chunk ${i + 1}/${chunksToSend.length}`);
            } catch (error) {
              retries++;
              console.error(`❌ Error sending chunk ${i + 1}/${chunksToSend.length} (attempt ${retries}/${maxRetries}):`, error.message);
              
              if (retries < maxRetries) {
                const waitTime = 500 * retries;
                await new Promise(resolve => setTimeout(resolve, waitTime));
              }
            }
          }
          
          // Small delay between chunks (reduced since we're only sending 5 max)
          if (i < chunksToSend.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        }
        
        // Always send the button after the chunks (for full transcript viewer)
        if (replyMarkup) {
          try {
            const buttonMessage = hasMoreChunks 
              ? `📝 <b>Preview complete</b> (showing ${chunksToSend.length} of ${totalChunks} sections)\n\n🎬 <b>View Full Transcript with Video:</b>`
              : `📝 <b>Transcript complete</b>\n\n🎬 <b>View Full Transcript with Video:</b>`;
            
            await bot.sendMessage(chatId, buttonMessage, {
              parse_mode: 'HTML',
              reply_markup: replyMarkup
            });
            console.log('✅ Sent full transcript viewer button');
          } catch (buttonError) {
            console.error('❌ Failed to send button:', buttonError.message);
            // Retry once
            try {
              await new Promise(resolve => setTimeout(resolve, 1000));
              await bot.sendMessage(chatId, '🎬 View Full Transcript:', {
                reply_markup: replyMarkup
              });
              console.log('✅ Button sent on retry');
            } catch (retryError) {
              console.error('❌ Failed to send button on retry:', retryError.message);
            }
          }
        }
        
        console.log(`✅ Finished sending ${chunksToSend.length} chunks${hasMoreChunks ? ` (${totalChunks - chunksToSend.length} more available in full viewer)` : ''}`);
      } else {
        bot.deleteMessage(chatId, processingMsg.message_id);
        bot.sendMessage(chatId, '❌ Failed to scrape transcript. The video may not have a transcript available, or there was an error processing the request.');
      }
    } catch (error) {
      console.error('Error in /scrape command:', error);
      bot.deleteMessage(chatId, processingMsg.message_id);
      
      if (error.code === 'ECONNREFUSED') {
        bot.sendMessage(chatId, '❌ Cannot connect to the backend server. Please ensure the server is running on port 3001.');
      } else if (error.code === 'ETIMEDOUT') {
        bot.sendMessage(chatId, '❌ Request timed out. The video may be too long or the server is overloaded.');
      } else {
        bot.sendMessage(chatId, `❌ Error: ${error.message}`);
      }
    }
  });

  // Handle direct YouTube URLs in messages (not commands)
  bot.on('message', async (msg) => {
    // Skip if it's a command
    if (msg.text && msg.text.startsWith('/')) {
      return;
    }
    
    const chatId = msg.chat.id;
    const text = msg.text || '';
    
    // Extract YouTube URL
    const url = extractYouTubeUrl(text);
    
    if (url) {
      // Send "processing" message
      const processingMsg = await bot.sendMessage(chatId, '⏳ Scraping transcript... This may take a moment.');
      
      try {
        // Call the backend API
        const response = await axios.post(API_URL, { url }, {
          timeout: 120000 // 2 minute timeout
        });
        
        if (response.data.success) {
          const { transcriptData, videoInfo } = response.data;
          
          // Extract only text (no timestamps)
          const textOnly = extractTextOnly(transcriptData);
          
          // Get video ID for the viewer link
          const videoId = extractVideoId(videoInfo?.url || url);
          
          // Delete processing message
          bot.deleteMessage(chatId, processingMsg.message_id);
          
          // Format message with title and text transcript
          let message = '';
          if (videoInfo && videoInfo.title) {
            message += `📹 <b>${videoInfo.title}</b>\n\n`;
          }
          
          message += `<b>Transcript:</b>\n\n${textOnly}`;
          
          // Create inline keyboard button for the viewer link
          let replyMarkup = null;
          if (videoId) {
            const viewerLink = `${WEB_VIEWER_URL}/${videoId}`;
            replyMarkup = {
              inline_keyboard: [[
                {
                  text: '🎬 View Video with Clickable Timestamps',
                  url: viewerLink
                }
              ]]
            };
          }
          
          // Send transcript data to server for storage (for the viewer)
          try {
            await axios.post(`${API_URL}/store`, {
              videoId: videoId,
              transcriptData: transcriptData,
              videoInfo: videoInfo
            });
          } catch (storeError) {
            console.error('Failed to store transcript data:', storeError.message);
          }
          
          // Split message into chunks, but limit to 5 chunks max in Telegram
          const chunks = splitMessage(message);
          const totalChunks = chunks.length;
          const maxTelegramChunks = 5;
          const chunksToSend = chunks.slice(0, maxTelegramChunks);
          const hasMoreChunks = totalChunks > maxTelegramChunks;
          
          console.log(`Transcript has ${totalChunks} chunks. Sending first ${chunksToSend.length} chunks to Telegram...`);
          
          // Send up to 5 chunks with minimal delays
          for (let i = 0; i < chunksToSend.length; i++) {
            const chunk = chunksToSend[i];
            const isLastTelegramChunk = (i === chunksToSend.length - 1);
            
            // Format chunk message - use HTML for continuation header
            const chunkMessage = i === 0 
              ? chunk 
              : `<b>[Continued ${i + 1}/${chunksToSend.length}]</b>\n\n${chunk}`;
            
            let sent = false;
            let retries = 0;
            const maxRetries = 3;
            
            while (!sent && retries < maxRetries) {
              try {
                const parseMode = chunkMessage.includes('<b>') ? 'HTML' : 'Markdown';
                await bot.sendMessage(chatId, chunkMessage, { 
                  parse_mode: parseMode,
                  disable_web_page_preview: false
                });
                sent = true;
                console.log(`✅ Sent chunk ${i + 1}/${chunksToSend.length}`);
              } catch (error) {
                retries++;
                console.error(`❌ Error sending chunk ${i + 1}/${chunksToSend.length} (attempt ${retries}/${maxRetries}):`, error.message);
                
                if (retries < maxRetries) {
                  const waitTime = 500 * retries;
                  await new Promise(resolve => setTimeout(resolve, waitTime));
                }
              }
            }
            
            // Small delay between chunks (reduced since we're only sending 5 max)
            if (i < chunksToSend.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 300));
            }
          }
          
          // Always send the button after the chunks (for full transcript viewer)
          if (replyMarkup) {
            try {
              const buttonMessage = hasMoreChunks 
                ? `📝 <b>Preview complete</b> (showing ${chunksToSend.length} of ${totalChunks} sections)\n\n🎬 <b>View Full Transcript with Video:</b>`
                : `📝 <b>Transcript complete</b>\n\n🎬 <b>View Full Transcript with Video:</b>`;
              
              await bot.sendMessage(chatId, buttonMessage, {
                parse_mode: 'HTML',
                reply_markup: replyMarkup
              });
              console.log('✅ Sent full transcript viewer button');
            } catch (buttonError) {
              console.error('❌ Failed to send button:', buttonError.message);
              // Retry once
              try {
                await new Promise(resolve => setTimeout(resolve, 1000));
                await bot.sendMessage(chatId, '🎬 View Full Transcript:', {
                  reply_markup: replyMarkup
                });
                console.log('✅ Button sent on retry');
              } catch (retryError) {
                console.error('❌ Failed to send button on retry:', retryError.message);
              }
            }
          }
          
          console.log(`✅ Finished sending ${chunksToSend.length} chunks${hasMoreChunks ? ` (${totalChunks - chunksToSend.length} more available in full viewer)` : ''}`);
        } else {
          bot.deleteMessage(chatId, processingMsg.message_id);
          bot.sendMessage(chatId, '❌ Failed to scrape transcript. The video may not have a transcript available.');
        }
      } catch (error) {
        console.error('Error processing YouTube URL:', error);
        bot.deleteMessage(chatId, processingMsg.message_id);
        
        if (error.code === 'ECONNREFUSED') {
          bot.sendMessage(chatId, '❌ Cannot connect to the backend server. Please ensure the server is running on port 3001.');
        } else if (error.code === 'ETIMEDOUT') {
          bot.sendMessage(chatId, '❌ Request timed out. The video may be too long or the server is overloaded.');
    } else {
          bot.sendMessage(chatId, `❌ Error: ${error.message}`);
        }
      }
    }
  });
}

async function startBot() {
  // Close any existing bot instances first
  await closeExistingBotInstances();
  
  // Create new bot instance
  bot = new TelegramBot(TELEGRAM_BOT_TOKEN, { polling: true });
  
  // Set up all event handlers
  setupBotHandlers(bot);
  
  // Set up graceful shutdown handlers
  const shutdown = async (signal) => {
    console.log(`\n${signal} received. Shutting down gracefully...`);
    if (bot) {
      try {
        bot.stopPolling();
        console.log('Bot polling stopped.');
      } catch (err) {
        console.error('Error stopping bot:', err.message);
      }
    }
    process.exit(0);
  };
  
  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGHUP', () => shutdown('SIGHUP'));
  
  return bot;
}

// Start the bot
startBot().then(() => {
  console.log('🤖 Telegram bot initialized and polling enabled');
  console.log(`📡 Backend API URL: ${API_URL}`);
  console.log('✅ Bot is ready and listening for messages');
}).catch((error) => {
  console.error('Failed to start bot:', error);
  process.exit(1);
});

// Helper function to split long messages (Telegram limit is 4096 characters)
function splitMessage(text, maxLength = 4096) {
  if (text.length <= maxLength) {
    return [text];
  }
  
  const chunks = [];
  let currentChunk = '';
  
  // Try to split by sentences first
  const sentences = text.split(/(?<=[.!?])\s+/);
  
  for (const sentence of sentences) {
    if ((currentChunk + sentence).length <= maxLength) {
      currentChunk += sentence + ' ';
    } else {
      if (currentChunk) {
        chunks.push(currentChunk.trim());
      }
      // If a single sentence is too long, split by words
      if (sentence.length > maxLength) {
        const words = sentence.split(' ');
        let wordChunk = '';
        for (const word of words) {
          if ((wordChunk + word).length <= maxLength) {
            wordChunk += word + ' ';
          } else {
            if (wordChunk) {
              chunks.push(wordChunk.trim());
            }
            wordChunk = word + ' ';
          }
        }
        currentChunk = wordChunk;
      } else {
        currentChunk = sentence + ' ';
      }
    }
  }
  
  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }
  
  return chunks;
}

// Helper function to extract YouTube URL from text
function extractYouTubeUrl(text) {
  const urlRegex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = text.match(urlRegex);
  return match ? match[0] : null;
}

// Helper function to extract only text from transcript (no timestamps)
function extractTextOnly(transcriptData) {
  if (!transcriptData || !Array.isArray(transcriptData)) {
    return 'No transcript data available';
  }
  
  // Extract only the text, ignoring timestamps
  const textOnly = transcriptData
    .map(segment => {
      if (typeof segment === 'string') {
        return segment;
      } else if (segment.text) {
        return segment.text; // Only text, no timestamp
      } else if (Array.isArray(segment)) {
        return segment.join(' ');
      }
      return String(segment);
    })
    .join(' ')
    .trim();
  
  return textOnly;
}

// Helper function to extract video ID from URL
function extractVideoId(url) {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}

// All bot event handlers are now set up in setupBotHandlers() function
