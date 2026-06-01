import pytest
from pydantic import ValidationError

from src.models import CharacterCard, EventItem, ForeshadowingItem, WorldbuildingItem


def test_character_card_requires_name_and_evidence() -> None:
    character = CharacterCard(
        name="林舟",
        aliases=["阿舟"],
        description="寻找父亲失踪真相的少年。",
        evidence=["第 1 章《起点》"],
    )

    assert character.name == "林舟"
    assert character.evidence == ["第 1 章《起点》"]


def test_character_card_rejects_missing_evidence() -> None:
    with pytest.raises(ValidationError):
        CharacterCard(name="林舟", evidence=[])


def test_event_item_keeps_chapter_summary_and_evidence() -> None:
    event = EventItem(
        chapter=1,
        summary="林舟在祠堂发现父亲留下的旧信。",
        evidence=["第 1 章《起点》"],
    )

    assert event.chapter == 1
    assert "旧信" in event.summary


def test_worldbuilding_item_validates_description() -> None:
    item = WorldbuildingItem(
        name="禁林",
        category="地点",
        description="村外禁止进入的林地。",
        evidence=["第 2 章《远行》"],
    )

    assert item.category == "地点"


def test_foreshadowing_item_records_clue() -> None:
    item = ForeshadowingItem(
        clue="黑袍人认得林舟的父亲。",
        status="未揭示",
        evidence=["第 3 章《黑影》"],
    )

    assert item.status == "未揭示"
