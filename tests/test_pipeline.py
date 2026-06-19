from pathlib import Path

from nce2_core.pipeline import build_lesson_from_txt

ROOT = Path(__file__).resolve().parents[1]
LESSON1 = ROOT / "nce_txt" / "第二册" / "1.TXT"


def test_build_lesson1():
    lesson = build_lesson_from_txt(
        LESSON1, lesson_num=1, title="A private conversation"
    )
    assert lesson.lesson == 1
    assert len(lesson.sentences) >= 14
    assert lesson.sentences[0].original.startswith("Last week")
    assert lesson.sentences[0].has_contraction is False
    contracted = [s for s in lesson.sentences if s.has_contraction]
    assert len(contracted) >= 1
    for s in lesson.sentences:
        assert s.tokens, f"sentence {s.id} has no tokens"
        assert s.id >= 1
