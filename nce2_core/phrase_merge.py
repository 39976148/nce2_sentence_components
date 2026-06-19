"""Merge word tokens into phrase-level tokens for underline display."""

from __future__ import annotations

import re

from nce2_core.models import Token

_TIME_HEAD = {
    "last", "next", "this", "that", "every", "each", "one", "some",
    "in", "at", "on", "during", "after", "before", "when", "while",
    "soon", "later", "then", "now", "today", "tomorrow", "yesterday",
}
_TIME_UNITS = {
    "week", "weeks", "year", "years", "month", "months", "day", "days",
    "morning", "evening", "afternoon", "night", "time", "summer", "winter",
    "spring", "autumn", "minute", "minutes", "hour", "hours", "moment",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
}
_PREP = {
    "to", "in", "on", "at", "from", "with", "by", "for", "of", "into",
    "behind", "about", "over", "under", "through", "after", "before",
    "between", "among", "off", "up", "down", "near", "round", "around",
}
_DETERMINERS = {"a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "her", "our", "their"}
_SUBJECT = {"i", "he", "she", "we", "they", "you", "it"}
_CONJ = {"and", "or", "but", "so", "because", "when", "if", "that", "as", "while"}
_IN_THE_NOUN = {"end", "morning", "evening", "afternoon", "night", "day", "week", "world", "country"}


def _norm(word: str) -> str:
    return re.sub(r"[^a-zA-Z']", "", word).lower()


def _join(tokens: list[Token], start: int, end: int) -> str:
    return " ".join(tokens[i].text for i in range(start, end))


def merge_phrase_tokens(tokens: list[Token]) -> list[Token]:
    """Merge e.g. Last+week -> 'Last week', to+the+theatre -> 'to the theatre.'"""
    if not tokens:
        return tokens

    merged: list[Token] = []
    i = 0
    n = len(tokens)

    while i < n:
        w0 = _norm(tokens[i].text)

        # Last week / Next year / One day
        if w0 in {"last", "next", "this", "each", "every", "one", "some"} and i + 1 < n:
            w1 = _norm(tokens[i + 1].text)
            if w1 in _TIME_UNITS:
                merged.append(Token(text=_join(tokens, i, i + 2), role=""))
                i += 2
                continue

        # In the end / In the morning
        if (
            w0 == "in"
            and i + 2 < n
            and _norm(tokens[i + 1].text) == "the"
            and _norm(tokens[i + 2].text) in _IN_THE_NOUN
        ):
            merged.append(Token(text=_join(tokens, i, i + 3), role=""))
            i += 3
            continue

        # Leading time head + unit (At last, On Monday)
        if w0 in {"at", "on", "in"} and i + 1 < n:
            w1 = _norm(tokens[i + 1].text)
            if w1 in _TIME_UNITS or w1 in {"last", "first", "once"}:
                merged.append(Token(text=_join(tokens, i, i + 2), role=""))
                i += 2
                continue

        # Prepositional phrase: to the theatre / behind me / in Italy
        if w0 in _PREP:
            j = i + 1
            if j < n and _norm(tokens[j].text) in _DETERMINERS:
                j += 1
            while j < n:
                wj = _norm(tokens[j].text)
                if wj in _CONJ:
                    break
                if wj in _SUBJECT and j == i + 1:
                    break
                if wj in _PREP and j > i + 1:
                    break
                j += 1
            if j > i + 1:
                merged.append(Token(text=_join(tokens, i, j), role=""))
                i = j
                continue

        merged.append(Token(text=tokens[i].text, role=""))
        i += 1

    return merged
