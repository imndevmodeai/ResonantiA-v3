import PropTypes from 'prop-types'

function URLInput({ onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    const url = e.target.url.value
    if (url) onSubmit(url)
  }

  return (
    <form onSubmit={handleSubmit} className="url-form">
      <input
        type="text"
        name="url"
        placeholder="Enter YouTube URL"
        disabled={loading}
        className="url-input"
      />
      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Loading...' : 'Get Transcript'}
      </button>
    </form>
  )
}

URLInput.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired
}

export default URLInput 