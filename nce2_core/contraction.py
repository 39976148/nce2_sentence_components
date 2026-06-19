from __future__ import annotations

import re

_REPLACEMENTS: list[tuple[re.Pattern[str], str | re.Pattern[str]]] = []

# Built at module load — order matters: longer patterns first
def _build_replacements() -> list[tuple[re.Pattern[str], str]]:
    specs: list[tuple[str, str]] = [
        (r"\bwon't\b", "will not"),
        (r"\bcan't\b", "can not"),
        (r"\bshan't\b", "shall not"),
        (r"\bn't\b", " not"),
        (r"\bI'm\b", "I am"),
        (r"\bI've\b", "I have"),
        (r"\bI'll\b", "I will"),
        (r"\bI'd\b", "I would"),
        (r"\byou're\b", "you are"),
        (r"\bYou're\b", "You are"),
        (r"\bwe're\b", "we are"),
        (r"\bthey're\b", "they are"),
        (r"\bhe's\b", "he is"),
        (r"\bshe's\b", "she is"),
        (r"\bit's\b", "it is"),
        (r"\bIt's\b", "It is"),
        (r"\bthat's\b", "that is"),
        (r"\bwhat's\b", "what is"),
        (r"\bthere's\b", "there is"),
        (r"\bhere's\b", "here is"),
    ]
    patterns = [(re.compile(p, re.I if p[0] != "I" else 0), r) for p, r in specs]
    patterns.extend(
        [
            (re.compile(r"\b(\w+)'re\b", re.I), r"\1 are"),
            (re.compile(r"\b(\w+)'ve\b", re.I), r"\1 have"),
            (re.compile(r"\b(\w+)'ll\b", re.I), r"\1 will"),
            (re.compile(r"\b(\w+)'d\b", re.I), r"\1 would"),
            (re.compile(r"\b(\w+)'m\b", re.I), r"\1 am"),
            (re.compile(r"\b(\w+)n't\b", re.I), r"\1 not"),
        ]
    )
    return patterns


_REPLACEMENTS = _build_replacements()


def expand_contractions(text: str) -> str:
    result = text
    for pattern, repl in _REPLACEMENTS:
        result = pattern.sub(repl, result)
    return result


def sentence_has_contraction(original: str, expanded: str) -> bool:
    return original != expanded
