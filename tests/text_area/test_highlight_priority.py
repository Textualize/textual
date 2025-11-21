import pytest
from textual.widgets import TextArea

@pytest.mark.asyncio
async def test_range_highlighting_priority_consistency():
    # Case 1: code with a line before
    ta1 = TextArea.code_editor(
        'print("hello")\nx = range(10)',
        language="python"
    )
    ta1._build_highlight_map()

    # Case 2: only the range() call
    ta2 = TextArea.code_editor(
        'x = range(10)',
        language="python"
    )
    ta2._build_highlight_map()

    # Get highlight lists
    line1 = ta1._highlights[1]   # second line
    line2 = ta2._highlights[0]   # first line

    # RANGE token begins at column 4 in both cases
    RANGE_START = 4

    def get_highlight_name(line):
        for start, end, name in line:
            if start == RANGE_START:
                return name
        return None

    name1 = get_highlight_name(line1)
    name2 = get_highlight_name(line2)

    assert name1 == name2, f"Expected same highlight, got {name1=} and {name2=}"
