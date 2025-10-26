# XscrapeExpressX Backend

Express.js backend server for YouTube transcript scraping with Puppeteer automation and Telegram bot integration.

## 🚀 Features

- **YouTube Transcript Scraping**: Automated extraction using Puppeteer
- **Stealth Browser Automation**: Bypasses YouTube's anti-bot detection
- **RESTful API**: Clean API endpoints for frontend integration
- **Telegram Bot**: Bot interface for transcript requests
- **File Storage**: Local storage for transcript files
- **Error Handling**: Comprehensive error management
- **Rate Limiting**: Protection against abuse

## 🏗️ Architecture

### Core Components
- **Express.js Server**: Main HTTP server
- **Puppeteer**: Browser automation for scraping
- **Stealth Plugin**: Anti-detection measures
- **File System**: Local transcript storage
- **Telegram Bot**: Bot interface

### Entry Points
- `app.mjs`: Main Express server with scraping functionality
- `server.mjs`: Alternative server configuration
- `telehug-bot`: Telegram bot integration

## 🛠️ Installation

### Prerequisites
- Node.js (v16 or higher)
- Chromium browser
- Telegram Bot Token (for bot functionality)

### Setup
```bash
cd backend
npm install
```

### Environment Variables
Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
CHROMIUM_PATH=/usr/bin/chromium-browser
PORT=3001
```

## 📡 API Endpoints

### POST /api/scrape
Scrape YouTube video transcript

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "success": true,
  "transcriptData": [
    {
      "timestamp": "0:00",
      "text": "Transcript text segment..."
    }
  ],
  "videoInfo": {
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "thumbnail": "thumbnail_url"
  }
}
```

### GET /api/transcripts
List all saved transcripts

**Response:**
```json
{
  "transcripts": [
    {
      "id": "transcript_id",
      "title": "Video Title",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

### GET /api/transcripts/:id
Get specific transcript by ID

**Response:**
```json
{
  "transcriptData": [...],
  "videoInfo": {...}
}
```

## 🧩 Core Functions

### Scraping Functions

#### `scrape(url)`
Main scraping orchestration function.

**Parameters:**
- `url`: YouTube video URL

**Returns:**
- Object containing transcript data and video info
- `null` if scraping fails

#### `clickMoreButton(page)`
Navigate to transcript options by clicking the "More" button.

**Parameters:**
- `page`: Puppeteer page object

**Returns:**
- `boolean`: Success status

#### `clickShowTranscriptButton(page)`
Access the transcript panel by clicking "Show transcript".

**Parameters:**
- `page`: Puppeteer page object

**Returns:**
- `boolean`: Success status

#### `getTranscriptText(page)`
Extract transcript content from the page.

**Parameters:**
- `page`: Puppeteer page object

**Returns:**
- Array of transcript segments with timestamps

#### `getVideoInfo(page)`
Extract video metadata (title, thumbnail, URL).

**Parameters:**
- `page`: Puppeteer page object

**Returns:**
- Object containing video information

### Utility Functions

#### `wait(ms)`
Promise-based timeout function.

#### `saveData(data, filename)`
Save transcript data to file system.

#### `scrollPageToFindElement(page, selector)`
Scroll page to locate elements.

## 🤖 Telegram Bot

### Bot Commands
- `/start` - Initialize bot and show welcome message
- `/help` - Display available commands and usage
- Send YouTube URL - Automatically scrape and send transcript

### Bot Features
- Direct transcript delivery in chat
- File download support
- Error handling with user-friendly messages
- Rate limiting for spam protection

### Bot Configuration
```javascript
const bot = new TelegramBot(token, { polling: true });
```

## 🔧 Configuration

### Puppeteer Configuration
```javascript
const browser = await puppeteer.launch({
  headless: true,
  args: ['--incognito', '--no-sandbox', '--disable-setuid-sandbox'],
  executablePath: CONFIG.executablePath
});
```

### Wait Times Configuration
```javascript
const CONFIG = {
  waitTimes: {
    pageLoad: 3000,        // Page load wait time
    afterClick: 3500,      // Wait after clicking elements
    transcriptLoad: 3000   // Wait for transcript to load
  }
};
```

## 🚨 Error Handling

### Common Errors
1. **Chromium Not Found**
   - Ensure Chromium is installed
   - Check `CHROMIUM_PATH` environment variable

2. **Transcript Not Available**
   - Video may not have transcript
   - Video might be age-restricted
   - YouTube layout changes

3. **Network Timeouts**
   - Check internet connection
   - Increase wait times in configuration

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## 🔒 Security

### Input Validation
- YouTube URL format validation
- XSS protection
- Rate limiting on API endpoints

### Environment Security
- Secure environment variable management
- No sensitive data in logs
- Proper error message sanitization

## 📊 Monitoring

### Logging
- Request/response logging
- Error logging with stack traces
- Performance metrics

### Health Checks
- Server health endpoint
- Database connectivity checks
- External service status

## 🚀 Deployment

### Production Setup
1. Set environment variables
2. Install dependencies
3. Configure reverse proxy (nginx)
4. Set up process manager (PM2)

### PM2 Configuration
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'xscrapex-backend',
    script: 'app.mjs',
    instances: 'max',
    exec_mode: 'cluster'
  }]
};
```

## 📝 Development

### Adding New Features
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

### Code Style
- Use ES6+ features
- Follow Express.js best practices
- Add JSDoc comments
- Maintain error handling

## 📄 License

This project is licensed under the ISC License. 