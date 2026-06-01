from src.chunker import split_book_into_chapters, split_paragraphs
from src.models import Book


def test_split_chinese_chapters() -> None:
    book = Book(
        title="demo",
        text=(
            "第一章 起点\n"
            "少年醒来。\n\n"
            "他看见远山。\n\n"
            "第002章 远行\n"
            "马蹄声碎。\n"
        ),
    )

    result = split_book_into_chapters(book)

    assert [chapter.title for chapter in result.chapters] == ["第一章 起点", "第002章 远行"]
    assert result.chapters[0].paragraphs[0].text == "少年醒来。"
    assert result.chapters[1].paragraphs[0].text == "马蹄声碎。"


def test_split_english_chapters() -> None:
    book = Book(
        title="demo",
        text=(
            "Chapter 1 The Door\n"
            "The door opened.\n\n"
            "Chapter 2 The Road\n"
            "The road waited.\n"
        ),
    )

    result = split_book_into_chapters(book)

    assert [chapter.title for chapter in result.chapters] == [
        "Chapter 1 The Door",
        "Chapter 2 The Road",
    ]
    assert result.chapters[0].content == "The door opened."
    assert result.chapters[1].content == "The road waited."


def test_split_paragraphs_removes_empty_blocks() -> None:
    paragraphs = split_paragraphs("第一段。\n\n\n第二段第一行。\n第二段第二行。\n\n  \n第三段。")

    assert [paragraph.text for paragraph in paragraphs] == [
        "第一段。",
        "第二段第一行。\n第二段第二行。",
        "第三段。",
    ]
    assert [paragraph.index for paragraph in paragraphs] == [1, 2, 3]
