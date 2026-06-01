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
