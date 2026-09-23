import { useState } from 'react';

export default function App() {
  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleExtract = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setData(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/extract-lyrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: url }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to extract lyrics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>Chinese Lyrics Extractor</h2>
      
      <form onSubmit={handleExtract}>
        <input
          type="url"
          placeholder="Paste YouTube URL..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          style={{ width: '70%', padding: '8px', marginRight: '8px' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Processing...' : 'Extract'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {data && (
        <div style={{ marginTop: '24px' }}>
          <h3>Lyrics Result</h3>
          {data.lyrics?.map((line, index) => (
            <div key={index} style={{ marginBottom: '12px' }}>
              <p style={{ margin: 0, fontWeight: 'bold' }}>{line.hanzi}</p>
              <p style={{ margin: 0, color: '#555' }}>{line.pinyin}</p>
              <p style={{ margin: 0, color: '#888', italic: 'true' }}>{line.english}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}