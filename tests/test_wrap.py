from textual._wrap import chunks


def test_chunks():
    assert list(chunks("")) == []
    assert list(chunks("    ")) == []
    assert list(chunks("\t")) == []
    assert list(chunks("foo")) == [(0, 3, "foo")]
    assert list(chunks("  foo  ")) == [(0, 7, "  foo  ")]
    assert list(chunks("foo bar")) == [(0, 4, "foo "), (4, 7, "bar")]
    assert list(chunks("\tfoo bar")) == [(0, 5, "\tfoo "), (5, 8, "bar")]
    assert list(chunks(" foo bar")) == [(0, 5, " foo "), (5, 8, "bar")]
    assert list(chunks("foo bar   ")) == [(0, 4, "foo "), (4, 10, "bar   ")]
    assert list(chunks("foo\t  bar   ")) == [(0, 6, "foo\t  "), (6, 12, "bar   ")]
    assert list(chunks("木\t  川   ")) == [(0, 4, "木\t  "), (4, 8, "川   ")]
