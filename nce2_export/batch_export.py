from __future__ import annotations

import html
from pathlib import Path

from nce2_core.models import Lesson
from nce2_core.lesson_io import load_lesson
from nce2_export.generator import export_lesson_html

_INDEX_CSS = """
body { font-family: "Segoe UI", sans-serif; background: #1a1a2e; color: #eee; padding: 2rem; }
h1 { color: #a0c4ff; }
a { color: #06d6a0; text-decoration: none; }
a:hover { text-decoration: underline; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.5rem; }
.item { padding: 0.4rem 0; }
"""


def export_all_lessons(
    lessons_dir: Path,
    output_dir: Path,
    lesson_nums: list[int] | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    nums = lesson_nums or sorted(
        int(p.stem) for p in lessons_dir.glob("*.json") if p.stem.isdigit()
    )
    links: list[str] = []
    for n in nums:
        json_path = lessons_dir / f"{n:02d}.json"
        if not json_path.exists():
            continue
        lesson = load_lesson(json_path)
        html_path = output_dir / f"lesson_{n:02d}.html"
        export_lesson_html(lesson, html_path)
        links.append(
            f'<div class="item"><a href="{html.escape(html_path.name)}">'
            f"Lesson {n:02d}: {html.escape(lesson.title)}</a></div>"
        )

    index_path = output_dir / "index.html"
    index_path.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>NCE2 Slides Index</title>
<style>{_INDEX_CSS}</style>
</head>
<body>
<h1>NCE2 幻灯片目录</h1>
<p>共 {len(links)} 课 · 点击打开单课演示（← → 翻页，F11 全屏）</p>
<div class="grid">
{"".join(links)}
</div>
</body>
</html>
""",
        encoding="utf-8",
    )
    return index_path
