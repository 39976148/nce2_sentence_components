from __future__ import annotations

from nce2_core.contraction import sentence_has_contraction
from nce2_core.models import Sentence, Token
from nce2_core.tokenizer import tokenize_expanded


def merge_tokens(tokens: list[Token], index: int) -> list[Token]:
    if index < 0 or index >= len(tokens) - 1:
        return list(tokens)
    merged = Token(
        text=f"{tokens[index].text} {tokens[index + 1].text}",
        role=tokens[index].role or tokens[index + 1].role,
    )
    result = tokens[:index] + [merged] + tokens[index + 2 :]
    return result


def split_token(tokens: list[Token], index: int) -> list[Token]:
    if index < 0 or index >= len(tokens):
        return list(tokens)
    text = tokens[index].text
    space = text.find(" ")
    if space <= 0 or space >= len(text) - 1:
        return list(tokens)
    left = Token(text=text[:space], role=tokens[index].role)
    right = Token(text=text[space + 1 :], role="")
    return tokens[:index] + [left, right] + tokens[index + 1 :]


def apply_expanded(sentence: Sentence, expanded: str) -> Sentence:
    expanded = expanded.strip()
    sentence.expanded = expanded
    sentence.has_contraction = sentence_has_contraction(sentence.original, expanded)
    sentence.tokens = tokenize_expanded(expanded)
    return sentence


def tokens_from_table_rows(rows: list[tuple[str, str]]) -> list[Token]:
    return [Token(text=text.strip(), role=role) for text, role in rows if text.strip()]
