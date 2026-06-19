"""Fill component roles for all existing lesson JSON files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nce2_core.auto_annotate import auto_annotate_lesson
from nce2_core.lesson_io import load_lesson, save_lesson


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    lessons_dir = root / "data" / "lessons"
    count = 0
    for path in sorted(lessons_dir.glob("*.json")):
        lesson = load_lesson(path)
        auto_annotate_lesson(lesson)
        save_lesson(lesson, path)
        count += 1
        print(f"annotated {path.name} ({len(lesson.sentences)} sentences)")
    print(f"Done: {count} lessons")


if __name__ == "__main__":
    main()
