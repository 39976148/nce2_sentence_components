from nce2_core.contraction import expand_contractions, sentence_has_contraction


def test_im_expansion():
    assert expand_contractions("I'm late.") == "I am late."


def test_no_contraction():
    original = "Last week I went to the theatre."
    expanded = expand_contractions(original)
    assert expanded == original
    assert sentence_has_contraction(original, expanded) is False


def test_cant_and_wont():
    assert expand_contractions("I can't hear a word!") == "I can not hear a word!"
    assert expand_contractions("won't") == "will not"


def test_youd():
    assert expand_contractions("You'd better go.") == "You would better go."
