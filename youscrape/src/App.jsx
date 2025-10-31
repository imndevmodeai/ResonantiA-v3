import { useState } from 'react'
import TranscriptViewer from './components/TranscriptViewer'
import URLInput from './components/URLInput'
import './App.css'

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [transcriptData, setTranscriptData] = useState(null)
  const [videoInfo, setVideoInfo] = useState(null)

  const handleURLSubmit = async (url) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:3000/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      })
      const data = await response.json()
      if (data.success) {
        setTranscriptData(data.transcriptData)
        setVideoInfo(data.videoInfo)
      } else {
        setError('Failed to get transcript')
      }
    } catch (err) {
      setError('Error connecting to server')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>YouTube Transcript Scraper</h1>
      <URLInput onSubmit={handleURLSubmit} loading={loading} />
      {error && <div className="error">{error}</div>}
      {transcriptData && videoInfo && (
        <TranscriptViewer 
          transcriptData={transcriptData} 
          videoInfo={videoInfo} 
        />
      )}
    </div>
  )
}

export default App 