import json
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from src.llm import call_llm
from src.models import ChapterPlan, ChapterReview
from src.planner import StoryContext


DEFAULT_PROMPT_PATH = Path("prompts/reviewer.md")
DEFAULT_REVIEW_OUTPUT_PATH = Path("data/outputs/chapter_review.json")


def load_reviewer_prompt(prompt_path: Path = DEFAULT_PROMPT_PATH) -> str:
    return prompt_path.read_text(encoding="utf-8")


def build_reviewer_prompt(
    template: str,
    *,
    plan: ChapterPlan,
    draft: str,
    context: StoryContext,
) -> str:
    payload = {
        "chapter_plan": plan.model_dump(mode="json"),
        "chapter_draft": draft,
        **context.model_dump(),
    }
    return (
        f"{template.strip()}\n\n"
        "请审校以下续写草稿，只返回 JSON：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def parse_review_response(response_text: str) -> ChapterReview:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"一致性审校结果不是合法 JSON: {error.msg}") from error

    try:
        return ChapterReview.model_validate(payload)
    except ValidationError as error:
        raise ValueError(f"一致性审校字段校验失败: {error}") from error


def review_chapter_draft(
    *,
    plan: ChapterPlan,
    draft: str,
    context: StoryContext,
    output_path: Path = DEFAULT_REVIEW_OUTPUT_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    llm_func: Callable[[str], str] = call_llm,
) -> ChapterReview:
    prompt = build_reviewer_prompt(
        load_reviewer_prompt(prompt_path),
        plan=plan,
        draft=draft,
        context=context,
    )
    review = parse_review_response(llm_func(prompt))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(review.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return review
