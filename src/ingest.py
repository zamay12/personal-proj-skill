from pathlib import Path

from src.models import Book


SUPPORTED_ENCODINGS = ("utf-8", "utf-8-sig", "gbk")


def read_text_file(path: str | Path) -> tuple[str, str]:
    txt_path = Path(path)
    last_error: UnicodeDecodeError | None = None

    for encoding in SUPPORTED_ENCODINGS:
        try:
            return txt_path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as error:
            last_error = error

    if last_error is not None:
        raise last_error
    raise FileNotFoundError(txt_path)


def clean_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]

    cleaned_lines: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank:
            if not previous_blank and cleaned_lines:
                cleaned_lines.append("")
            previous_blank = True
            continue

        cleaned_lines.append(line.strip())
        previous_blank = False

    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def ingest_book(path: str | Path) -> Book:
    txt_path = Path(path)
    raw_text, encoding = read_text_file(txt_path)
    text = clean_text(raw_text)
    return Book(
        title=txt_path.stem,
        text=text,
        source_path=txt_path,
        encoding=encoding,
    )
