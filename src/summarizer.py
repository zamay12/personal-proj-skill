import json
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from src.llm import call_llm
from src.models import Chapter, ChapterSummary


DEFAULT_CHAPTERS_PATH = Path("data/processed/chapters.json")
DEFAULT_OUTPUT_PATH = Path("kb/summaries.json")
DEFAULT_PROMPT_PATH = Path("prompts/summarizer.md")


def load_summary_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def load_chapters(chapters_path: Path = DEFAULT_CHAPTERS_PATH) -> list[Chapter]:
    payload = json.loads(chapters_path.read_text(encoding="utf-8"))
    return [Chapter.model_validate(chapter) for chapter in payload.get("chapters", [])]


def build_summary_prompt(template: str, chapter: Chapter) -> str:
    chapter_payload = {
        "chapter_index": chapter.index,
        "chapter_title": chapter.title,
        "chapter_content": chapter.content,
    }
    return (
        f"{template.strip()}\n\n"
        "请摘要以下章节，只返回 JSON：\n"
        f"{json.dumps(chapter_payload, ensure_ascii=False, indent=2)}"
    )


def parse_summary_response(
    response_text: str,
    *,
    chapter_index: int,
    chapter_title: str,
) -> ChapterSummary:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"第 {chapter_index} 章《{chapter_title}》摘要不是合法 JSON: {error.msg}"
        ) from error

    if not isinstance(payload, dict):
        raise ValueError(f"第 {chapter_index} 章《{chapter_title}》摘要必须是 JSON 对象")

    payload["chapter_index"] = chapter_index
    payload["chapter_title"] = chapter_title

    try:
        return ChapterSummary.model_validate(payload)
    except ValidationError as error:
        raise ValueError(f"第 {chapter_index} 章《{chapter_title}》摘要字段校验失败: {error}") from error


def summarize_chapters(
    *,
    chapters_path: Path = DEFAULT_CHAPTERS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> list[ChapterSummary]:
    template = load_summary_prompt(prompt_path)
    chapters = load_chapters(chapters_path)
    summaries: list[ChapterSummary] = []

    for chapter in chapters:
        prompt = build_summary_prompt(template, chapter)
        response_text = llm_func(prompt)
        summaries.append(
            parse_summary_response(
                response_text,
                chapter_index=chapter.index,
                chapter_title=chapter.title,
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summaries": [summary.model_dump(mode="json") for summary in summaries]}
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summaries
