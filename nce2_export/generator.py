from __future__ import annotations

import html
from pathlib import Path

from nce2_core.models import Lesson, Sentence

_ASSETS = Path(__file__).resolve().parent / "assets"


def _render_token_row(sentence: Sentence) -> str:
    parts: list[str] = []
    for token in sentence.tokens:
        text = html.escape(token.text)
        role = html.escape(token.role) if token.role else "—"
        width = max(len(token.text), 2)
        parts.append(
            f'<span class="token-group">'
            f'<span class="token-text">{text}</span>'
            f'<div class="underline" style="width:{width}ch"></div>'
            f'<div class="role-label">{role}</div>'
            f"</span>"
        )
    return "".join(parts)


def _render_slide(lesson: Lesson, sentence: Sentence, active: bool) -> str:
    title = html.escape(f"Lesson {lesson.lesson}: {lesson.title}")
    orig = html.escape(f"({sentence.id}) {sentence.original}")
    expanded_line = ""
    if sentence.has_contraction:
        exp = html.escape(f"({sentence.id}) {sentence.expanded}")
        expanded_line = f'  <div class="line-expanded">{exp}</div>\n'
    analysis = _render_token_row(sentence)
    active_cls = "slide active" if active else "slide"
    return (
        f'<section class="{active_cls}">\n'
        f'  <div class="line-title">{title}</div>\n'
        f'  <div class="line-original">{orig}</div>\n'
        f"{expanded_line}"
        f'  <div class="analysis">{analysis}</div>\n'
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
