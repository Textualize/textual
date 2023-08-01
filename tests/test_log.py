from textual.widgets import Log


def test_process_line():
    assert Log._process_line("") == []
    assert Log._process_line("foo") == ["foo"]
    assert Log._process_line("foo\nbar") == ["foo", "bar"]
    assert Log._process_line("\x00foo\nbar") == ["�foo", "bar"]
    assert Log._process_line("\x00\tfoo\nbar") == ["�       foo", "bar"]
