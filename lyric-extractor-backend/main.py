import os
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session, select
from database import get_session, init_db
from models import SongLyric
from pipeline import orchestrate_lyrics_extraction, LyricsResponse
from extractor import get_chinese_lyrics

# Lifespan context manager to initialize the database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    init_db()
    yield  # Control is returned to the application

app = FastAPI(
    title="Lyric Extractor API",
    description="A pipeline to extract lyrics from YouTube videos with fallback engines (external search on NetEase Music)",
    version="1.0.0",
    lifespan =lifespan,
)

# Below 2 allows CORS in FastAPI.
# Allow requests from React development server (CORS). Because By default, browser security blocks React from making requests to fastAPI.
origins = [
    "http://localhost:5173",  # React development server
    "http://127.0.0.1:5173",  # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Pydantic schema model
async def extract_lyrics(
    payload: LyricsRequest, db: Session = Depends(get_session)
    ):  
    url_str = payload.video_url
    print(f"Received API request for URL: {url_str}")

    # -------------------------------------------------------
    # Step 1: Check database cache first
    # -------------------------------------------------------
    statement = select(SongLyric).where(SongLyric.video_url == url_str)
    cached_song = db.exec(statement).first()
    if cached_song:
        print(f"Cache hit for URL: {url_str}. Returning cached lyrics.")
        # Split stored multi-line text into lists
        hanzi_lines = (cached_song.original_lyrics or "").split("\n")
        pinyin_lines = (cached_song.pinyin_lyrics or "").split("\n")
        english_lines = (cached_song.translated_lyrics or "").split("\n")

        # Pair the lines back into LyricsLine objects
        lyrics_list = [
            {"hanzi": h, "pinyin": p, "english": e}
            for h, p, e in zip(hanzi_lines, pinyin_lines, english_lines)
        ]

        return LyricsResponse(lyrics=lyrics_list)
    # -------------------------------------------------------
    # Step 2: Scrape and process the YouTube video
    # -------------------------------------------------------
    print(f"No cache found for URL: {url_str}. Proceeding to scrape and process.")
    
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
    # -------------------------------------------------------
    # Step 3: Save new lyrics to the database for future cache hits
    # -------------------------------------------------------
    try:
        #Convert Pydantic object to JSON string for storage
        lyrics_dict = structured_lyrics.model_dump()
        # Join the structured lines into multi-line strings
        hanzi_text = "\n".join([line.hanzi for line in structured_lyrics.lyrics])
        pinyin_text = "\n".join([line.pinyin for line in structured_lyrics.lyrics])
        english_text = "\n".join([line.english for line in structured_lyrics.lyrics])

        new_entry = SongLyric(
            video_url=url_str,
            title = scraped_content.get("title", ""),
            artist = scraped_content.get("artist", ""),
            original_lyrics=hanzi_text,  # Populates the required NOT NULL field
            pinyin_lyrics=pinyin_text,
            translated_lyrics=english_text,
            )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        print(f"Saving new lyrics entry to database for URL: {url_str}")
    except Exception as db_err:
        print(f"Error preparing database entry: {db_err}")

    return structured_lyrics # Return Pydantic object as JSON

# Health check endpoint
@app.get("/health",status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "environment_configured": bool(os.getenv("OPENAI_API_KEY"))}