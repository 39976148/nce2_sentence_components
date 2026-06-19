from nce2_core.catalog import default_book


def test_nce2_only():
    book = default_book()
    assert book.id == 2
    assert book.lesson_count == 96
    assert "第二册" in book.txt_subdir
