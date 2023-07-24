import pytest

from textual._document import Document

TEXT = """I must not fear.
Fear is the mind-killer.
I forgot the rest of the quote.
Sorry Will."""


@pytest.fixture
def document():
    document = Document()
    document.load_text(TEXT)
    return document


def test_delete_range_single_character(document):
    deleted_text = document.delete_range((0, 0), (0, 1))
    assert deleted_text == "I"
    assert document._lines == [
        " must not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_newline(document):
    """Testing deleting newline from right to left"""
    deleted_text = document.delete_range((1, 0), (0, 16))
    assert deleted_text == "\n"
    assert document._lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_character_end_of_document_newline(document):
    """Check deleting the newline character at the end of the document"""
    deleted_text = document.delete_range((1, 0), (0, 16))
    assert deleted_text == "\n"
    assert document._lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_multiple_characters_on_one_line(document):
    deleted_text = document.delete_range((0, 2), (0, 7))
    assert deleted_text == "must "
    assert document._lines == [
        "I not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_multiple_lines_partially_spanned(document):
    """Deleting a selection that partially spans the first and final lines of the selection."""
    deleted_text = document.delete_range((0, 2), (2, 2))
    assert deleted_text == "must not fear.\nFear is the mind-killer.\nI "
    assert document._lines == [
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_end_of_line(document):
    """Testing deleting newline from left to right"""
    deleted_text = document.delete_range((0, 16), (1, 0))
    assert deleted_text == "\n"
    assert document._lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_line_excluding_newline(document):
    """Delete from the start to the end of the line."""
    deleted_text = document.delete_range((2, 0), (2, 31))
    assert deleted_text == "I forgot the rest of the quote."
    assert document._lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "",
        "Sorry Will.",
    ]


def test_delete_range_single_line_including_newline(document):
    """Delete from the start of a line to the start of the line below."""
    deleted_text = document.delete_range((2, 0), (3, 0))
    assert deleted_text == "I forgot the rest of the quote.\n"
    assert document._lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "Sorry Will.",
    ]


def test_delete_range_single_character_start_of_document():
    """Check deletion of the first character in the document"""
    pass


def test_delete_range_single_character_end_of_document_newline():
    """Check deleting the newline character at the end of the document"""
    pass
