import re
import yt_dlp
from typing import Dict, Any, Optional
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
    
def get_captions(youtube_url: str) -> str:
    """
    Fetches the Chinese CC from a YouTube video.

    Args:
        youtube_url (str): The YouTube video URL.

    Returns:
        str: The Chinese lyrics.
    """
    video_id = extract_video_id(youtube_url)
    data = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hans', 'zh-Hant', 'zh', 'zh-CN', 'zh-TW'])

    full_lyrics = []
    for entry in data:
        full_lyrics.append(entry['text'])

    return "\n".join(full_lyrics)

    
def get_description(video_url: str) -> str:
    """
    Uses yt-dlp to grab the video title, channel name (uploader), and description 
    all in a single network request.
    """

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            return { 
                "title": info_dict.get('title', ""),
                "artist": info_dict.get('uploader', ""),
                "description": info_dict.get('description',"")
            }
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")
            return {"title": "", "artist": "", "description": ""}

def get_chinese_lyrics(video_url: str) -> str:
    """
    Fetches the Chinese lyrics from a YouTube video, either from the CC or the description.

    Args:
        video_url (str): The YouTube video URL.
    """
    video_id = extract_video_id(video_url)

    output_data = {
        "transcript": None,
        "description": None,
        "title": "",
        "artist": ""
    }

    meta = get_description(video_url)
    output_data["title"] = meta.get("title", "")
    output_data["artist"] = meta.get("artist", "")
    
    try:
        # Fetch the transcript (CC)
        print("Fetching Chinese captions...")
        transcript = get_captions(video_url)
        output_data["transcript"] = transcript
        print("Chinese captions fetched successfully.")

    except Exception:
        print("No Chinese captions found. Attempting to fetch from description...")
        # description_text = get_description(video_url)
        output_data["description"] = meta.get("description", "")
        print("Fetched description successfully.")
        
    return output_data


if __name__ == "__main__":
    youtube_url = input("Enter YouTube URL: ")
    lyrics = get_chinese_lyrics(youtube_url)
    print(lyrics)
