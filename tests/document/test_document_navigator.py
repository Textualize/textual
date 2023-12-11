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
# 1 | 01234


def make_navigator(text, width):
    document = Document(text)
    wrapped_document = WrappedDocument(document, width)
    wrapped_document.wrap()
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
    ],
)
def test_up(start, end):
    assert make_navigator(TEXT, 4).up(start, 4) == end


@pytest.mark.parametrize(
    "start,end",
    [
        # [(0, 0), (0, 3)],
        # [(0, 1), (0, 4)],
        # [(0, 2), (0, 5)],
        # [(0, 3), (1, 0)],
        # [(0, 4), (1, 1)],
        # [(0, 5), (1, 2)],
        # [(0, 6), (1, 3)],
        [(0, 7), (1, 4)],
    ],
)
def test_down(start, end):
    assert make_navigator(TEXT, 4).down(start, 4) == end
