from nce2_core.models import Token
from nce2_core.phrase_merge import merge_phrase_tokens
from nce2_core.auto_annotate import auto_annotate_tokens


def test_last_week_theatre_sentence():
    words = [
        Token(text="Last", role=""),
        Token(text="week", role=""),
        Token(text="I", role=""),
        Token(text="went", role=""),
        Token(text="to", role=""),
        Token(text="the", role=""),
        Token(text="theatre.", role=""),
    ]
    result = auto_annotate_tokens(words)
    assert len(result) == 4
    assert result[0].text == "Last week"
    assert result[0].role == "时间状语"
    assert result[1].text == "I"
    assert result[1].role == "主语"
    assert result[2].text == "went"
    assert result[2].role == "谓语"
    assert result[3].text == "to the theatre."
    assert result[3].role == "地点状语"


def test_merge_phrase_only():
    words = [
        Token(text="Last", role=""),
        Token(text="week", role=""),
        Token(text="I", role=""),
        Token(text="went", role=""),
        Token(text="to", role=""),
        Token(text="the", role=""),
        Token(text="theatre.", role=""),
    ]
    merged = merge_phrase_tokens(words)
    assert [t.text for t in merged] == ["Last week", "I", "went", "to the theatre."]
