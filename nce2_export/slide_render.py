from __future__ import annotations

import html

from nce2_core.models import Sentence


def render_token_groups(sentence: Sentence) -> str:
    parts: list[str] = []
    for token in sentence.tokens:
        text = html.escape(token.text)
        role = html.escape(token.role) if token.role else "—"
        parts.append(
            f'<span class="token-group">'
            f'<span class="token-word">{text}</span>'
            f'<div class="underline"></div>'
            f'<div class="role-label">{role}</div>'
            f"</span>"
        )
    return "".join(parts)
