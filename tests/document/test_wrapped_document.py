import pytest

from textual.document._document import Document
from textual.document._wrapped_document import WrappedDocument
from textual.geometry import Offset

SIMPLE_TEXT = "123 4567\n12345\n123456789\n"


def test_wrap():
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    assert wrapped_document.lines == [
        ["123 ", "4567"],
        ["1234", "5"],
        ["1234", "5678", "9"],
        [""],
    ]


def test_wrap_empty_document():
    document = Document("")
    wrapped_document = WrappedDocument(document, width=4)

    assert wrapped_document.lines == [[""]]


def test_wrap_width_zero_no_wrapping():
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=0)

    assert wrapped_document.lines == [
        ["123 4567"],
        ["12345"],
        ["123456789"],
        [""],
    ]


def test_refresh_range():
    """The post-edit content is not wrapped."""
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    start_location = (1, 0)
    old_end_location = (3, 0)

    edit_result = document.replace_range(start_location, old_end_location, "123")

    # Inform the wrapped document about the range impacted by the edit
    wrapped_document.wrap_range(
        start_location,
        old_end_location,
        edit_result.end_location,
    )

    # Now confirm the resulting wrapped version is as we would expect
    assert wrapped_document.lines == [["123 ", "4567"], ["123"]]


def test_refresh_range_new_text_wrapped():
    """The post-edit content itself must be wrapped."""
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    start_location = (1, 0)
    old_end_location = (3, 0)

    edit_result = document.replace_range(
        start_location, old_end_location, "12 34567 8901"
    )

    # Inform the wrapped document about the range impacted by the edit
    wrapped_document.wrap_range(
        start_location, old_end_location, edit_result.end_location
    )

    # Now confirm the resulting wrapped version is as we would expect
    assert wrapped_document.lines == [
        ["123 ", "4567"],
        ["12 ", "3456", "7 ", "8901"],
    ]


def test_refresh_range_wrapping_at_previously_unavailable_range():
    """When we insert new content at the end of the document, ensure it wraps correctly."""
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    edit_result = document.replace_range((3, 0), (3, 0), "012 3456\n78 90123\n45")
    wrapped_document.wrap_range((3, 0), (3, 0), edit_result.end_location)

    assert wrapped_document.lines == [
        ["123 ", "4567"],
        ["1234", "5"],
        ["1234", "5678", "9"],
        ["012 ", "3456"],
        ["78 ", "9012", "3"],
        ["45"],
    ]


def test_refresh_range_wrapping_disabled_previously_unavailable_range():
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=0)  # wrapping disabled

    edit_result = document.replace_range((3, 0), (3, 0), "012 3456\n78 90123\n45")
    wrapped_document.wrap_range((3, 0), (3, 0), edit_result.end_location)

    assert wrapped_document.lines == [
        ["123 4567"],
        ["12345"],
        ["123456789"],
        ["012 3456"],
        ["78 90123"],
        ["45"],
    ]


@pytest.mark.parametrize(
    "offset,location",  # location is (row, column)
    [
        (Offset(x=0, y=0), (0, 0)),
        (Offset(x=1, y=0), (0, 1)),
        (Offset(x=2, y=1), (0, 6)),
        (Offset(x=0, y=3), (1, 4)),
        (Offset(x=1, y=3), (1, 5)),
        (Offset(x=200, y=3), (1, 5)),
        (Offset(x=0, y=6), (2, 8)),
        (Offset(x=0, y=7), (3, 0)),  # Clicking on the final, empty line
        (Offset(x=0, y=1000), (3, 0)),
    ],
)
def test_offset_to_location_wrapping_enabled(offset, location):
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    assert wrapped_document.offset_to_location(offset) == location


@pytest.mark.parametrize(
    "offset,location",  # location is (row, column)
    [
        (Offset(x=0, y=0), (0, 0)),
        (Offset(x=1, y=0), (0, 1)),
        (Offset(x=2, y=1), (1, 2)),
        (Offset(x=0, y=3), (3, 0)),
        (Offset(x=1, y=3), (3, 0)),
        (Offset(x=200, y=3), (3, 0)),
        (Offset(x=200, y=200), (3, 0)),  # Clicking below the document
    ],
)
def test_offset_to_location_wrapping_disabled(offset, location):
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=0)

    assert wrapped_document.offset_to_location(offset) == location


@pytest.mark.parametrize(
    "offset,location",
    [
        [Offset(-3, 0), (0, 0)],
        [Offset(0, -10), (0, 0)],
    ],
)
def test_offset_to_location_invalid_offset_clamps_to_valid_offset(offset, location):
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    result = wrapped_document.offset_to_location(offset)
    assert result == location


@pytest.mark.parametrize(
    "line_index, offsets",
    [
        (0, [4]),
        (1, [4]),
        (2, [4, 8]),
    ],
)
def test_get_offsets(line_index, offsets):
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    assert wrapped_document.get_offsets(line_index) == offsets


def test_get_offsets_no_wrapping():
    document = Document("abc")
    wrapped_document = WrappedDocument(document, width=4)

    assert wrapped_document.get_offsets(0) == []


@pytest.mark.parametrize("line_index", [-4, 10000])
def test_get_offsets_invalid_line_index(line_index):
    document = Document(SIMPLE_TEXT)
    wrapped_document = WrappedDocument(document, width=4)

    with pytest.raises(ValueError):
        wrapped_document.get_offsets(line_index)
