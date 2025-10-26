# XscrapeExpressX API Documentation

Comprehensive API reference for the YouTube transcript scraper backend service.

## 🚀 Base URL

```
http://localhost:3001
```

## 📡 Authentication

Currently, the API does not require authentication. However, rate limiting is implemented to prevent abuse.

## 📋 Endpoints

### POST /api/scrape

Scrape transcript from a YouTube video.

**Request:**
```http
POST /api/scrape
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | YouTube video URL |

**Response (Success):**
```json
{
  "success": true,
  "transcriptData": [
    {
      "timestamp": "0:00",
      "text": "Hello, welcome to this video tutorial."
    },
    {
      "timestamp": "0:05",
      "text": "Today we'll be learning about web development."
    }
  ],
  "videoInfo": {
    "title": "Web Development Tutorial for Beginners",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "thumbnail": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Transcript not available for this video",
  "code": "TRANSCRIPT_NOT_FOUND"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid URL)
- `404` - Transcript not found
- `500` - Internal Server Error

### GET /api/transcripts

List all saved transcripts.

**Request:**
```http
GET /api/transcripts
```

**Response:**
```json
{
  "success": true,
  "transcripts": [
    {
      "id": "transcript_123",
      "title": "Web Development Tutorial",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "videoUrl": "https://www.youtube.com/watch?v=VIDEO_ID"
    },
    {
      "id": "transcript_456",
      "title": "React Tutorial for Beginners",
      "createdAt": "2024-01-02T00:00:00.000Z",
      "videoUrl": "https://www.youtube.com/watch?v=ANOTHER_ID"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `500` - Internal Server Error

### GET /api/transcripts/:id

Get specific transcript by ID.

**Request:**
```http
GET /api/transcripts/transcript_123
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Transcript ID |

**Response (Success):**
```json
{
  "success": true,
  "transcriptData": [
    {
      "timestamp": "0:00",
      "text": "Hello, welcome to this video tutorial."
    }
  ],
  "videoInfo": {
    "title": "Web Development Tutorial for Beginners",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "thumbnail": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Transcript not found",
  "code": "TRANSCRIPT_NOT_FOUND"
}
```

**Status Codes:**
- `200` - Success
- `404` - Transcript not found
- `500` - Internal Server Error

### GET /api/health

Health check endpoint.

**Request:**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 3600
}
```

**Status Codes:**
- `200` - Service healthy
- `503` - Service unhealthy

## 🔧 Error Codes

| Code | Description |
|------|-------------|
| `INVALID_URL` | YouTube URL format is invalid |
| `TRANSCRIPT_NOT_FOUND` | No transcript available for video |
| `VIDEO_NOT_FOUND` | YouTube video does not exist |
| `AGE_RESTRICTED` | Video is age-restricted |
| `NETWORK_ERROR` | Network connection failed |
| `BROWSER_ERROR` | Browser automation failed |
| `RATE_LIMITED` | Too many requests |

## 📊 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Limit**: 10 requests per minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time

**Rate Limit Exceeded Response:**
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMITED",
  "retryAfter": 60
}
```

## 🔒 Security

### Input Validation
- YouTube URL format validation
- XSS protection
- Request size limits

### Headers
- `Content-Type: application/json` required for POST requests
- CORS headers for cross-origin requests

## 📝 Examples

### JavaScript (Fetch)
```javascript
// Scrape transcript
const response = await fetch('/api/scrape', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://www.youtube.com/watch?v=VIDEO_ID'
  })
});

const data = await response.json();
console.log(data);
```

### cURL
```bash
# Scrape transcript
curl -X POST http://localhost:3001/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# Get transcripts list
curl http://localhost:3001/api/transcripts

# Get specific transcript
curl http://localhost:3001/api/transcripts/transcript_123
```

### Python (requests)
```python
import requests

# Scrape transcript
response = requests.post('http://localhost:3001/api/scrape', 
  json={'url': 'https://www.youtube.com/watch?v=VIDEO_ID'})
data = response.json()
print(data)
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure proper CORS headers
   - Check origin configuration

2. **Network Timeouts**
   - Increase timeout settings
   - Check network connectivity

3. **Browser Automation Failures**
   - Verify Chromium installation
   - Check executable path configuration

### Debug Mode
Enable debug logging by setting environment variable:
```bash
DEBUG=true npm run dev
```

## 📄 License

This API documentation is part of the XscrapeExpressX project, licensed under the ISC License. 