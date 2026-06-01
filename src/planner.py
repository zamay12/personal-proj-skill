import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from src.extractor import load_summaries
from src.llm import call_llm
from src.models import (
    ChapterPlan,
    ChapterSummary,
    CharacterCard,
    ForeshadowingItem,
    WorldbuildingItem,
)


DEFAULT_SUMMARIES_PATH = Path("kb/summaries.json")
DEFAULT_CHARACTERS_PATH = Path("kb/characters.json")
DEFAULT_WORLDBUILDING_PATH = Path("kb/worldbuilding.json")
DEFAULT_FORESHADOWING_PATH = Path("kb/foreshadowing.json")
DEFAULT_PROMPT_PATH = Path("prompts/planner.md")
DEFAULT_PLAN_OUTPUT_PATH = Path("data/outputs/chapter_plan.json")

T = TypeVar("T", bound=BaseModel)


@dataclass
class StoryContext:
    recent_summaries: list[ChapterSummary]
    characters: list[CharacterCard]
    worldbuilding: list[WorldbuildingItem]
    foreshadowing: list[ForeshadowingItem]

    def model_dump(self) -> dict[str, Any]:
        return {
            "recent_summaries": [item.model_dump(mode="json") for item in self.recent_summaries],
            "characters": [item.model_dump(mode="json") for item in self.characters],
            "worldbuilding": [item.model_dump(mode="json") for item in self.worldbuilding],
            "foreshadowing": [item.model_dump(mode="json") for item in self.foreshadowing],
        }


def load_planner_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def build_story_context(
    *,
    after_chapter: int,
    direction: str,
    summaries_path: Path = DEFAULT_SUMMARIES_PATH,
    characters_path: Path = DEFAULT_CHARACTERS_PATH,
    worldbuilding_path: Path = DEFAULT_WORLDBUILDING_PATH,
    foreshadowing_path: Path = DEFAULT_FORESHADOWING_PATH,
) -> StoryContext:
    recent_summaries = select_recent_summaries(load_summaries(summaries_path), after_chapter)
    context_blob = _context_blob(direction, recent_summaries)
    recent_refs = {f"第 {summary.chapter_index} 章" for summary in recent_summaries}

    characters = _select_relevant(
        _load_items(characters_path, "characters", CharacterCard),
        context_blob,
        recent_refs,
        lambda item: [item.name, *item.aliases],
    )
    worldbuilding = _select_relevant(
        _load_items(worldbuilding_path, "worldbuilding", WorldbuildingItem),
        context_blob,
        recent_refs,
        lambda item: [item.name, item.category],
    )
    foreshadowing = _select_relevant(
        _load_items(foreshadowing_path, "foreshadowing", ForeshadowingItem),
        context_blob,
        recent_refs,
        lambda item: [item.clue, item.status],
    )
    return StoryContext(
        recent_summaries=recent_summaries,
        characters=characters,
        worldbuilding=worldbuilding,
        foreshadowing=foreshadowing,
    )


def select_recent_summaries(
    summaries: list[ChapterSummary],
    after_chapter: int,
    *,
    max_count: int = 5,
) -> list[ChapterSummary]:
    eligible = [summary for summary in summaries if summary.chapter_index <= after_chapter]
    eligible.sort(key=lambda summary: summary.chapter_index)
    return eligible[-max_count:]


def build_planning_prompt(template: str, context: StoryContext, direction: str) -> str:
    payload = {
        "user_direction": direction,
        **context.model_dump(),
    }
    return (
        f"{template.strip()}\n\n"
        "请基于以下上下文规划下一章，只返回 JSON：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def parse_plan_response(response_text: str) -> ChapterPlan:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"剧情规划结果不是合法 JSON: {error.msg}") from error

    try:
        return ChapterPlan.model_validate(payload)
    except ValidationError as error:
        raise ValueError(f"剧情规划字段校验失败: {error}") from error


def create_chapter_plan(
    *,
    context: StoryContext,
    direction: str,
    output_path: Path = DEFAULT_PLAN_OUTPUT_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> ChapterPlan:
    prompt = build_planning_prompt(load_planner_prompt(prompt_path), context, direction)
    plan = parse_plan_response(llm_func(prompt))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return plan


def _load_items(path: Path, key: str, model: type[T]) -> list[T]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [model.model_validate(item) for item in payload.get(key, [])]


def _select_relevant(
    items: list[T],
    context_blob: str,
    recent_refs: set[str],
    keywords_for: Callable[[T], list[str]],
    *,
    limit: int = 12,
) -> list[T]:
    relevant: list[T] = []
    for item in items:
        evidence = getattr(item, "evidence", [])
        keywords = [keyword for keyword in keywords_for(item) if keyword]
        evidence_match = any(any(ref in source for ref in recent_refs) for source in evidence)
        keyword_match = any(keyword in context_blob for keyword in keywords)
        if evidence_match or keyword_match:
            relevant.append(item)
        if len(relevant) >= limit:
            break
    return relevant


def _context_blob(direction: str, summaries: list[ChapterSummary]) -> str:
    parts = [direction]
    for summary in summaries:
        parts.extend(
            [
                summary.chapter_title,
                summary.summary,
                " ".join(summary.main_events),
                " ".join(summary.characters),
                " ".join(summary.locations),
                " ".join(summary.new_settings),
                " ".join(summary.open_threads),
            ]
        )
    return "\n".join(parts)
