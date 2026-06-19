from nce2_core.catalog import default_book, enabled_books, get_book


def test_default_book_is_nce2():
    book = default_book()
    assert book.id == 2
    assert book.enabled is True
    assert book.lesson_count == 96


def test_other_books_disabled():
    assert get_book(1).enabled is False
    assert get_book(3).enabled is False
    assert len(enabled_books()) == 1
