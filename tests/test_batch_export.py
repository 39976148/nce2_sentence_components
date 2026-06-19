from pathlib import Path

from nce2_core.models import Sentence, Token
from nce2_export.batch_export import export_all_lessons
from nce2_export.slide_render import render_token_groups

ROOT = Path(__file__).resolve().parents[1]


def test_render_token_groups_contains_word_and_role():
    sentence = Sentence(
        id=1,
        original="I am late.",
        expanded="I am late.",
        has_contraction=False,
        tokens=[
            Token(text="I", role="主语"),
            Token(text="am", role="系动词"),
            Token(text="late.", role="表语"),
        ],
    )
    html = render_token_groups(sentence)
    assert 'class="token-word"' in html
    assert "主语" in html
    assert "late." in html


def test_export_all_lessons_index(tmp_path: Path):
    lessons_src = ROOT / "data" / "lessons"
    out = tmp_path / "out"
    export_all_lessons(lessons_src, out, lesson_nums=[1, 2])
    assert (out / "lesson_01.html").exists()
    assert (out / "lesson_02.html").exists()
    index = (out / "index.html").read_text(encoding="utf-8")
    assert "Lesson 01" in index
    assert "Lesson 02" in index
