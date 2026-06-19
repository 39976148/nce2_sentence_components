from __future__ import annotations

from nce2_core.models import Token


def tokenize_expanded(expanded: str) -> list[Token]:
    words = expanded.split()
    if not words:
        return []
    return [Token(text=w, role="") for w in words]
