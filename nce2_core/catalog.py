"""NCE book catalog — multi-book extension (UI shows enabled books only)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BookSpec:
    id: int
    label: str
    txt_subdir: str
    titles_file: str
    lesson_count: int
    enabled: bool


BOOKS: dict[int, BookSpec] = {
    1: BookSpec(
        id=1,
        label="新概念英语第一册",
        txt_subdir="第一册",
        titles_file="titles_book1.json",
        lesson_count=72,
        enabled=False,
    ),
    2: BookSpec(
        id=2,
        label="新概念英语第二册",
        txt_subdir="第二册",
        titles_file="titles.json",
        lesson_count=96,
        enabled=True,
    ),
    3: BookSpec(
        id=3,
        label="新概念英语第三册",
        txt_subdir="第三册",
        titles_file="titles_book3.json",
        lesson_count=60,
        enabled=False,
    ),
    4: BookSpec(
        id=4,
        label="新概念英语第四册",
        txt_subdir="第四册",
        titles_file="titles_book4.json",
        lesson_count=48,
        enabled=False,
    ),
}


def get_book(book_id: int) -> BookSpec:
    if book_id not in BOOKS:
        raise KeyError(f"Unknown book id: {book_id}")
    return BOOKS[book_id]


def enabled_books() -> list[BookSpec]:
    return [b for b in BOOKS.values() if b.enabled]


def nce_txt_dir(root: Path, book: BookSpec) -> Path:
    return root / "nce_txt" / book.txt_subdir


def titles_path(root: Path, book: BookSpec) -> Path:
    return root / "data" / book.titles_file


def lessons_dir(root: Path, book: BookSpec) -> Path:
    return root / "data" / "lessons" / f"book{book.id}"


def default_book() -> BookSpec:
    enabled = enabled_books()
    if not enabled:
        raise RuntimeError("No enabled books in catalog")
    return enabled[0]
