import json
from collections.abc import Callable
from pathlib import Path

from src.llm import call_llm
from src.models import ChapterPlan, ChapterReview
from src.planner import StoryContext


DEFAULT_PROMPT_PATH = Path("prompts/reviser.md")
DEFAULT_FINAL_OUTPUT_PATH = Path("data/outputs/chapter_final.md")


def load_reviser_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def build_reviser_prompt(
    template: str,
    *,
    plan: ChapterPlan,
    draft: str,
    review: ChapterReview,
    context: StoryContext,
) -> str:
    payload = {
        "chapter_plan": plan.model_dump(mode="json"),
        "chapter_draft": draft,
        "review": review.model_dump(mode="json"),
        **context.model_dump(),
    }
    return (
        f"{template.strip()}\n\n"
        "请根据以下审校报告修订草稿，并只输出最终 Markdown 正文：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def revise_chapter_draft(
    *,
    plan: ChapterPlan,
    draft: str,
    review: ChapterReview,
    context: StoryContext,
    output_path: Path = DEFAULT_FINAL_OUTPUT_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> str:
    prompt = build_reviser_prompt(
        load_reviser_prompt(prompt_path),
        plan=plan,
        draft=draft,
        review=review,
        context=context,
    )
    final_text = llm_func(prompt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_text, encoding="utf-8")
    return final_text
