from __future__ import annotations

import json
from pathlib import Path

from nce2_core.catalog import BookSpec, default_book, lessons_dir, nce_txt_dir, titles_path
from nce2_core.models import lesson_to_dict
from nce2_core.pipeline import build_lesson_from_txt


def load_titles(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def batch_import(
    root: Path,
    book: BookSpec | None = None,
    out_dir: Path | None = None,
    lessons: list[int] | None = None,
) -> None:
    book = book or default_book()
    txt_dir = nce_txt_dir(root, book)
    titles = load_titles(titles_path(root, book))
    out = out_dir or lessons_dir(root, book)
    out.mkdir(parents=True, exist_ok=True)
    nums = lessons or list(range(1, book.lesson_count + 1))
    for n in nums:
        title = titles.get(str(n)) or titles.get(str(n), f"Lesson {n}")
        txt_path = txt_dir / f"{n}.TXT"
        if not txt_path.exists():
            raise FileNotFoundError(txt_path)
        lesson = build_lesson_from_txt(txt_path, lesson_num=n, title=title)
        lesson.book = book.id
        out_path = out / f"{n:02d}.json"
        out_path.write_text(
            json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def batch_import_book2(
    txt_dir: Path,
    titles_path: Path,
    out_dir: Path,
    lessons: list[int] | None = None,
) -> None:
    """Backward-compatible wrapper for tests and legacy callers."""
    from nce2_core.catalog import get_book

    book = get_book(2)
    titles = load_titles(titles_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    nums = lessons or list(range(1, book.lesson_count + 1))
    for n in nums:
        title = titles[str(n)]
        txt_path = txt_dir / f"{n}.TXT"
        if not txt_path.exists():
            raise FileNotFoundError(txt_path)
        lesson = build_lesson_from_txt(txt_path, lesson_num=n, title=title)
        out_path = out_dir / f"{n:02d}.json"
        out_path.write_text(
            json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
