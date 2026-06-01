import re

from src.models import Book, Chapter, Paragraph


CHAPTER_TITLE_PATTERN = re.compile(
    r"^\s*(?:(?:卷[一二三四五六七八九十百千万\d]+)\s+)?"
    r"(?:(?:第[一二三四五六七八九十百千万零〇\d]{1,6}章)|(?:Chapter\s+\d+))"
    r"(?:\s+.*)?\s*$",
    re.IGNORECASE,
)


def is_chapter_title(line: str) -> bool:
    return bool(CHAPTER_TITLE_PATTERN.match(line))


def split_paragraphs(content: str) -> list[Paragraph]:
    blocks = re.split(r"\n\s*\n+", content.strip())
    paragraphs: list[Paragraph] = []

    for block in blocks:
        text = block.strip()
        if not text:
            continue
        paragraphs.append(Paragraph(index=len(paragraphs) + 1, text=text))

    return paragraphs


def split_book_into_chapters(book: Book) -> Book:
    chapters = split_text_into_chapters(book.text)
    return book.model_copy(update={"chapters": chapters})


def split_text_into_chapters(text: str) -> list[Chapter]:
    lines = text.splitlines()
    chapters: list[Chapter] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if is_chapter_title(line):
            if current_title is not None:
                chapters.append(_build_chapter(len(chapters) + 1, current_title, current_lines))
            current_title = line.strip()
            current_lines = []
            continue

        current_lines.append(line)

    if current_title is not None:
        chapters.append(_build_chapter(len(chapters) + 1, current_title, current_lines))
    elif text.strip():
        chapters.append(_build_chapter(1, "正文", lines))

    return chapters


def _build_chapter(index: int, title: str, lines: list[str]) -> Chapter:
    content = "\n".join(lines).strip()
    return Chapter(
        index=index,
        title=title,
        content=content,
        paragraphs=split_paragraphs(content),
    )
