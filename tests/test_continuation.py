import json

from src.continuation import continue_story
from src.models import ChapterSummary
from src.planner import StoryContext, build_planning_prompt, select_recent_summaries


def test_select_recent_summaries_uses_at_most_latest_five() -> None:
    summaries = [
        ChapterSummary(
            chapter_index=index,
            chapter_title=f"第{index}章",
            summary=f"摘要{index}",
            main_events=[],
            characters=[],
            locations=[],
            new_settings=[],
            open_threads=[],
            emotional_tone="平静",
        )
        for index in range(1, 8)
    ]

    selected = select_recent_summaries(summaries, after_chapter=7)

    assert [summary.chapter_index for summary in selected] == [3, 4, 5, 6, 7]


def test_planning_prompt_uses_context_without_full_novel_text() -> None:
    context = StoryContext(
        recent_summaries=[
            ChapterSummary(
                chapter_index=1,
                chapter_title="第一章 起点",
                summary="林舟发现旧信。",
                main_events=["发现旧信"],
                characters=["林舟"],
                locations=["祠堂"],
                new_settings=[],
                open_threads=["父亲失踪"],
                emotional_tone="悬疑",
            )
        ],
        characters=[],
        worldbuilding=[],
        foreshadowing=[],
    )

    prompt = build_planning_prompt("规划 Prompt", context, "推进调查")

    assert "林舟发现旧信" in prompt
    assert "chapter_content" not in prompt


def test_continue_story_runs_plan_draft_review_revise_and_saves_outputs(tmp_path, monkeypatch) -> None:
    kb_dir = tmp_path / "kb"
    prompts_dir = tmp_path / "prompts"
    output_dir = tmp_path / "outputs"
    kb_dir.mkdir()
    prompts_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    (prompts_dir / "planner.md").write_text("剧情规划 Prompt", encoding="utf-8")
    (prompts_dir / "writer.md").write_text("续写生成 Prompt", encoding="utf-8")
    (prompts_dir / "reviewer.md").write_text("一致性审校 Prompt", encoding="utf-8")
    (prompts_dir / "reviser.md").write_text("修订 Prompt", encoding="utf-8")

    (kb_dir / "summaries.json").write_text(
        json.dumps(
            {
                "summaries": [
                    {
                        "chapter_index": index,
                        "chapter_title": f"第{index}章",
                        "summary": f"摘要{index}",
                        "main_events": [f"事件{index}"],
                        "characters": ["林舟"],
                        "locations": [],
                        "new_settings": [],
                        "open_threads": ["父亲失踪"],
                        "emotional_tone": "悬疑",
                    }
                    for index in range(1, 7)
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (kb_dir / "characters.json").write_text(
        json.dumps(
            {
                "characters": [
                    {
                        "name": "林舟",
                        "aliases": [],
                        "description": "调查父亲失踪的少年。",
                        "evidence": ["第 6 章《第6章》"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (kb_dir / "worldbuilding.json").write_text(
        json.dumps(
            {
                "worldbuilding": [
                    {
                        "name": "黑袍人",
                        "category": "势力",
                        "description": "身份未明。",
                        "evidence": ["第 5 章《第5章》"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (kb_dir / "foreshadowing.json").write_text(
        json.dumps(
            {
                "foreshadowing": [
                    {
                        "clue": "父亲失踪与黑袍人有关。",
                        "status": "未揭示",
                        "evidence": ["第 6 章《第6章》"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    calls: list[str] = []

    def fake_llm(prompt: str) -> str:
        if "剧情规划 Prompt" in prompt:
            calls.append("plan")
            assert "摘要1" not in prompt
            assert "摘要2" in prompt
            assert "摘要6" in prompt
            return json.dumps(
                {
                    "next_chapter_title": "第七章 旧信余温",
                    "chapter_goal": "推进调查但不揭示黑袍人身份。",
                    "beats": ["整理线索", "夜探祠堂"],
                    "must_include": ["父亲失踪"],
                    "avoid": ["揭露黑袍人身份"],
                    "ending_hook": "旧信背面显出暗纹。",
                },
                ensure_ascii=False,
            )
        if "续写生成 Prompt" in prompt:
            calls.append("draft")
            assert "第七章 旧信余温" in prompt
            return "# 第七章 旧信余温\n\n林舟再次来到祠堂。"
        if "一致性审校 Prompt" in prompt:
            calls.append("review")
            return json.dumps(
                {
                    "score": 92,
                    "passed": True,
                    "issues": [],
                    "revision_instruction": "保留草稿，仅润色语句。",
                },
                ensure_ascii=False,
            )
        if "修订 Prompt" in prompt:
            calls.append("revise")
            return "# 第七章 旧信余温\n\n林舟再次来到祠堂，旧信在掌心微微发烫。"
        raise AssertionError(f"unexpected prompt: {prompt}")

    result = continue_story(
        after_chapter=6,
        direction="推进主角调查父亲失踪真相，不要立刻揭露黑袍人身份",
        words=3000,
        output_dir=output_dir,
        llm_func=fake_llm,
    )

    assert calls == ["plan", "draft", "review", "revise"]
    assert result.review.passed is True
    assert (output_dir / "chapter_plan.json").exists()
    assert (output_dir / "chapter_draft.md").exists()
    assert (output_dir / "chapter_review.json").exists()
    assert (output_dir / "chapter_final.md").read_text(encoding="utf-8").startswith("# 第七章")
