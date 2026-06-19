import json
from pathlib import Path

from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(__file__).resolve().parents[1]


def test_export_lesson1_html(tmp_path: Path):
    json_path = ROOT / "data" / "lessons" / "01.json"
    if not json_path.exists():
        from nce2_core.batch import batch_import_book2

        batch_import_book2(
            ROOT / "nce_txt" / "第二册",
            ROOT / "data" / "titles.json",
            ROOT / "data" / "lessons",
            lessons=[1],
        )
    lesson = lesson_from_dict(json.loads(json_path.read_text(encoding="utf-8")))
    out = tmp_path / "lesson_01.html"
    export_lesson_html(lesson, out)
    html = out.read_text(encoding="utf-8")
    assert "Lesson 1: A private conversation" in html
    assert "slide active" in html
    assert "Last week I went to the theatre." in html
    assert "<style>" in html
    assert "<script>" in html
