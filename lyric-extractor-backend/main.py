import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Optional
from pipeline import orchestrate_lyrics_extraction, LyricsResponse
from extractor import get_chinese_lyrics

app = FastAPI(
    title="Lyric Extractor API",
    description="A pipeline to extract lyrics from YouTube videos with fallback engines (external search on NetEase Music)",
    version="1.0.0",
)

# Define expected JSON payload incoming request structure
class LyricsRequest(BaseModel):
    video_url: str

# Main extraction endpoint
@app.post(
    "/extract-lyrics",
    response_model=LyricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract lyrics from a YouTube video URL",
    description="This endpoint takes a YouTube video URL and returns structured lyrics data, including Hanzi, Pinyin, and English translations. It uses a multi-step pipeline with fallback mechanisms.",
)

async def extract_lyrics(payload: LyricsRequest):
    url_str = payload.video_url
    print(f"Received API request for URL: {url_str}")

    # Trigger background scrapers to collect raw tracks(Captions/Description) from YouTube
    try:
        scraped_content = get_chinese_lyrics(url_str)  # returns a str dictionary with keys "transcript" and "description"
        print(f"Scraped content for {url_str}: {scraped_content}")
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload data: {str(val_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during scraping: {str(e)}"
        )
    
    # Run the orchestration pipeline to process the scraped content
    structured_lyrics = orchestrate_lyrics_extraction(scraped_content)

    # If all failed, return a 404 with a message
    if not structured_lyrics or not structured_lyrics.lyrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lyrics could not be extracted from the provided YouTube URL."
        )
    
    return structured_lyrics # Return Pydantic object as JSON

# Health check endpoint
@app.get("/health",status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "environment_configured": bool(os.getenv("OPENAI_API_KEY"))}