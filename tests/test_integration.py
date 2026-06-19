import json
from pathlib import Path

from nce2_core.batch import batch_import_book2
from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_lesson1(tmp_path: Path):
    lessons_dir = tmp_path / "lessons"
    batch_import_book2(
        ROOT / "nce_txt" / "第二册",
        ROOT / "data" / "titles.json",
        lessons_dir,
        lessons=[1],
    )
    lesson = lesson_from_dict(
        json.loads((lessons_dir / "01.json").read_text(encoding="utf-8"))
    )
    html_path = tmp_path / "lesson_01.html"
    export_lesson_html(lesson, html_path)
    html = html_path.read_text(encoding="utf-8")
    assert html.count('<section class="slide') == len(lesson.sentences)
    assert "private conversation" in html
