from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Label

COLLAPSED_CLASS = "-collapsed"


def get_title(collapsible: Collapsible) -> Collapsible.Title:
    return collapsible.get_child_by_type(Collapsible.Title)


def get_contents(collapsible: Collapsible) -> Collapsible.Contents:
    return collapsible.get_child_by_type(Collapsible.Contents)


async def test_collapsible():
    """It should be possible to access title and collapsed."""
    collapsible = Collapsible(title="Pilot", collapsed=True)
    assert collapsible._title.label == "Pilot"
    assert collapsible.collapsed


async def test_compose_default_collapsible():
    """Test default settings of Collapsible with 1 widget in contents."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(Label("Some Contents"))

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert get_title(collapsible).label == "Toggle"
        assert get_title(collapsible).has_class(COLLAPSED_CLASS)
        assert len(get_contents(collapsible).children) == 1
        assert get_contents(collapsible).has_class(COLLAPSED_CLASS)


async def test_compose_empty_collapsible():
    """It should be possible to create an empty Collapsible."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible()

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert len(get_contents(collapsible).children) == 0


async def test_compose_nested_collapsible():
    """Children Collapsibles are independent from parents Collapsibles."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            with Collapsible(Label("Outer"), id="outer", collapsed=False):
                yield Collapsible(Label("Inner"), id="inner", collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        outer: Collapsible = pilot.app.get_child_by_id("outer")
        inner: Collapsible = get_contents(outer).get_child_by_id("inner")
        outer.collapsed = True
        assert not inner.collapsed


async def test_compose_expanded_collapsible():
    """It should be possible to create a Collapsible with expanded contents."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert not get_title(collapsible).has_class(COLLAPSED_CLASS)
        assert not get_contents(collapsible).has_class(COLLAPSED_CLASS)


async def test_collapsible_collapsed_title_label():
    """Collapsed title label should be displayed."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(Label("Some Contents"), collapsed=True)

    async with CollapsibleApp().run_test() as pilot:
        title = get_title(pilot.app.query_one(Collapsible))
        assert not title.get_child_by_id("expanded-symbol").display
        assert title.get_child_by_id("collapsed-symbol").display


async def test_collapsible_expanded_title_label():
    """Expanded title label should be displayed."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(Label("Some Contents"), collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        title = get_title(pilot.app.query_one(Collapsible))
        assert title.get_child_by_id("expanded-symbol").display
        assert not title.get_child_by_id("collapsed-symbol").display


async def test_collapsible_collapsed_contents_display_false():
    """Test default settings of Collapsible with 1 widget in contents."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(Label("Some Contents"), collapsed=True)

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert not get_contents(collapsible).display


async def test_collapsible_expanded_contents_display_true():
    """Test default settings of Collapsible with 1 widget in contents."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(Label("Some Contents"), collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert get_contents(collapsible).display


async def test_reactive_collapsed():
    """Updating ``collapsed`` should change classes of children."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert not get_title(collapsible).has_class(COLLAPSED_CLASS)
        collapsible.collapsed = True
        assert get_contents(collapsible).has_class(COLLAPSED_CLASS)
        collapsible.collapsed = False
        assert not get_title(collapsible).has_class(COLLAPSED_CLASS)


async def test_toggle_title():
    """Clicking title should update ``collapsed``."""

    class CollapsibleApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Collapsible(collapsed=False)

    async with CollapsibleApp().run_test() as pilot:
        collapsible = pilot.app.query_one(Collapsible)
        assert not collapsible.collapsed
        assert not get_title(collapsible).has_class(COLLAPSED_CLASS)

        await pilot.click(Collapsible.Title)
        assert collapsible.collapsed
        assert get_contents(collapsible).has_class(COLLAPSED_CLASS)

        await pilot.click(Collapsible.Title)
        assert not collapsible.collapsed
        assert not get_title(collapsible).has_class(COLLAPSED_CLASS)
