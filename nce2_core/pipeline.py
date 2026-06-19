from __future__ import annotations

from pathlib import Path

from nce2_core.auto_annotate import auto_annotate_sentence
from nce2_core.contraction import expand_contractions, sentence_has_contraction
from nce2_core.models import Lesson, Sentence
from nce2_core.parser import extract_lesson_body
from nce2_core.splitter import split_sentences
from nce2_core.tokenizer import tokenize_expanded


def build_lesson_from_txt(path: Path, lesson_num: int, title: str) -> Lesson:
    body = extract_lesson_body(path)
    raw_sentences = split_sentences(body)
    sentences: list[Sentence] = []
    for idx, original in enumerate(raw_sentences, start=1):
        expanded = expand_contractions(original)
        has_c = sentence_has_contraction(original, expanded)
        sentences.append(
            Sentence(
                id=idx,
                original=original,
                expanded=expanded,
                has_contraction=has_c,
                tokens=tokenize_expanded(expanded),
            )
        )
    for s in sentences:
        auto_annotate_sentence(s)
    return Lesson(book=2, lesson=lesson_num, title=title, sentences=sentences)
