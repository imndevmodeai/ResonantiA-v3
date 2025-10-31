# XscrapeExpressX Frontend

React-based frontend for the YouTube transcript scraper application. Built with Vite for fast development and optimized builds.

## 🚀 Features

- **Modern React Architecture**: Built with React 18 and modern hooks
- **Fast Development**: Vite for instant hot module replacement
- **Component-Based Design**: Modular, reusable components
- **Responsive UI**: Works seamlessly on all device sizes
- **Type Safety**: PropTypes for component validation

## 🧩 Components

### URLInput
Form component for submitting YouTube URLs with loading state management.

**Props:**
- `onSubmit`: Function called with URL when form is submitted
- `loading`: Boolean to show loading state

**Usage:**
```jsx
<URLInput onSubmit={handleUrlSubmit} loading={isLoading} />
```

### TranscriptViewer
Displays transcript data with timestamps and download functionality.

**Props:**
- `transcriptData`: Array of transcript segments with timestamp and text
- `videoInfo`: Object containing video title, URL, and thumbnail

**Usage:**
```jsx
<TranscriptViewer 
  transcriptData={transcript} 
  videoInfo={videoInfo} 
/>
```

## 🛠️ Development

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```
Access the application at http://localhost:5173

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── URLInput.jsx     # URL input form
│   │   └── TranscriptViewer.jsx # Transcript display
│   ├── App.jsx              # Main application component
│   ├── App.css              # Application styles
│   ├── index.css            # Global styles
│   └── main.jsx             # Application entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── vite.config.js           # Vite configuration
└── eslint.config.js         # ESLint configuration
```

## 🎨 Styling

The application uses CSS for styling with:
- Responsive design principles
- Modern CSS features
- Component-scoped styles
- Clean, accessible design

## 🔧 Configuration

### Vite Configuration
The project uses Vite with React plugin for optimal development experience.

### ESLint Configuration
ESLint is configured for code quality and consistency.

## 📡 API Integration

The frontend communicates with the backend API for:
- Submitting YouTube URLs for scraping
- Receiving transcript data
- Error handling and user feedback

## 🚀 Deployment

### Build Process
1. Run `npm run build`
2. Deploy the `dist` folder to your hosting service

### Environment Variables
- `VITE_API_URL`: Backend API URL (defaults to localhost:3001)

## 🤝 Contributing

1. Follow React best practices
2. Use PropTypes for component validation
3. Maintain component separation
4. Add comments for complex logic
5. Test components thoroughly

## 📄 License

This project is licensed under the ISC License.
