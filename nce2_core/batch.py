from __future__ import annotations

import json
from pathlib import Path

from nce2_core.models import lesson_to_dict
from nce2_core.pipeline import build_lesson_from_txt


def load_titles(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def batch_import_book2(
    txt_dir: Path,
    titles_path: Path,
    out_dir: Path,
    lessons: list[int] | None = None,
) -> None:
    titles = load_titles(titles_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    nums = lessons or list(range(1, 97))
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
