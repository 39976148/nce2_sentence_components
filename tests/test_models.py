import json
from pathlib import Path

from nce2_core.models import Lesson, Sentence, Token, lesson_from_dict, lesson_to_dict


def test_lesson_roundtrip(tmp_path: Path):
    lesson = Lesson(
        book=2,
        lesson=1,
        title="A private conversation",
        sentences=[
            Sentence(
                id=1,
                original="I'm late.",
                expanded="I am late.",
                has_contraction=True,
                tokens=[
                    Token(text="I", role=""),
                    Token(text="am", role=""),
                    Token(text="late.", role=""),
                ],
            )
        ],
    )
    path = tmp_path / "01.json"
    path.write_text(
        json.dumps(lesson_to_dict(lesson), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    loaded = lesson_from_dict(json.loads(path.read_text(encoding="utf-8")))
    assert loaded.lesson == 1
    assert loaded.sentences[0].expanded == "I am late."
    assert loaded.sentences[0].has_contraction is True
    assert len(loaded.sentences[0].tokens) == 3
