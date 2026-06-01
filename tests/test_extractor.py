import json

from src.extractor import extract_knowledge


def test_extract_knowledge_saves_deduped_outputs(tmp_path) -> None:
    chapters_path = tmp_path / "chapters.json"
    summaries_path = tmp_path / "summaries.json"
    output_dir = tmp_path / "kb"
    prompt_path = tmp_path / "extractor.md"
    prompt_path.write_text("抽取 characters events worldbuilding foreshadowing", encoding="utf-8")

    chapters_path.write_text(
        json.dumps(
            {
                "chapters": [
                    {
                        "index": 1,
                        "title": "第一章 起点",
                        "content": "林舟发现旧信。",
                        "paragraphs": [{"index": 1, "text": "林舟发现旧信。"}],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    summaries_path.write_text(
        json.dumps(
            {
                "summaries": [
                    {
                        "chapter_index": 1,
                        "chapter_title": "第一章 起点",
                        "summary": "林舟发现旧信。",
                        "main_events": ["林舟发现旧信"],
                        "characters": ["林舟"],
                        "locations": ["祠堂"],
                        "new_settings": [],
                        "open_threads": ["父亲失踪"],
                        "emotional_tone": "悬疑",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    def fake_llm(prompt: str) -> str:
        assert "林舟发现旧信" in prompt
        return json.dumps(
            {
                "characters": [
                    {"name": "林舟", "description": "少年", "evidence": ["第 1 章《第一章 起点》"]},
                    {"name": "林舟", "description": "少年", "evidence": ["第 1 章《第一章 起点》"]},
                ],
                "events": [
                    {
                        "chapter": 1,
                        "summary": "林舟发现旧信。",
                        "evidence": ["第 1 章《第一章 起点》"],
                    },
                    {
                        "chapter": 1,
                        "summary": "林舟发现旧信。",
                        "evidence": ["第 1 章《第一章 起点》"],
                    },
                ],
                "worldbuilding": [
                    {
                        "name": "祠堂",
                        "category": "地点",
                        "description": "村中祠堂。",
                        "evidence": ["第 1 章《第一章 起点》"],
                    }
                ],
                "foreshadowing": [
                    {
                        "clue": "旧信暗示父亲失踪另有隐情。",
                        "status": "未揭示",
                        "evidence": ["第 1 章《第一章 起点》"],
                    }
                ],
            },
            ensure_ascii=False,
        )

    result = extract_knowledge(
        chapters_path=chapters_path,
        summaries_path=summaries_path,
        output_dir=output_dir,
        prompt_path=prompt_path,
        llm_func=fake_llm,
    )

    characters = json.loads((output_dir / "characters.json").read_text(encoding="utf-8"))
    events = json.loads((output_dir / "events.json").read_text(encoding="utf-8"))

    assert len(result.characters) == 1
    assert len(result.events) == 1
    assert characters["characters"][0]["evidence"] == ["第 1 章《第一章 起点》"]
    assert events["events"][0]["summary"] == "林舟发现旧信。"
