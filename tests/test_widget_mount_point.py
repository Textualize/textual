import pytest

from textual.widget import MountError, Widget


class Content(Widget):
    pass


class Body(Widget):
    pass


def test_find_dom_spot():
    # Build up a "fake" DOM for an application.
    screen = Widget(name="Screen")
    header = Widget(name="Header", id="header")
    body = Body(id="body")
    content = [Content(id=f"item{n}") for n in range(1000)]
    body._add_children(*content)
    footer = Widget(name="Footer", id="footer")
    screen._add_children(header, body, footer)

    # Just as a quick double-check, make sure the main components are in
    # their intended place.
    assert list(screen._nodes) == [header, body, footer]

    # Now check that we find what we're looking for in the places we expect
    # to find them.
    assert screen._find_mount_point(1) == (screen, 1)
    assert screen._find_mount_point(body) == screen._find_mount_point(1)
    assert screen._find_mount_point("Body") == screen._find_mount_point(body)
    assert screen._find_mount_point("#body") == screen._find_mount_point(1)

    # Finally, let's be sure that we get an error if, for some odd reason,
    # we go looking for a widget that isn't actually part of the DOM we're
    # looking in.
    with pytest.raises(MountError):
        _ = screen._find_mount_point(Widget())
