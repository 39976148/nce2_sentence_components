from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Token:
    text: str
    role: str = ""


@dataclass
class Sentence:
    id: int
    original: str
    expanded: str
    has_contraction: bool
    tokens: list[Token] = field(default_factory=list)


@dataclass
class Lesson:
    book: int
    lesson: int
    title: str
    sentences: list[Sentence] = field(default_factory=list)


def token_to_dict(token: Token) -> dict[str, Any]:
    return {"text": token.text, "role": token.role}


def token_from_dict(data: dict[str, Any]) -> Token:
    return Token(text=data["text"], role=data.get("role", ""))


def sentence_to_dict(sentence: Sentence) -> dict[str, Any]:
    return {
        "id": sentence.id,
        "original": sentence.original,
        "expanded": sentence.expanded,
        "has_contraction": sentence.has_contraction,
        "tokens": [token_to_dict(t) for t in sentence.tokens],
    }


def sentence_from_dict(data: dict[str, Any]) -> Sentence:
    return Sentence(
        id=data["id"],
        original=data["original"],
        expanded=data["expanded"],
        has_contraction=data["has_contraction"],
        tokens=[token_from_dict(t) for t in data.get("tokens", [])],
    )


def lesson_to_dict(lesson: Lesson) -> dict[str, Any]:
    return {
        "book": lesson.book,
        "lesson": lesson.lesson,
        "title": lesson.title,
        "sentences": [sentence_to_dict(s) for s in lesson.sentences],
    }


def lesson_from_dict(data: dict[str, Any]) -> Lesson:
    return Lesson(
        book=data["book"],
        lesson=data["lesson"],
        title=data["title"],
        sentences=[sentence_from_dict(s) for s in data.get("sentences", [])],
    )
