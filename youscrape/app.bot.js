// bot.js
const TelegramBot = require('node-telegram-bot-api');
const scrape = require('./scrape');

const bot = new TelegramBot('YOUR_API_TOKEN', { polling: true });

bot.onText(/\/scrape (.+)/, (msg, match) => {
  const url = match[1];
  scrape(url).then((result) => {
    if (result.success) {
      const transcriptData = result.transcriptData;
      bot.sendMessage(msg.chat.id, transcriptData.join('\n'));
    } else {
      bot.sendMessage(msg.chat.id, 'Error scraping transcript');
    }
  });
});
