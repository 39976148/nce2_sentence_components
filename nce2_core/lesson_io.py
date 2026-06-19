from __future__ import annotations

import json
from pathlib import Path

from nce2_core.models import Lesson, lesson_from_dict, lesson_to_dict


def load_lesson(path: Path) -> Lesson:
    return lesson_from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_lesson(lesson: Lesson, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
