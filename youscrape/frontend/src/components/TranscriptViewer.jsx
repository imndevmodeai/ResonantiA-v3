import PropTypes from 'prop-types'

function TranscriptViewer({ transcriptData, videoInfo }) {
  const downloadTranscript = () => {
    const text = transcriptData.map(segment => segment.text).join(' ')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${videoInfo.title}_transcript.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="transcript-container">
      <div className="header">
        <a href={videoInfo.url} target="_blank" rel="noopener noreferrer">
          <h2>{videoInfo.title}</h2>
          <img src={videoInfo.thumbnail} alt={videoInfo.title} className="thumbnail" />
        </a>
      </div>

      <div className="timestamps">
        <h3>Timestamps</h3>
        <div className="timestamp-grid">
          {transcriptData.map((segment, index) => (
            <a
              key={index}
              href={`${videoInfo.url}&t=${segment.timestamp}`}
              target="_blank"
              rel="noopener noreferrer"
              className="timestamp-link"
            >
              {segment.timestamp}
            </a>
          ))}
        </div>
      </div>

      <div className="transcript-text">
        <h3>Transcript</h3>
        <button onClick={downloadTranscript} className="download-button">
          Download Transcript
        </button>
        <p>{transcriptData.map(segment => segment.text).join(' ')}</p>
      </div>
    </div>
  )
}

TranscriptViewer.propTypes = {
  transcriptData: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired
    })
  ).isRequired,
  videoInfo: PropTypes.shape({
    title: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
    thumbnail: PropTypes.string.isRequired
  }).isRequired
}

export default TranscriptViewer 