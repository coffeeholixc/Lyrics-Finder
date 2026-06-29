import os
import re
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from extractor import get_chinese_lyrics
from external_search import search_netease_for_song_id, fetch_lyrics_from_netease

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Schema for lyrics data (child blueprint)
class LyricsLine(BaseModel):
    hanzi: str
    pinyin: str
    english: str

# AI schema to get lyrics (parent blueprint)
class LyricsResponse(BaseModel):
    lyrics: list[LyricsLine]

# Above can be combined like
# class LyricsResponse(BaseModel):
#     class LyricsLine(BaseModel):
#         hanzi: str
#         pinyin: str
#         english: str
#     lyrics : list[LyricsLine]

# Function to use YT CC
def process_caption_with_ai(raw_lyrics: str) -> LyricsResponse:
    """
    Sends the raw captions to the OpenAI API for structured translation and Pinyin rendering.
    """
    print("Sending CC transcript to OpenAI API for processing...")

    system_prompt = (
        "You are an expert translator and bilingual music editor. Take the provided raw Chinese lyrics. "
        "For every line, translate it into English and provide the correct Pinyin. "
        "Pay careful attention to the context and meaning of the lyrics, especially to the polyphonic characters (多音字) and tone sandhi to ensure the Pinyin matches. "
        "Return the results strictly matching the requested JSON schema."
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_lyrics}
        ],
        response_format=LyricsResponse,
    )
    return completion.choices[0].message.parsed

def process_description_with_ai(raw_description:str) -> LyricsResponse:
    """
    Sends the raw description to the OpenAI API for processing and 
    returns the structured JSON output containing the lyrics in 
    Hanzi, Pinyin, and English translation.
    """

    print("Sending description to OpenAI API for processing...")

    system_prompt = (
        "You are an expert bilingual music editor and localization engine.\n"
        "You will be given a raw, cluttered YouTube video description box. Your tasks are:\n"
        "1. First, find out if the song lyrics exist inside the text.\n"
        "2. Locate and isolate the actual Chinese song lyrics (Hanzi).\n"
        "3. Strip away all marketing links, social media handles, sponsor promotions, and audio production credits.\n"
        "4. Step through the clean Chinese lyrics line-by-line.\n"
        "5. For every line, keep the original Hanzi, generate its accurate phonetic Pinyin (handling polyphonic characters and tone sandhi in context), "
        "and translate that specific line into natural English.\n"
        "Output the array strictly matching the JSON format structure provided."
    )

    completion = client.beta.chat.completions.parse(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_description}
        ],
        response_format = LyricsResponse,
    )
    return completion.choices[0].message.parsed

# TESTING MAIN FUNCTION
if __name__ == "__main__":
    # testing
    #youtube_url = "https://www.youtube.com/watch?v=8MG--WuNW1Y&list=RD8MG--WuNW1Y&start_radio=1"
    youtube_url = input("Enter YouTube URL: ")

    # Running scraper
    raw_text = get_chinese_lyrics(youtube_url) # returns a dictionary with keys "transcript" and "description"
    structured_data = None

    # Running pipeline
    if (not structured_data or not structured_data.lyrics) and raw_text.get("transcript"):
        try:
            structured_data = process_caption_with_ai(raw_text["transcript"])
        except Exception as e:
            print(f"Caption processing failed: {e}")
    
    if (not structured_data or not structured_data.lyrics) and raw_text.get("description"):
        try:
            structured_data = process_description_with_ai(raw_text["description"])
        except Exception as e:
            print(f"Description processing failed: {e}")   
    
    if not structured_data or not structured_data.lyrics:
            print("YouTube content yielded no lyric data. Initializing NetEase backup pipeline...")
            title = raw_text.get("title", "")
            artist = raw_text.get("artist", "")
            
            if title and artist:
                try:
                    # Clean up artist metadata string using regex
                    match = re.search(r"^(.*?[ \u4e00-\u9fff]+)", artist)
                    clean_artist = match.group(1).strip() if match else artist.strip()
                    
                    # Fetch via NetEase
                    song_id = search_netease_for_song_id(title, clean_artist)
                    if song_id:
                        raw_netease_lyrics = fetch_lyrics_from_netease(song_id)
                        if raw_netease_lyrics:
                            structured_data = process_description_with_ai(raw_netease_lyrics)
                except Exception as e:
                    print(f"NetEase backup pipeline encountered an error: {e}")
            else:
                print("Missing video metadata fields.")

    # Output the structured data
    if structured_data is not None:
        print("Structured Lyrics Data:")
        for item in structured_data.lyrics:
            print(f"Hanzi: {item.hanzi}") 
            print(f"Pinyin: {item.pinyin}") 
            print(f"English: {item.english}")
            print("-" * 20)
    else:
        print("No structured data to display.")