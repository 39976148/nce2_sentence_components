"""NCE2-only book constants."""

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


NCE2 = BookSpec(
    id=2,
    label="新概念英语第二册",
    txt_subdir="第二册",
    titles_file="titles.json",
    lesson_count=96,
)


def default_book() -> BookSpec:
    return NCE2


def nce_txt_dir(root: Path) -> Path:
    return root / "nce_txt" / NCE2.txt_subdir


def titles_path(root: Path) -> Path:
    return root / "data" / NCE2.titles_file


def lessons_dir(root: Path) -> Path:
    return root / "data" / "lessons"
