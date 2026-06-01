import json

import pytest
from pydantic import ValidationError

from src.models import ChapterSummary
from src.summarizer import (
    load_summary_prompt,
    parse_summary_response,
    summarize_chapters,
)


def test_summary_prompt_loads_required_fields() -> None:
    prompt = load_summary_prompt()

    for field_name in [
        "summary",
        "main_events",
        "characters",
        "locations",
        "new_settings",
        "open_threads",
        "emotional_tone",
    ]:
        assert field_name in prompt


def test_chapter_summary_validates_json_shape() -> None:
    summary = ChapterSummary.model_validate(
        {
            "chapter_index": 1,
            "chapter_title": "第一章 起点",
            "summary": "主角醒来并发现环境异常。",
            "main_events": ["主角醒来"],
            "characters": ["主角"],
            "locations": ["山村"],
            "new_settings": ["村外有禁地"],
            "open_threads": ["父亲失踪"],
            "emotional_tone": "悬疑",
        }
    )

    assert summary.chapter_index == 1
    assert summary.main_events == ["主角醒来"]


def test_chapter_summary_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        ChapterSummary.model_validate(
            {
                "chapter_index": 1,
                "chapter_title": "第一章 起点",
                "summary": "缺少列表字段。",
            }
        )


def test_parse_summary_response_reports_invalid_json() -> None:
    with pytest.raises(ValueError, match="第 1 章.*不是合法 JSON"):
        parse_summary_response("not json", chapter_index=1, chapter_title="第一章 起点")


def test_parse_summary_response_reports_validation_error() -> None:
    with pytest.raises(ValueError, match="第 1 章.*字段校验失败"):
        parse_summary_response(
            json.dumps({"summary": "缺少字段。"}, ensure_ascii=False),
            chapter_index=1,
            chapter_title="第一章 起点",
        )


def test_summarize_chapters_saves_validated_summaries(tmp_path) -> None:
    chapters_path = tmp_path / "chapters.json"
    summaries_path = tmp_path / "summaries.json"
    prompt_path = tmp_path / "summarizer.md"
    prompt_path.write_text(
        "请输出 summary main_events characters locations new_settings open_threads emotional_tone",
        encoding="utf-8",
    )
    chapters_path.write_text(
        json.dumps(
            {
                "title": "demo",
                "chapters": [
                    {
                        "index": 1,
                        "title": "第一章 起点",
                        "content": "主角醒来。",
                        "paragraphs": [{"index": 1, "text": "主角醒来。"}],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    def fake_llm(prompt: str) -> str:
        assert "第一章 起点" in prompt
        return json.dumps(
            {
                "summary": "主角醒来。",
                "main_events": ["主角醒来"],
                "characters": ["主角"],
                "locations": [],
                "new_settings": [],
                "open_threads": [],
                "emotional_tone": "平静",
            },
            ensure_ascii=False,
        )

    summaries = summarize_chapters(
        chapters_path=chapters_path,
        output_path=summaries_path,
        prompt_path=prompt_path,
        llm_func=fake_llm,
    )

    saved = json.loads(summaries_path.read_text(encoding="utf-8"))
    assert summaries[0].chapter_title == "第一章 起点"
    assert saved["summaries"][0]["summary"] == "主角醒来。"
