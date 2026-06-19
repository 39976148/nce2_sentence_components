from pathlib import Path

from nce2_core.parser import extract_lesson_body

ROOT = Path(__file__).resolve().parents[1]
LESSON1 = ROOT / "nce_txt" / "第二册" / "1.TXT"


def test_lesson1_extracts_body():
    body = extract_lesson_body(LESSON1)
    assert "Last week I went to the theatre." in body
    assert "private conversation" in body
    assert "New words" not in body
    assert "Why did the writer complain" not in body


def test_lesson1_not_empty():
    body = extract_lesson_body(LESSON1)
    assert len(body) > 200
