# XscrapeExpressX - YouTube Transcript Scraper

A full-stack web application for extracting and viewing YouTube video transcripts with a modern React frontend and Express.js backend. This application uses Puppeteer with stealth capabilities to bypass YouTube's anti-bot measures and extract transcripts from videos.

## 🚀 Features

- **YouTube Transcript Extraction**: Automated scraping using Puppeteer with stealth plugin
- **React Frontend**: Modern UI for URL input and transcript viewing
- **Timestamp Navigation**: Clickable timestamps that link to specific video moments
- **Download Functionality**: Export transcripts as text files
- **Telegram Bot Integration**: Bot interface for transcript requests
- **Stealth Browser Automation**: Bypasses YouTube's anti-bot detection
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

- **Frontend**: React + Vite with modern component architecture
- **Backend**: Express.js with Puppeteer for web scraping
- **Browser Automation**: Puppeteer with Stealth Plugin
- **Styling**: CSS with responsive design principles
- **Data Storage**: Local file system for transcript storage

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager
- Chromium browser (for Puppeteer)
- Telegram Bot Token (optional, for bot functionality)

## 🛠️ Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd youscrape
```

### 2. Install Dependencies
```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
npm install
cd ..
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
CHROMIUM_PATH=/usr/bin/chromium-browser
PORT=3001
```

### 4. Start the Application
```bash
# Start backend server
npm run dev

# In another terminal, start frontend
cd frontend
npm run dev
```

### 5. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:3001

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for bot functionality | Required |
| `CHROMIUM_PATH` | Path to Chromium executable | `/usr/bin/chromium-browser` |
| `PORT` | Backend server port | `3001` |

### Browser Configuration
The application uses Puppeteer with the following configuration:
- Headless mode enabled
- Stealth plugin for anti-detection
- Incognito mode for clean sessions
- Custom executable path support

## 📡 API Reference

### POST /api/scrape
Scrape YouTube video transcript

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "transcriptData": [
    {
      "timestamp": "0:00",
      "text": "Transcript text segment..."
    }
  ],
  "videoInfo": {
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "thumbnail": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg"
  }
}
```

### GET /api/transcripts
List all saved transcripts

### GET /api/transcripts/:id
Get specific transcript by ID

## 🗂️ Project Structure

```
youscrape/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── URLInput.jsx
│   │   │   └── TranscriptViewer.jsx
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # App entry point
│   ├── package.json
│   └── README.md
├── backend/                  # Express.js server
│   ├── app.mjs              # Main server file
│   ├── server.mjs           # Alternative server
│   ├── telehug-bot          # Telegram bot
│   └── package.json
├── transcripts/              # Saved transcript files
├── app.hug.mjs              # Main application entry
├── package.json             # Root dependencies
└── README.md                # This file
```

## 🧩 Components

### Frontend Components

#### URLInput
- Form component for submitting YouTube URLs
- Loading state management
- Input validation

#### TranscriptViewer
- Displays transcript with timestamps
- Download functionality
- Video information display
- Timestamp navigation links

### Backend Functions

#### Core Scraping Functions
- `scrape(url)`: Main scraping orchestration
- `clickMoreButton(page)`: Navigate to transcript options
- `clickShowTranscriptButton(page)`: Access transcript panel
- `getTranscriptText(page)`: Extract transcript content
- `getVideoInfo(page)`: Get video metadata

## 🤖 Telegram Bot

The application includes a Telegram bot for transcript requests:

### Bot Commands
- `/start` - Initialize bot
- `/help` - Show available commands
- Send YouTube URL - Automatically scrape transcript

### Bot Features
- Direct transcript delivery
- File download support
- Error handling and user feedback

## 🚨 Troubleshooting

### Common Issues

1. **Chromium Not Found**
   ```bash
   # Install Chromium
   sudo apt install chromium-browser
   # Or update CHROMIUM_PATH in .env
   ```

2. **Puppeteer Launch Failures**
   - Ensure Chromium is installed
   - Check executable path in configuration
   - Verify system permissions

3. **Transcript Not Found**
   - Verify video has available transcript
   - Check YouTube URL format
   - Ensure video is not age-restricted

### Debug Mode
Enable debug logging by setting environment variable:
```bash
DEBUG=true npm run dev
```

## 🔒 Security Considerations

- Input validation for YouTube URLs
- Rate limiting for API endpoints
- Error handling for failed requests
- Secure environment variable management

## 📝 Development

### Adding New Features
1. Create feature branch
2. Implement changes
3. Update documentation
4. Test thoroughly
5. Submit pull request

### Code Style
- Use consistent formatting
- Add comments for complex logic
- Follow React best practices
- Maintain component separation

## 📄 License

This project is licensed under the ISC License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting section
- Review API documentation

---

**Built with ❤️ using React, Express.js, and Puppeteer**
