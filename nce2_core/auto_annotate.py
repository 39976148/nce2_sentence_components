"""Rule-based sentence component annotation (offline, editable in GUI)."""

from __future__ import annotations

import re

from nce2_core.models import Sentence, Token
from nce2_core.phrase_merge import merge_phrase_tokens, _norm, _PREP, _SUBJECT, _CONJ, _TIME_HEAD

_LINKING = {"am", "is", "are", "was", "were", "be", "been", "being"}
_AUX = {
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must",
}
_DETERMINERS = {"a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "her", "our", "their"}
_COMMON_VERBS = {
    "went", "go", "goes", "going", "gone", "come", "came", "get", "got",
    "had", "have", "has", "said", "say", "says", "looked", "look", "looks",
    "turned", "turn", "enjoy", "enjoyed", "hear", "heard", "bear", "bore",
    "talk", "talked", "talking", "sit", "sat", "sitting", "pay", "paid",
    "make", "made", "take", "took", "give", "gave", "know", "knew",
    "think", "thought", "see", "saw", "want", "wanted", "need", "needed",
    "like", "liked", "live", "lived", "work", "worked", "play", "played",
    "call", "called", "ask", "asked", "tell", "told", "put", "keep", "kept",
    "let", "leave", "left", "become", "became", "find", "found", "bring",
    "brought", "begin", "began", "seem", "seemed", "help", "helped",
    "show", "showed", "shown", "try", "tried", "use", "used", "move", "moved",
}
_LOC_PREP = {"to", "in", "at", "on", "behind", "into", "from", "near", "over", "under", "around", "round"}


def _first_word(text: str) -> str:
    return _norm(text.split()[0]) if text.split() else ""


def _is_verb(word: str) -> bool:
    w = _norm(word)
    if not w:
        return False
    if w in _LINKING or w in _AUX or w in _COMMON_VERBS:
        return True
    if len(w) > 3 and w.endswith("ed"):
        return True
    if len(w) > 4 and w.endswith("ing"):
        return True
    return False


def _is_time_phrase(text: str) -> bool:
    parts = text.split()
    if not parts:
        return False
    w0 = _norm(parts[0])
    if w0 in {"last", "next", "this", "each", "every", "one", "some"}:
        return True
    if w0 in _TIME_HEAD and len(parts) >= 2:
        return True
    if w0 == "in" and len(parts) >= 3 and _norm(parts[1]) == "the":
        return True
    return False


def _is_loc_prep_phrase(text: str) -> bool:
    return _first_word(text) in _LOC_PREP and " " in text


def auto_annotate_tokens(tokens: list[Token]) -> list[Token]:
    if not tokens:
        return tokens

    tokens = merge_phrase_tokens(tokens)
    n = len(tokens)
    roles = [""] * n
    i = 0

    # Leading time phrase
    if i < n and _is_time_phrase(tokens[i].text):
        roles[i] = "时间状语"
        i += 1

    # Subject
    if i < n:
        w = _first_word(tokens[i].text)
        if w in _SUBJECT or (w in _DETERMINERS and " " not in tokens[i].text):
            roles[i] = "主语"
            i += 1
        elif w in _DETERMINERS or w not in _PREP:
            roles[i] = "主语"
            i += 1

    # Predicate
    if i < n and _is_verb(tokens[i].text):
        roles[i] = "系动词" if _first_word(tokens[i].text) in _LINKING else "谓语"
        i += 1

    if i < n and _first_word(tokens[i].text) == "not":
        roles[i] = "状语"
        i += 1

    while i < n:
        text = tokens[i].text
        w = _first_word(text)

        if w in _CONJ:
            roles[i] = "连词"
        elif _is_loc_prep_phrase(text) or (w in _PREP and len(text.split()) > 1):
            roles[i] = "地点状语" if w in _LOC_PREP else "介词短语"
        elif w in _PREP:
            roles[i] = "介词短语"
        elif w in {"very", "so", "too", "quite", "really", "always", "often", "never", "loudly", "angrily", "rudely", "quickly", "slowly"}:
            roles[i] = "状语"
        elif w in _DETERMINERS or (len(text.split()) > 1 and not _is_verb(text)):
            roles[i] = "表语" if any(r == "系动词" for r in roles) else "宾语"
        elif _is_verb(text):
            roles[i] = "谓语"
        else:
            roles[i] = "表语" if any(r == "系动词" for r in roles) else "宾语"
        i += 1

    return [Token(text=t.text, role=roles[idx]) for idx, t in enumerate(tokens)]


def auto_annotate_sentence(sentence: Sentence) -> Sentence:
    sentence.tokens = auto_annotate_tokens(sentence.tokens)
    return sentence


def auto_annotate_lesson(lesson) -> None:
    for s in lesson.sentences:
        auto_annotate_sentence(s)
