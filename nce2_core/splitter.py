from __future__ import annotations

import re

_ABBREV = r"Mr|Mrs|Ms|Dr|St|Prof|etc|e\.g|i\.e|a\.m|p\.m|No|Vol|Fig"
_ABBREV_DOT = re.compile(rf"\b(?:{_ABBREV})\.", re.I)
_DECIMAL = re.compile(r"\d+\.\d+")


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []

    protected = text
    placeholders: dict[str, str] = {}

    def _protect(match: re.Match[str]) -> str:
        key = f"§{len(placeholders)}§"
        placeholders[key] = match.group(0)
        return key

    protected = _DECIMAL.sub(_protect, protected)
    protected = _ABBREV_DOT.sub(_protect, protected)

    parts = re.split(r"(?<=[.!?])\s+", protected)
    sentences: list[str] = []
    for part in parts:
        restored = part
        for key, val in placeholders.items():
            restored = restored.replace(key, val)
        restored = restored.strip()
        if restored:
            sentences.append(restored)
    return sentences
