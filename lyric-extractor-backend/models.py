# Define table structure to store the lyrics

from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone

class SongLyric(SQLModel, table=True):
    __tablename__ = "songs_lyric"

    id: Optional[int] = Field(default=None, primary_key=True)
    video_url: Optional[str] = Field(default=None, index=True, unique=True)
    title: Optional[str] = Field(default=None, index=True)
    artist: Optional[str] = Field(default=None, index=True)
    original_lyrics: Optional[str]
    pinyin_lyrics: Optional[str] = None
    translated_lyrics: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
