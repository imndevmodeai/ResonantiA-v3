# Telegram Thread Saver Bot - Setup Instructions

## Prerequisites

1. **Node.js** (v14 or higher)
   - Check version: `node --version`
   - Install from: https://nodejs.org/

2. **Chrome/Chromium Browser**
   - **Linux**: `sudo apt-get install chromium-browser` or `sudo apt-get install google-chrome-stable`
   - **macOS**: Download from https://www.google.com/chrome/
   - **Windows**: Download from https://www.google.com/chrome/

3. **Telegram Bot Token**
   - Create a bot via @BotFather on Telegram
   - Save your token securely

## Installation Steps

### 1. Install Dependencies

```bash
cd telThreadSaver
npm install
```

### 2. Install Chrome for Puppeteer (Alternative Method)

If Chrome is not found automatically, install via Puppeteer:

```bash
npx puppeteer browsers install chrome
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add your Telegram bot token:

```
TELEGRAM_BOT_TOKEN=your_actual_token_here
```

**CRITICAL**: Never commit the `.env` file to version control!

### 4. Verify Chrome Installation

The script will automatically search for Chrome in common locations. If Chrome is installed in a non-standard location, you may need to modify the `findChromeExecutable()` function in `app.js`.

Common Chrome paths:
- **Linux**: `/usr/bin/google-chrome` or `/usr/bin/chromium-browser`
- **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`

### 5. Run the Bot

```bash
node app.js
```

Or use npm:

```bash
npm start
```

## Usage

1. Start the bot (see step 5 above)
2. Open Telegram and find your bot
3. Send a Hugging Face chat URL (e.g., `https://hf.co/chat/r/ZTqJv4Y`)
4. The bot will scrape the content and send it back as a text file

## Troubleshooting

### Error: "Chrome not found"

**Solution 1**: Install Chrome system-wide (recommended)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install google-chrome-stable

# Or Chromium
sudo apt-get install chromium-browser
```

**Solution 2**: Use Puppeteer's Chrome installer
```bash
npx puppeteer browsers install chrome
```

**Solution 3**: Manually specify Chrome path in `app.js`
Edit the `findChromeExecutable()` function to include your Chrome path.

### Error: "TELEGRAM_BOT_TOKEN not found"

**Solution**: Create `.env` file with your token:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

### Error: "No text content found"

**Solution**: The page structure may have changed. Check:
1. URL is accessible
2. Page loads completely (wait time may need adjustment)
3. Content selectors in `scrapeTextFile()` may need updating

### Error: "File was created but cannot be found"

**Solution**: Check file permissions on the `saves/` directory:
```bash
chmod 755 saves/
```

## File Structure

```
telThreadSaver/
├── app.js              # Main bot script
├── package.json        # Node.js dependencies
├── .env               # Environment variables (DO NOT COMMIT)
├── saves/             # Directory for saved files (auto-created)
└── README.md          # This file
```

## Security Notes

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Keep bot token secret** - Don't share in public channels
3. **Review scraped content** - Ensure compliance with Hugging Face ToS
4. **Rate limiting** - Be respectful of target servers

## Advanced Configuration

### Change Headless Mode

In `app.js`, modify the `puppeteer.launch()` call:
```javascript
headless: false,  // Set to false to see browser window (for debugging)
```

### Adjust Timeout

Modify timeout values:
```javascript
timeout: 60000,  // Increase to 60 seconds if needed
```

### Custom Content Selectors

Modify the `contentSelectors` array in `scrapeTextFile()` to target specific page elements.

## Support

For issues or questions:
1. Check console logs for detailed error messages
2. Verify all prerequisites are installed
3. Test Chrome installation: `google-chrome --version`
4. Test Node.js: `node --version`
