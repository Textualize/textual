from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Label, Static


async def test_remove_single_widget():
    """It should be possible to the only widget on a screen."""
    async with App().run_test() as pilot:
        widget = Static()
        assert not widget.is_attached
        await pilot.app.mount(widget)
        assert widget.is_attached
        assert len(pilot.app.screen._nodes) == 1
        await pilot.app.query_one(Static).remove()
        assert not widget.is_attached
        assert len(pilot.app.screen._nodes) == 0


async def test_many_remove_all_widgets():
    """It should be possible to remove all widgets on a multi-widget screen."""
    async with App().run_test() as pilot:
        await pilot.app.mount(*[Static() for _ in range(10)])
        assert len(pilot.app.screen._nodes) == 10
        await pilot.app.query(Static).remove()
        assert len(pilot.app.screen._nodes) == 0


async def test_many_remove_some_widgets():
    """It should be possible to remove some widgets on a multi-widget screen."""
    async with App().run_test() as pilot:
        await pilot.app.mount(*[Static(classes=f"is-{n % 2}") for n in range(10)])
        assert len(pilot.app.screen._nodes) == 10
        await pilot.app.query(".is-0").remove()
        assert len(pilot.app.screen._nodes) == 5


async def test_remove_branch():
    """It should be possible to remove a whole branch in the DOM."""
    async with App().run_test() as pilot:
        await pilot.app.mount(
            Container(Container(Container(Container(Container(Static()))))),
            Static(),
            Container(Container(Container(Container(Container(Static()))))),
        )
        assert len(pilot.app.screen.walk_children(with_self=False)) == 13
        await pilot.app.screen._nodes[0].remove()
        assert len(pilot.app.screen.walk_children(with_self=False)) == 7


async def test_remove_overlap():
    """It should be possible to remove an overlapping collection of widgets."""
    async with App().run_test() as pilot:
        await pilot.app.mount(
            Container(Container(Container(Container(Container(Static()))))),
            Static(),
            Container(Container(Container(Container(Container(Static()))))),
        )
        assert len(pilot.app.screen.walk_children(with_self=False)) == 13
        await pilot.app.query(Container).remove()
        assert len(pilot.app.screen.walk_children(with_self=False)) == 1


async def test_remove_move_focus():
    """Removing a focused widget should settle focus elsewhere."""
    async with App().run_test() as pilot:
        buttons = [Button(str(n)) for n in range(10)]
        await pilot.app.mount(Container(*buttons[:5]), Container(*buttons[5:]))
        assert len(pilot.app.screen._nodes) == 2
        assert len(pilot.app.screen.walk_children(with_self=False)) == 12
        assert pilot.app.focused is None
        await pilot.press("tab")
        assert pilot.app.focused is not None
        assert pilot.app.focused == buttons[0]
        await pilot.app.screen._nodes[0].remove()
        assert len(pilot.app.screen._nodes) == 1
        assert len(pilot.app.screen.walk_children(with_self=False)) == 6
        assert pilot.app.focused is not None
        assert pilot.app.focused == buttons[9]


async def test_widget_remove_order():
    """A Widget.remove of a top-level widget should cause bottom-first removal."""

    removals: list[str] = []

    class Removable(Container):
        def on_unmount(self, _):
            removals.append(self.id if self.id is not None else "unknown")

    async with App().run_test() as pilot:
        await pilot.app.mount(
            Removable(Removable(Removable(id="grandchild"), id="child"), id="parent")
        )
        assert len(pilot.app.screen.walk_children(with_self=False)) == 3
        await pilot.app.screen._nodes[0].remove()
        assert len(pilot.app.screen.walk_children(with_self=False)) == 0
        assert removals == ["grandchild", "child", "parent"]


async def test_query_remove_order():
    """A DOMQuery.remove of a top-level widget should cause bottom-first removal."""

    removals: list[str] = []

    class Removable(Container):
        def on_unmount(self, _):
            removals.append(self.id if self.id is not None else "unknown")

    async with App().run_test() as pilot:
        await pilot.app.mount(
            Removable(Removable(Removable(id="grandchild"), id="child"), id="parent")
        )
        assert len(pilot.app.screen.walk_children(with_self=False)) == 3
        await pilot.app.query(Removable).remove()
        assert len(pilot.app.screen.walk_children(with_self=False)) == 0
        assert removals == ["grandchild", "child", "parent"]


class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield Button("ABC")
        yield Label("Outside of vertical.")
        with Vertical():
            for index in range(5):
                yield Label(str(index))


async def test_widget_remove_children_container():
    app = ExampleApp()
    async with app.run_test():
        container = app.query_one(Vertical)

        # 6 labels in total, with 5 of them inside the container.
        assert len(app.query(Label)) == 6
        assert len(container.children) == 5

        await container.remove_children()

        # The labels inside the container are gone, and the 1 outside remains.
        assert len(app.query(Label)) == 1
        assert len(container.children) == 0


async def test_widget_remove_children_with_star_selector():
    app = ExampleApp()
    async with app.run_test():
        container = app.query_one(Vertical)

        # 6 labels in total, with 5 of them inside the container.
        assert len(app.query(Label)) == 6
        assert len(container.children) == 5

        await container.remove_children("*")

        # The labels inside the container are gone, and the 1 outside remains.
        assert len(app.query(Label)) == 1
        assert len(container.children) == 0


async def test_widget_remove_children_with_string_selector():
    app = ExampleApp()
    async with app.run_test():
        container = app.query_one(Vertical)

        # 6 labels in total, with 5 of them inside the container.
        assert len(app.query(Label)) == 6
        assert len(container.children) == 5

        await app.screen.remove_children("Label")

        # Only the Screen > Label widget is gone, everything else remains.
        assert len(app.query(Button)) == 1
        assert len(app.query(Vertical)) == 1
        assert len(app.query(Label)) == 5


async def test_widget_remove_children_with_type_selector():
    app = ExampleApp()
    async with app.run_test():
        assert len(app.query(Button)) == 1  # Sanity check.
        await app.screen.remove_children(Button)
        assert len(app.query(Button)) == 0


async def test_widget_remove_children_with_selector_does_not_leak():
    app = ExampleApp()
    async with app.run_test():
        container = app.query_one(Vertical)

        # 6 labels in total, with 5 of them inside the container.
        assert len(app.query(Label)) == 6
        assert len(container.children) == 5

        await container.remove_children("Label")

        # The labels inside the container are gone, and the 1 outside remains.
        assert len(app.query(Label)) == 1
        assert len(container.children) == 0


async def test_widget_remove_children_no_children():
    app = ExampleApp()
    async with app.run_test():
        button = app.query_one(Button)

        count_before = len(app.query("*"))
        await button.remove_children()
        count_after = len(app.query("*"))

        assert len(app.query(Button)) == 1  # The button still remains.
        assert (
            count_before == count_after
        )  # No widgets have been removed, since Button has no children.


async def test_widget_remove_children_no_children_match_selector():
    app = ExampleApp()
    async with app.run_test():
        container = app.query_one(Vertical)
        assert len(container.query("Button")) == 0  # Sanity check.

        count_before = len(app.query("*"))
        container_children_before = list(container.children)
        await container.remove_children("Button")

        assert count_before == len(app.query("*"))
        assert container_children_before == list(container.children)
