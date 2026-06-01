from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from src.llm import call_llm
from src.models import ChapterPlan, ChapterReview
from src.planner import build_story_context, create_chapter_plan
from src.reviewer import review_chapter_draft
from src.reviser import revise_chapter_draft
from src.writer import write_chapter_draft


@dataclass
class ContinuationResult:
    plan: ChapterPlan
    draft: str
    review: ChapterReview
    final_text: str


def continue_story(
    *,
    after_chapter: int,
    direction: str,
    words: int,
    output_dir: Path = Path("data/outputs"),
    llm_func: Callable[[str], str] = call_llm,
) -> ContinuationResult:
    context = build_story_context(after_chapter=after_chapter, direction=direction)
    plan = create_chapter_plan(
        context=context,
        direction=direction,
        output_path=output_dir / "chapter_plan.json",
        llm_func=llm_func,
    )
    draft = write_chapter_draft(
        plan=plan,
        context=context,
        words=words,
        output_path=output_dir / "chapter_draft.md",
        llm_func=llm_func,
    )
    review = review_chapter_draft(
        plan=plan,
        draft=draft,
        context=context,
        output_path=output_dir / "chapter_review.json",
        llm_func=llm_func,
    )
    final_text = revise_chapter_draft(
        plan=plan,
        draft=draft,
        review=review,
        context=context,
        output_path=output_dir / "chapter_final.md",
        llm_func=llm_func,
    )
    return ContinuationResult(plan=plan, draft=draft, review=review, final_text=final_text)
