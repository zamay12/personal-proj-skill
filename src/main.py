import json
from pathlib import Path

import typer

from src.chunker import split_book_into_chapters
from src.ingest import ingest_book


app = typer.Typer(help="Novel continuation agent commands.")


@app.command()
def ingest(txt_path: Path) -> None:
    """Read a txt novel, split chapters, and save processed JSON."""
    book = split_book_into_chapters(ingest_book(txt_path))
    output_path = Path("data/processed/chapters.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "title": book.title,
        "source_path": str(book.source_path) if book.source_path else None,
        "encoding": book.encoding,
        "chapters": [chapter.model_dump(mode="json") for chapter in book.chapters],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    typer.echo(f"Saved {len(book.chapters)} chapters to {output_path}")


if __name__ == "__main__":
    app()
