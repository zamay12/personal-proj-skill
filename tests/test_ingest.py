from src.ingest import clean_text, ingest_book


def test_clean_text_collapses_extra_blank_lines() -> None:
    assert clean_text("  第一章\n\n\n正文一。\r\n\r\n\r\n正文二。\n\n") == "第一章\n\n正文一。\n\n正文二。"


def test_ingest_book_reads_utf8_text(tmp_path) -> None:
    txt_path = tmp_path / "novel.txt"
    txt_path.write_text("第一章\n\n正文。", encoding="utf-8")

    book = ingest_book(txt_path)

    assert book.title == "novel"
    assert book.text == "第一章\n\n正文。"
    assert book.source_path == txt_path
    assert book.encoding == "utf-8"
