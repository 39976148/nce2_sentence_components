from nce2_core.splitter import split_sentences


def test_basic_periods():
    text = "I turned round. I looked at the man."
    assert split_sentences(text) == [
        "I turned round.",
        "I looked at the man.",
    ]


def test_abbreviation_mr():
    text = "Mr. Smith arrived. He sat down."
    assert split_sentences(text) == ["Mr. Smith arrived.", "He sat down."]


def test_quoted_dialogue():
    text = (
        "'It's none of your business,' the young man said rudely. "
        "'This is a private conversation!'"
    )
    result = split_sentences(text)
    assert len(result) == 2
    assert result[0].startswith("'It's none")
    assert result[1] == "'This is a private conversation!'"
