import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The video ID.
    """
    pattern = r'(?:v=|\/v\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})'
    video_id = re.search(pattern, url)
    if video_id:
        return video_id.group(1)
    else:
        raise ValueError("Invalid YouTube URL")
    
def get_chinese_lyrics(youtube_url: str) -> str:
    """
    Fetches the Chinese lyrics from a YouTube video.

    Args:
        youtube_url (str): The YouTube video URL.

    Returns:
        str: The Chinese lyrics.
    """
    try:
        api = YouTubeTranscriptApi()
        video_id = extract_video_id(youtube_url)
        data = api.fetch(video_id, languages=['zh-Hans', 'zh-Hant', 'zh', 'zh-CN', 'zh-TW'])

        full_lyrics = []
        for entry in data:
            full_lyrics.append(entry.__dict__['text'])

        return "\n".join(full_lyrics)
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"

if __name__ == "__main__":
    youtube_url = input("Enter YouTube URL: ")
    lyrics = get_chinese_lyrics(youtube_url)
    print(lyrics)
