from nce2_core.models import Token
from nce2_core.token_ops import apply_expanded, merge_tokens, split_token


def test_merge_tokens():
    tokens = [
        Token(text="Last", role=""),
        Token(text="week", role=""),
        Token(text="I", role="主语"),
    ]
    merged = merge_tokens(tokens, 0)
    assert len(merged) == 2
    assert merged[0].text == "Last week"
    assert merged[1].text == "I"


def test_split_token():
    tokens = [Token(text="Last week", role="时间状语"), Token(text="I", role="")]
    split = split_token(tokens, 0)
    assert len(split) == 3
    assert split[0].text == "Last"
    assert split[1].text == "week"


def test_split_no_space_unchanged():
    tokens = [Token(text="I", role="主语")]
    assert split_token(tokens, 0) == tokens


def test_apply_expanded():
    from nce2_core.models import Sentence

    s = Sentence(
        id=1,
        original="I'm late.",
        expanded="I am late.",
        has_contraction=True,
        tokens=[Token(text="I", role="主语")],
    )
    apply_expanded(s, "I am very late.")
    assert s.expanded == "I am very late."
    assert len(s.tokens) == 4
    assert s.tokens[0].text == "I"
