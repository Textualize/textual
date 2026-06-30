
from textual.markup import escape, to_content

def test_escape_nested_brackets():
    problematic_string = "[type=x, v={'a[0]'}]"
    escaped = escape(problematic_string)
    assert escaped == "\\[type=x, v={'a[0]'}]"
    content = to_content(escaped)
    assert str(content) == problematic_string
