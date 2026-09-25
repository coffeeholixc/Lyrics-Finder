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
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'; // Use the environment variable or fallback to localhost
      const response = await fetch(`${API_BASE_URL}/extract-lyrics`, {
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

// 3. User Interface
  return (
    <div className="mx-auto">
{/* Header Web App Name */}
      <header  className = "text-center">
        <h1 className = "text-5xl font-bold mt-30 mb-30">Han/Pin/Eng Lyric</h1>
      </header>

{/* Input Form */}
      <div className="w-full md:w-3/4 lg:w-1/2 mx-auto mb-24">
        <form onSubmit={handleFetchLyrics} className="relative group">
          {/* Search Bar */}
          <input
            type = "text"
            placeholder = "Enter Youtube URL"
            value={url}
            onChange={(e) => setURL(e.target.value)}
            required
            className="w-full px-5 py-3.5 pr-12 text-sm text-gray-900 placeholder:text-gray-400 bg-white border border-gray-200 rounded-full shadow-sm focus:ring-2 focus:ring-gray-200 focus:border-gray-300 transition-all focus:outline-none"
            />
          {/* Search Button */}
          <button
            type="submit"
            disabled={loading}
            className="absolute right-4 top-1/2 -translate-y-1/2 "
          >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                strokeWidth={2} 
                stroke="currentColor" 
                className="w-5 h-5"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
            {/* {loading ? 'Processing...' : 'Search Lyrics'}  */}
            {/* If loading is true, show "Processing...", otherwise show "Search Lyrics" */}
          </button>
        </form>
{/* Error Message */}
        {error && <p className="text-red-500 text-center">Error: {error}</p>}
      </div>

{/* Video Placeholder */}
    {/* <div>
        <div className="bg-gray-100 border-2 border-dashed border-gray-200 rounded-2xl flex items-center justify-center shadow-inner w-1/2 mx-auto mt-4 mb-4 h-48">
          <div className="text-center text-gray-400">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 10 10" 
              strokeWidth={1} 
              stroke="currentColor" 
              className="w-16 h-16 mx-auto mb-4"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25v13.5m-7.5-13.5v13.5" />
            </svg>
            <p className="font-medium text-lg">YouTube Video Placeholder</p>
            <p className="text-sm mt-1">Video embeds here</p>
          </div>
        </div>
    </div> */}


{/* Lyrics Display */}
{/* The 3 Lyric Blocks will ONLY show once lyrics data exists */}
{Lyrics && (
  <div className="max-w-6xl mx-auto bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
    
    {/* 1. Header Row */}
    <div className="grid grid-cols-3 bg-gray-50/80 border-b border-gray-100 p-4 font-bold text-xs text-gray-400 uppercase tracking-widest text-center md:text-left">
      <div>Hanzi (漢字)</div>
      <div>Pinyin (拼音)</div>
      <div>English (英文)</div>
    </div>

    {/* 2. Lyric Rows Container */}
    <div className="divide-y divide-gray-100 max-h-[500px] overflow-y-auto">
      {Lyrics.lyrics?.map((line, index) => (
        <div 
          key={index} 
          className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 items-center hover:bg-indigo-50/30 transition-colors"
        >
          {/* Column 1: Hanzi */}
          <div className="text-gray-950 font-medium text-base md:text-lg leading-snug">
            {line.hanzi}
          </div>

          {/* Column 2: Pinyin */}
          <div className="text-indigo-600 font-medium text-sm md:text-base leading-snug">
            {line.pinyin}
          </div>

          {/* Column 3: English */}
          <div className="text-gray-600 italic text-sm leading-snug">
            {line.english}
          </div>
        </div>
      ))}
    </div>

  </div>
)}
    </div>
  );
}