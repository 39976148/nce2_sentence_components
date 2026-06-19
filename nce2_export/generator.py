from __future__ import annotations

import html
from pathlib import Path

from nce2_core.models import Lesson, Sentence
from nce2_export.slide_render import render_token_groups

_ASSETS = Path(__file__).resolve().parent / "assets"


def _render_slide(lesson: Lesson, sentence: Sentence, active: bool) -> str:
    title = html.escape(f"Lesson {lesson.lesson}: {lesson.title}")
    orig = html.escape(f"({sentence.id}) {sentence.original}")
    expanded_line = ""
    if sentence.has_contraction:
        exp = html.escape(f"({sentence.id}) {sentence.expanded}")
        expanded_line = f'    <div class="line-expanded">{exp}</div>\n'
    analysis = render_token_groups(sentence)
    active_cls = "slide active" if active else "slide"
    return (
        f'<section class="{active_cls}">\n'
        f'  <div class="slide-body">\n'
        f'    <div class="line-title">{title}</div>\n'
        f'    <div class="line-original">{orig}</div>\n'
        f"{expanded_line}"
        f'    <div class="analysis">{analysis}</div>\n'
        f'  </div>\n'
        f"</section>\n"
    )


def export_lesson_html(lesson: Lesson, out_path: Path) -> None:
    css = (_ASSETS / "slide.css").read_text(encoding="utf-8")
    js = (_ASSETS / "slide.js").read_text(encoding="utf-8")
    slides = "".join(
        _render_slide(lesson, s, active=(i == 0))
        for i, s in enumerate(lesson.sentences)
    )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson {lesson.lesson}: {html.escape(lesson.title)}</title>
<style>{css}</style>
</head>
<body>
<div class="deck">
{slides}
</div>
<div class="hint">← → 翻页 · F11 全屏</div>
<script>{js}</script>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
