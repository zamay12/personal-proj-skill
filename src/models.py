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


class EvidenceMixin(BaseModel):
    evidence: list[str] = Field(min_length=1)


class CharacterCard(EvidenceMixin):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    description: str = ""


class EventItem(EvidenceMixin):
    chapter: int = Field(ge=1)
    summary: str = Field(min_length=1)


class WorldbuildingItem(EvidenceMixin):
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ForeshadowingItem(EvidenceMixin):
    clue: str = Field(min_length=1)
    status: str = Field(min_length=1)


class ChapterPlan(BaseModel):
    next_chapter_title: str = Field(min_length=1)
    chapter_goal: str = Field(min_length=1)
    beats: list[str] = Field(min_length=1)
    must_include: list[str]
    avoid: list[str]
    ending_hook: str = Field(min_length=1)


class ChapterReview(BaseModel):
    score: float = Field(ge=0, le=100)
    passed: bool
    issues: list[str]
    revision_instruction: str = Field(min_length=1)
