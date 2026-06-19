import json

from nce2_core.ai_annotate import parse_annotation_response
from nce2_core.models import Sentence, Token


def test_parse_annotation_response():
    sentence = Sentence(
        id=1,
        original="I'm late.",
        expanded="I am late.",
        has_contraction=True,
        tokens=[Token(text="I", role=""), Token(text="am", role=""), Token(text="late.", role="")],
    )
    raw = json.dumps(
        {
            "tokens": [
                {"text": "I", "role": "主语"},
                {"text": "am", "role": "系动词"},
                {"text": "late.", "role": "表语"},
            ]
        }
    )
    tokens = parse_annotation_response(raw, sentence)
    assert [t.role for t in tokens] == ["主语", "系动词", "表语"]


def test_parse_merged_tokens():
    sentence = Sentence(
        id=1,
        original="Last week I went.",
        expanded="Last week I went.",
        has_contraction=False,
        tokens=[
            Token(text="Last", role=""),
            Token(text="week", role=""),
            Token(text="I", role=""),
            Token(text="went.", role=""),
        ],
    )
    raw = json.dumps(
        {
            "tokens": [
                {"text": "Last week", "role": "时间状语"},
                {"text": "I", "role": "主语"},
                {"text": "went.", "role": "谓语"},
            ]
        }
    )
    tokens = parse_annotation_response(raw, sentence)
    assert len(tokens) == 3
    assert tokens[0].text == "Last week"


def test_parse_rejects_mismatch():
    sentence = Sentence(
        id=1,
        original="Hi.",
        expanded="I am late.",
        has_contraction=True,
        tokens=[Token(text="I", role=""), Token(text="am", role=""), Token(text="late.", role="")],
    )
    raw = json.dumps({"tokens": [{"text": "I", "role": "主语"}, {"text": "am", "role": "系动词"}]})
    try:
        parse_annotation_response(raw, sentence)
        assert False, "expected ValueError"
    except ValueError:
        pass
