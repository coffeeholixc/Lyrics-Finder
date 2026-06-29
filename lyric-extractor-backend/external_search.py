# Entirely made by Gemini. I struggled with finding my own solutions. At first, I tried KKBOX and DuckDuckGo but I was hit with either Error 202 (Bot Block) or 403 (Copyright Lockdown)
# So I had Gemini helped and it introduced me to NetEase Music. I was able to find the song ID and lyrics using their API.

import requests
import re
from typing import Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/"
}

def search_netease_for_song_id(song_title: str, song_artist: str) -> Optional[int]:
    """
    Searches NetEase Music for a song by title and artist, and returns the song ID if found.

    Args:
        song_title (str): The title of the song.
        song_artist (str): The artist of the song.

    Returns:
        Optional[int]: The song ID if found, otherwise None.
    """
    search_url = "https://music.163.com/api/search/get"
    combined_query = f"{song_title} {song_artist}".strip()

    params = {
        "s":combined_query,
        "type": 1,  # Search for songs
        "limit": 10  # Limit the number of results
    }

    try:
        print(f"Searching NetEase Music for: {combined_query}")
        response = requests.get(search_url, headers=HEADERS, params=params)
        data = response.json()

        songs = data.get("result", {}).get("songs", [])
        if songs:
            # Return the first song's ID
            return songs[0].get("id")
            print(f"Found song ID: {songs[0].get('id')} for '{combined_query}'")
        else:
            print(f"No songs found for '{combined_query}'")
            return None

    except Exception as e:
        print(f"Error during search: {e}")
        return None

def fetch_lyrics_from_netease(song_id: int) -> Optional[str]:
    """
    Fetches the lyrics for a song from NetEase Music using the song ID.

    Args:
        song_id (int): The ID of the song.
    """
    lyric_url = f"https://music.163.com/api/song/lyric?os=pc&id={song_id}&lv=-1&kv=-1&tv=-1"

    try:
        response = requests.get(lyric_url, headers=HEADERS)
        data = response.json()
        
        print(f"Fetching lyrics for song ID: {song_id}")
        lyrics = data.get("lrc", {}).get("lyric", "")
        if lyrics:
            # Remove timestamps and return clean lyrics
            clean_lyrics = re.sub(r"\[.*?\]", "", lyrics).strip()
            # print(clean_lyrics)
            return clean_lyrics
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    song_title = "如果呢"
    song_artist = "郑润泽"
    song_id = search_netease_for_song_id(song_title, song_artist)
    song_lyrics = fetch_lyrics_from_netease(song_id)
    if song_lyrics:
        print(f"Successfully fetched for '{song_title}' by '{song_artist}':\n{song_id}")
        print(song_lyrics)
    else:
        print("Song not found.")  