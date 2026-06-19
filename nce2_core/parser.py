from __future__ import annotations

from pathlib import Path


def _is_english_line(line: str) -> bool:
    if len(line) < 15:
        return False
    alpha = sum(c.isascii() and c.isalpha() for c in line)
    return alpha > len(line) * 0.45


def extract_english_lines(raw: str) -> list[str]:
    lines: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if "New words and expressions" in s:
            break
        if _is_english_line(s):
            lines.append(s)
    return lines


def extract_lesson_body(path: Path) -> str:
    data = path.read_bytes().decode("latin-1")
    lines = extract_english_lines(data)
    if not lines:
        return ""

    while lines and lines[0].rstrip().endswith("?"):
        lines.pop(0)

    return " ".join(lines)
