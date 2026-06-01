import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.llm import call_llm
from src.models import (
    Chapter,
    ChapterSummary,
    CharacterCard,
    EventItem,
    ForeshadowingItem,
    WorldbuildingItem,
)
from src.summarizer import load_chapters


DEFAULT_CHAPTERS_PATH = Path("data/processed/chapters.json")
DEFAULT_SUMMARIES_PATH = Path("kb/summaries.json")
DEFAULT_OUTPUT_DIR = Path("kb")
DEFAULT_PROMPT_PATH = Path("prompts/extractor.md")


@dataclass
class ExtractionResult:
    characters: list[CharacterCard]
    events: list[EventItem]
    worldbuilding: list[WorldbuildingItem]
    foreshadowing: list[ForeshadowingItem]


def load_extractor_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def load_summaries(summaries_path: Path = DEFAULT_SUMMARIES_PATH) -> list[ChapterSummary]:
    payload = json.loads(summaries_path.read_text(encoding="utf-8"))
    return [ChapterSummary.model_validate(summary) for summary in payload.get("summaries", [])]


def build_extraction_prompt(template: str, chapter: Chapter, summary: ChapterSummary) -> str:
    chapter_payload = {
        "chapter_index": chapter.index,
        "chapter_title": chapter.title,
        "chapter_summary": summary.model_dump(mode="json"),
        "chapter_content": chapter.content,
    }
    return (
        f"{template.strip()}\n\n"
        "请从以下章节摘要和正文中抽取知识，只返回 JSON：\n"
        f"{json.dumps(chapter_payload, ensure_ascii=False, indent=2)}"
    )


def parse_extraction_response(response_text: str, *, chapter: Chapter) -> ExtractionResult:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"第 {chapter.index} 章《{chapter.title}》知识抽取结果不是合法 JSON: {error.msg}") from error

    if not isinstance(payload, dict):
        raise ValueError(f"第 {chapter.index} 章《{chapter.title}》知识抽取结果必须是 JSON 对象")

    try:
        return ExtractionResult(
            characters=[CharacterCard.model_validate(item) for item in _items(payload, "characters")],
            events=[EventItem.model_validate(item) for item in _items(payload, "events")],
            worldbuilding=[
                WorldbuildingItem.model_validate(item) for item in _items(payload, "worldbuilding")
            ],
            foreshadowing=[
                ForeshadowingItem.model_validate(item) for item in _items(payload, "foreshadowing")
            ],
        )
    except ValidationError as error:
        raise ValueError(f"第 {chapter.index} 章《{chapter.title}》知识抽取字段校验失败: {error}") from error


def extract_knowledge(
    *,
    chapters_path: Path = DEFAULT_CHAPTERS_PATH,
    summaries_path: Path = DEFAULT_SUMMARIES_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> ExtractionResult:
    template = load_extractor_prompt(prompt_path)
    chapters = load_chapters(chapters_path)
    summaries_by_chapter = {summary.chapter_index: summary for summary in load_summaries(summaries_path)}

    all_characters: list[CharacterCard] = []
    all_events: list[EventItem] = []
    all_worldbuilding: list[WorldbuildingItem] = []
    all_foreshadowing: list[ForeshadowingItem] = []

    for chapter in chapters:
        summary = summaries_by_chapter.get(chapter.index)
        if summary is None:
            raise ValueError(f"第 {chapter.index} 章《{chapter.title}》缺少章节摘要，无法抽取知识")

        prompt = build_extraction_prompt(template, chapter, summary)
        extraction = parse_extraction_response(llm_func(prompt), chapter=chapter)
        all_characters.extend(extraction.characters)
        all_events.extend(extraction.events)
        all_worldbuilding.extend(extraction.worldbuilding)
        all_foreshadowing.extend(extraction.foreshadowing)

    result = ExtractionResult(
        characters=_dedupe_characters(all_characters),
        events=_dedupe_events(all_events),
        worldbuilding=all_worldbuilding,
        foreshadowing=all_foreshadowing,
    )
    write_extraction_outputs(result, output_dir)
    return result


def write_extraction_outputs(result: ExtractionResult, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "characters.json", "characters", result.characters)
    _write_json(output_dir / "events.json", "events", result.events)
    _write_json(output_dir / "worldbuilding.json", "worldbuilding", result.worldbuilding)
    _write_json(output_dir / "foreshadowing.json", "foreshadowing", result.foreshadowing)


def _items(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"`{key}` 必须是数组")
    return value


def _dedupe_characters(characters: list[CharacterCard]) -> list[CharacterCard]:
    seen: set[str] = set()
    deduped: list[CharacterCard] = []
    for character in characters:
        key = character.name.strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(character)
    return deduped


def _dedupe_events(events: list[EventItem]) -> list[EventItem]:
    seen: set[tuple[int, str]] = set()
    deduped: list[EventItem] = []
    for event in events:
        key = (event.chapter, event.summary.strip())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return deduped


def _write_json(path: Path, key: str, items: list[Any]) -> None:
    payload = {key: [item.model_dump(mode="json") for item in items]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
