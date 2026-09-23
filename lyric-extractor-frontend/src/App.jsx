import {useState} from 'react';

export default function App() {
// 1. State Management
  const [url, setURL] = useState('');
  const [Lyrics, setLyrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

// 2. Fetch Lyrics Function
  const handleFetchLyrics = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLyrics(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/extract-lyrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({video_url: url}),
      });

      if(!response.ok){
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setLyrics(data);

    } catch (err) {
      setError(err.message || 'An error occurred while fetching lyrics.');
    } finally {
    setLoading(false);
  }
};

// 2. User Interface
  return (
    <div>
      <h2>EnHanPin Lyrics</h2>

      {/* Input Form */}
      <form onSubmit={handleFetchLyrics}>
        <input
          type = "text"
          placeholder = "Enter Youtube URL"
          value={url}
          onChange={(e) => setURL(e.target.value)}
          required
          style={{ width: '70%', padding: '8px', marginRight: '8px'}}
          />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Get Lyrics'}
        </button>
      </form>

      {/* Error Message */}
      {error && <p style={{color: 'red'}}>Error: {error}</p>}

      {/* Lyrics Display */}
      {Lyrics && (
      <div style={{ marginTop: '20px'}}>
        <h3>{Lyrics.title || 'Lyrics Output'}</h3>
        {Lyrics.lyrics?.map((line, index) => (

         <div key={index} style={{ marginBottom: '12px'}}>
          <p style={{ fontWeight: 'bold', margin: '0'}}>{line.english}</p>
          <p style={{ fontWeight: 'bold', margin: '0'}}>{line.hanzi}</p>
          <p style={{ fontWeight: 'bold', margin: '0'}}>{line.pinyin}</p>
        </div>

        ))}
      </div>
      )}
    </div>
  );
}