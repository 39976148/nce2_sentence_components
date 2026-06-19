from __future__ import annotations

from nce2_core.contraction import expand_contractions, sentence_has_contraction
from nce2_core.models import Lesson, Sentence
from nce2_core.tokenizer import tokenize_expanded


def renumber_lesson(lesson: Lesson) -> None:
    for idx, sentence in enumerate(lesson.sentences, start=1):
        sentence.id = idx


def _sentence_from_text(text: str) -> Sentence:
    text = text.strip()
    expanded = expand_contractions(text)
    return Sentence(
        id=0,
        original=text,
        expanded=expanded,
        has_contraction=sentence_has_contraction(text, expanded),
        tokens=tokenize_expanded(expanded),
    )


def split_sentence(lesson: Lesson, index: int, part1: str, part2: str) -> None:
    if index < 0 or index >= len(lesson.sentences):
        raise IndexError("sentence index out of range")
    p1, p2 = part1.strip(), part2.strip()
    if not p1 or not p2:
        raise ValueError("拆分后的两部分都不能为空")
    s1 = _sentence_from_text(p1)
    s2 = _sentence_from_text(p2)
    lesson.sentences[index : index + 1] = [s1, s2]
    renumber_lesson(lesson)


def merge_with_next(lesson: Lesson, index: int) -> None:
    if index < 0 or index >= len(lesson.sentences) - 1:
        raise IndexError("无法合并：已是最后一句或索引无效")
    a = lesson.sentences[index].original.rstrip()
    b = lesson.sentences[index + 1].original.lstrip()
    merged = _sentence_from_text(f"{a} {b}")
    lesson.sentences[index : index + 2] = [merged]
    renumber_lesson(lesson)


def update_sentence_original(sentence: Sentence, original: str) -> Sentence:
    original = original.strip()
    expanded = expand_contractions(original)
    sentence.original = original
    sentence.expanded = expanded
    sentence.has_contraction = sentence_has_contraction(original, expanded)
    sentence.tokens = tokenize_expanded(expanded)
    return sentence
