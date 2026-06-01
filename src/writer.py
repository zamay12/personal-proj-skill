import json
from collections.abc import Callable
from pathlib import Path

from src.llm import call_llm
from src.models import ChapterPlan
from src.planner import StoryContext


DEFAULT_PROMPT_PATH = Path("prompts/writer.md")
DEFAULT_DRAFT_OUTPUT_PATH = Path("data/outputs/chapter_draft.md")


def load_writer_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def build_writer_prompt(
    template: str,
    *,
    plan: ChapterPlan,
    context: StoryContext,
    words: int,
) -> str:
    payload = {
        "target_words": words,
        "chapter_plan": plan.model_dump(mode="json"),
        **context.model_dump(),
    }
    return (
        f"{template.strip()}\n\n"
        "请基于以下上下文生成下一章 Markdown 正文：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def write_chapter_draft(
    *,
    plan: ChapterPlan,
    context: StoryContext,
    words: int,
    output_path: Path = DEFAULT_DRAFT_OUTPUT_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> str:
    prompt = build_writer_prompt(load_writer_prompt(prompt_path), plan=plan, context=context, words=words)
    draft = llm_func(prompt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(draft, encoding="utf-8")
    return draft
