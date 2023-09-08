import pytest

from textual.widgets.text_area import Document, EditResult

TEXT = """I must not fear.
Fear is the mind-killer.
I forgot the rest of the quote.
Sorry Will."""


@pytest.fixture
def document():
    document = Document(TEXT)
    return document


def test_delete_single_character(document):
    replace_result = document.replace_range((0, 0), (0, 1), "")
    assert replace_result == EditResult(end_location=(0, 0), replaced_text="I")
    assert document.lines == [
        " must not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_single_newline(document):
    """Testing deleting newline from right to left"""
    replace_result = document.replace_range((1, 0), (0, 16), "")
    assert replace_result == EditResult(end_location=(0, 16), replaced_text="\n")
    assert document.lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_near_end_of_document(document):
    """Test deleting a range near the end of a document."""
    replace_result = document.replace_range((1, 0), (3, 11), "")
    assert replace_result == EditResult(
        end_location=(1, 0),
        replaced_text="Fear is the mind-killer.\n"
        "I forgot the rest of the quote.\n"
        "Sorry Will.",
    )
    assert document.lines == [
        "I must not fear.",
        "",
    ]


def test_delete_clearing_the_document(document):
    replace_result = document.replace_range((0, 0), (4, 0), "")
    assert replace_result == EditResult(
        end_location=(0, 0),
        replaced_text=TEXT,
    )
    assert document.lines == [""]


def test_delete_multiple_characters_on_one_line(document):
    replace_result = document.replace_range((0, 2), (0, 7), "")
    assert replace_result == EditResult(
        end_location=(0, 2),
        replaced_text="must ",
    )
    assert document.lines == [
        "I not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_multiple_lines_partially_spanned(document):
    """Deleting a selection that partially spans the first and final lines of the selection."""
    replace_result = document.replace_range((0, 2), (2, 2), "")
    assert replace_result == EditResult(
        end_location=(0, 2),
        replaced_text="must not fear.\nFear is the mind-killer.\nI ",
    )
    assert document.lines == [
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_end_of_line(document):
    """Testing deleting newline from left to right"""
    replace_result = document.replace_range((0, 16), (1, 0), "")
    assert replace_result == EditResult(
        end_location=(0, 16),
        replaced_text="\n",
    )
    assert document.lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_single_line_excluding_newline(document):
    """Delete from the start to the end of the line."""
    replace_result = document.replace_range((2, 0), (2, 31), "")
    assert replace_result == EditResult(
        end_location=(2, 0),
        replaced_text="I forgot the rest of the quote.",
    )
    assert document.lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "",
        "Sorry Will.",
    ]


def test_delete_single_line_including_newline(document):
    """Delete from the start of a line to the start of the line below."""
    replace_result = document.replace_range((2, 0), (3, 0), "")
    assert replace_result == EditResult(
        end_location=(2, 0),
        replaced_text="I forgot the rest of the quote.\n",
    )
    assert document.lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "Sorry Will.",
    ]


TEXT_NEWLINE_EOF = """\
I must not fear.
Fear is the mind-killer.
"""


def test_delete_end_of_file_newline():
    document = Document(TEXT_NEWLINE_EOF)
    replace_result = document.replace_range((2, 0), (1, 24), "")
    assert replace_result == EditResult(end_location=(1, 24), replaced_text="\n")
    assert document.lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
    ]
