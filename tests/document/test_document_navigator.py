import pytest

from textual.document._document import Document
from textual.document._document_navigator import DocumentNavigator
from textual.document._wrapped_document import WrappedDocument

TEXT = """\
01 3456
01234"""


# wrapped width = 4:
# line_index | wrapped_lines
# 0 | 01_
#   | 3456
# 1 | 0123
#   | 4


def make_navigator(text, width):
    document = Document(text)
    wrapped_document = WrappedDocument(document, width)
    navigator = DocumentNavigator(wrapped_document)
    return navigator


@pytest.mark.parametrize(
    "start,end",
    [
        [(0, 0), (0, 0)],
        [(0, 1), (0, 0)],
        [(0, 2), (0, 0)],
        [(0, 3), (0, 0)],
        [(0, 4), (0, 1)],
        [(0, 5), (0, 2)],
        [(0, 6), (0, 2)],  # clamps to valid index
        [(0, 7), (0, 2)],  # clamps to the last valid index
        [(1, 0), (0, 3)],
        [(1, 1), (0, 4)],
        [(1, 5), (1, 1)],
    ],
)
def test_get_location_above(start, end):
    assert make_navigator(TEXT, 4).get_location_above(start) == end


@pytest.mark.parametrize(
    "start,end",
    [
        [(0, 0), (0, 3)],
        [(0, 1), (0, 4)],
        [(0, 2), (0, 5)],
        [(0, 3), (1, 0)],
        [(0, 4), (1, 1)],
        [(0, 5), (1, 2)],
        [(0, 6), (1, 3)],
        [(0, 7), (1, 3)],
        [(1, 3), (1, 5)],
    ],
)
def test_get_location_below(start, end):
    assert make_navigator(TEXT, 4).get_location_below(start) == end


@pytest.mark.parametrize(
    "start,end",
    [
        [(0, 0), (0, 0)],
        [(0, 2), (0, 0)],
        [(0, 3), (0, 3)],
        [(0, 6), (0, 3)],
        [(0, 7), (0, 3)],
        [(1, 0), (1, 0)],
        [(1, 3), (1, 0)],
        [(1, 4), (1, 4)],
        [(1, 5), (1, 4)],
    ],
)
def test_get_location_home(start, end):
    assert make_navigator(TEXT, 4).get_location_home(start) == end


@pytest.mark.parametrize(
    "start,end",
    [
        [(0, 0), (0, 2)],
        [(0, 2), (0, 2)],
        [(0, 3), (0, 7)],
        [(0, 5), (0, 7)],
        [(1, 2), (1, 3)],
    ],
)
def test_get_location_end(start, end):
    assert make_navigator(TEXT, 4).get_location_end(start) == end
