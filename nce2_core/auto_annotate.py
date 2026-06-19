"""Rule-based sentence component annotation (offline, editable in GUI)."""

from __future__ import annotations

import re

from nce2_core.models import Sentence, Token

_SUBJECT = {"i", "he", "she", "we", "they", "you", "it"}
_LINKING = {"am", "is", "are", "was", "were", "be", "been", "being"}
_AUX = {
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must",
}
_PREP = {
    "to", "in", "on", "at", "from", "with", "by", "for", "of", "into",
    "behind", "about", "over", "under", "through", "after", "before",
    "between", "among", "off", "up", "down", "near", "round", "around",
}
_CONJ = {"and", "or", "but", "so", "because", "when", "if", "that", "as", "while"}
_TIME_HEAD = {
    "last", "in", "at", "on", "every", "sometimes", "one", "this", "that",
    "when", "after", "before", "during", "soon", "later", "then", "now",
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


def _norm(word: str) -> str:
    return re.sub(r"[^a-zA-Z']", "", word).lower()


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


def _mark_range(roles: list[str], start: int, end: int, role: str) -> None:
    for i in range(start, min(end, len(roles))):
        if not roles[i]:
            roles[i] = role


def auto_annotate_tokens(tokens: list[Token]) -> list[Token]:
    if not tokens:
        return tokens

    roles = [""] * len(tokens)
    n = len(tokens)
    i = 0

    # Leading time / adverbial phrases
    if _norm(tokens[0].text) in _TIME_HEAD:
        j = 1
        while j < n and _norm(tokens[j].text) not in _SUBJECT and not _is_verb(tokens[j].text):
            if _norm(tokens[j].text) in {"week", "year", "day", "month", "morning", "evening", "end", "time", "summer", "winter", "spring", "autumn", "o'clock"}:
                j += 1
                break
            j += 1
            if j - i >= 4:
                break
        _mark_range(roles, i, j, "时间状语")
        i = j

    if i < n and _norm(tokens[i].text) == "in" and i + 1 < n and _norm(tokens[i + 1].text) == "the":
        j = i + 1
        while j < n and _norm(tokens[j].text) not in _SUBJECT and not _is_verb(tokens[j].text):
            j += 1
            if j - i >= 5:
                break
        _mark_range(roles, i, j, "时间状语")
        i = j

    # Subject
    subj_start = i
    if i < n and _norm(tokens[i].text) in _SUBJECT:
        roles[i] = "主语"
        i += 1
    elif i < n and _norm(tokens[i].text) in _DETERMINERS:
        j = i + 1
        while j < n and not _is_verb(tokens[j].text):
            j += 1
            if j - i >= 6:
                break
        _mark_range(roles, i, j, "主语")
        i = j
    elif i < n and _norm(tokens[i].text) not in _PREP:
        roles[i] = "主语"
        i += 1

    # Predicate / linking verb
    if i < n and _is_verb(tokens[i].text):
        roles[i] = "系动词" if _norm(tokens[i].text) in _LINKING else "谓语"
        i += 1

    # not
    if i < n and _norm(tokens[i].text) == "not":
        roles[i] = "状语"
        i += 1

    # Remainder: prep phrases, objects, complements, attributes
    while i < n:
        w = _norm(tokens[i].text)
        if w in _CONJ:
            roles[i] = "连词"
            i += 1
            continue
        if w in _PREP or (w == "to" and i + 1 < n):
            j = i + 1
            while j < n and _norm(tokens[j].text) not in _CONJ:
                if j > i + 1 and _is_verb(tokens[j].text) and _norm(tokens[j].text) not in {"be"}:
                    break
                j += 1
                if j - i >= 6:
                    break
            prep_role = "地点状语" if w in {"in", "at", "on", "behind", "to", "into", "near", "from"} else "介词短语"
            _mark_range(roles, i, j, prep_role)
            i = j
            continue
        if w in {"very", "so", "too", "quite", "really", "always", "often", "never", "loudly", "angrily", "rudely", "quickly", "slowly"}:
            roles[i] = "状语"
            i += 1
            continue
        if w in {"a", "an", "the", "this", "that", "my", "your", "his", "her", "its", "our", "their"}:
            j = i + 1
            while j < n and not _is_verb(tokens[j].text) and _norm(tokens[j].text) not in _CONJ:
                j += 1
                if j - i >= 5:
                    break
            # After linking verb -> 表语; else 宾语
            pred_idx = subj_start
            while pred_idx < n and roles[pred_idx] not in {"谓语", "系动词"}:
                pred_idx += 1
            is_pred = pred_idx < n and roles[pred_idx] == "系动词"
            _mark_range(roles, i, j, "表语" if is_pred else "宾语")
            i = j
            continue
        if _is_verb(tokens[i].text):
            roles[i] = "谓语"
            i += 1
            continue
        if not roles[i]:
            roles[i] = "表语" if any(r == "系动词" for r in roles) else "宾语"
        i += 1

    return [Token(text=t.text, role=roles[idx]) for idx, t in enumerate(tokens)]


def auto_annotate_sentence(sentence: Sentence) -> Sentence:
    sentence.tokens = auto_annotate_tokens(sentence.tokens)
    return sentence


def auto_annotate_lesson(lesson) -> None:
    for s in lesson.sentences:
        auto_annotate_sentence(s)
