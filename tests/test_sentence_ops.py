from nce2_core.auto_annotate import auto_annotate_sentence
from nce2_core.models import Lesson, Sentence, Token
from nce2_core.sentence_ops import merge_with_next, renumber_lesson, split_sentence


def test_auto_annotate_simple():
    s = Sentence(
        id=1,
        original="I had a very good seat.",
        expanded="I had a very good seat.",
        has_contraction=False,
        tokens=[
            Token(text="I", role=""),
            Token(text="had", role=""),
            Token(text="a", role=""),
            Token(text="very", role=""),
            Token(text="good", role=""),
            Token(text="seat.", role=""),
        ],
    )
    auto_annotate_sentence(s)
    assert s.tokens[0].role == "主语"
    assert s.tokens[1].role == "谓语"
    assert any(t.role in {"宾语", "定语", "状语"} for t in s.tokens[2:])


def test_split_sentence():
    lesson = Lesson(
        book=2,
        lesson=1,
        title="Test",
        sentences=[
            Sentence(
                id=1,
                original="A and B.",
                expanded="A and B.",
                has_contraction=False,
                tokens=[Token(text="A", role=""), Token(text="and", role=""), Token(text="B.", role="")],
            )
        ],
    )
    split_sentence(lesson, 0, "A.", "B.")
    assert len(lesson.sentences) == 2
    assert lesson.sentences[0].original == "A."
    assert lesson.sentences[1].original == "B."
    assert lesson.sentences[0].id == 1
    assert lesson.sentences[1].id == 2


def test_merge_with_next():
    lesson = Lesson(
        book=2,
        lesson=1,
        title="Test",
        sentences=[
            Sentence(id=1, original="Hello.", expanded="Hello.", has_contraction=False, tokens=[Token(text="Hello.", role="")]),
            Sentence(id=2, original="World.", expanded="World.", has_contraction=False, tokens=[Token(text="World.", role="")]),
        ],
    )
    merge_with_next(lesson, 0)
    assert len(lesson.sentences) == 1
    assert "Hello." in lesson.sentences[0].original
    assert "World." in lesson.sentences[0].original
