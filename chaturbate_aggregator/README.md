# Chaturbate Content Aggregator

A Flask application that aggregates live streams and past performances from Chaturbate and cloudbate.com.

## Features

- ✅ Extract Chaturbate usernames from URLs or plain text
- ✅ Check if users are currently live on Chaturbate
- ✅ Scrape past performances from cloudbate.com
- ✅ Auto-playing preview videos on page load (like cloudbate.com hover effect)
- ✅ Support for multiple usernames
- ✅ Responsive design

## Installation

1. Install dependencies:
```bash
cd chaturbate_aggregator
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export PORT=5000
export HOST=0.0.0.0
export DEBUG=True
export SECRET_KEY=your_secret_key_here
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter Chaturbate username(s) or URL(s) and click "View Content"

## API Endpoints

- `GET /` - Main landing page
- `GET /user/<username>` - User landing page with live status and performances
- `POST /process` - Process input and redirect to user page
- `POST /api/extract` - Extract usernames from input (JSON API)
- `GET /api/user/<username>` - Get user data (JSON API)

## Supported Input Formats

- Plain username: `alicelighthouse`
- Full URL: `https://chaturbate.com/alicelighthouse/`
- Partial URL: `chaturbate.com/alicelighthouse`
- Multiple usernames: `user1, user2, user3` or one per line

## Features

### Auto-Playing Preview Videos

The landing page automatically plays preview videos on load, mimicking the hover effect from cloudbate.com. Videos:
- Auto-play when page loads
- Play when scrolled into viewport
- Pause when scrolled out of viewport
- Can be clicked to play/pause manually

### Remote Access

The server listens on `0.0.0.0` by default, making it accessible from other devices on your network. To access remotely:
- Use your machine's IP address: `http://YOUR_IP:5000`
- Or configure port forwarding/ngrok for external access

## Notes

- The app uses web scraping, which may be subject to rate limiting
- Some videos may require user interaction to play (browser autoplay policies)
- Cloudbate.com scraping depends on their HTML structure remaining consistent

