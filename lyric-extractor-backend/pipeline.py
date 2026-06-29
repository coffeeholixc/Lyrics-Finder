import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from extractor import get_chinese_lyrics

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

# Function to get lyrics from OpenAI API
def process_lyrics_with_ai(raw_lyrics:str) -> LyricsResponse:
    """
    Sends the raw lyrics to the OpenAI API for processing and 
    returns the structured JSON output containing the lyrics in 
    Hanzi, Pinyin, and English translation.
    """

    print("Sending lyrics to OpenAI API for processing...")

    system_prompt = (
        "You are an expert translator and linguist. Take the provided raw Chinese lyrics."
        "For every distinct line, translate it into English and provide the correct Pinyin"
        "Pay careful attention to the context and meaning of the lyrics, especially to the polyphonic characters (多音字) and tone sandhi to ensure the Pinyin matches"
        "Return the results strictly matching the requested JSON schema"
    )

# Call  the OpenAI API with the system prompt and raw lyrics
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_lyrics}
        ],
        response_format=LyricsResponse,
    )
    return completion.choices[0].message.parsed

# TESTING MAIN FUNCTION
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=8MG--WuNW1Y&list=RD8MG--WuNW1Y&start_radio=1"

    # Running scraper
    raw_text = get_chinese_lyrics(youtube_url)

    # Running Ai pipeline
    if "Error" not in raw_text:
        structured_data = process_lyrics_with_ai(raw_text)

        print("\nStructured Lyrics Data:")
        for item in structured_data.lyrics: #note for self: object.attribute. structured_data is an instance of LyricsResponse, which has a list of LyricsLine objects in the lyrics attribute
            print(f"Hanzi: {item.hanzi}") 
            print(f"Pinyin: {item.pinyin}") 
            print(f"English: {item.english}")
            print("-" * 20)
    else:
        print(raw_text) 