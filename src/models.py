from pathlib import Path

from pydantic import BaseModel, Field


class Paragraph(BaseModel):
    index: int = Field(ge=1)
    text: str


class Chapter(BaseModel):
    index: int = Field(ge=1)
    title: str
    content: str
    paragraphs: list[Paragraph] = Field(default_factory=list)


class Book(BaseModel):
    title: str
    text: str
    source_path: Path | None = None
    encoding: str | None = None
    chapters: list[Chapter] = Field(default_factory=list)


class ChapterSummary(BaseModel):
    chapter_index: int = Field(ge=1)
    chapter_title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    main_events: list[str]
    characters: list[str]
    locations: list[str]
    new_settings: list[str]
    open_threads: list[str]
    emotional_tone: str = Field(min_length=1)
