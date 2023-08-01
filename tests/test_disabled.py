"""Test Widget.disabled."""

import pytest

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    DirectoryTree,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    MarkdownViewer,
    OptionList,
    RadioButton,
    RadioSet,
    RichLog,
    Select,
    Switch,
    Tree,
)


class DisableApp(App[None]):
    """Application for testing Widget.disabled."""

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield VerticalScroll(
            Button(),
            DataTable(),
            DirectoryTree("."),
            Input(),
            ListView(),
            Switch(),
            RichLog(),
            Tree("Test"),
            Markdown(),
            MarkdownViewer(),
            id="test-container",
        )


async def test_all_initially_enabled() -> None:
    """All widgets should start out enabled."""
    async with DisableApp().run_test() as pilot:
        assert all(
            not node.disabled for node in pilot.app.screen.query("#test-container > *")
        )


async def test_enabled_widgets_have_enabled_pseudo_class() -> None:
    """All enabled widgets should have the :enabled pseudoclass."""
    async with DisableApp().run_test() as pilot:
        assert all(
            node.has_pseudo_class("enabled") and not node.has_pseudo_class("disabled")
            for node in pilot.app.screen.query("#test-container > *")
        )


async def test_all_individually_disabled() -> None:
    """Post-disable all widgets should report being disabled."""
    async with DisableApp().run_test() as pilot:
        for node in pilot.app.screen.query("VerticalScroll > *"):
            node.disabled = True
        assert all(
            node.disabled for node in pilot.app.screen.query("#test-container > *")
        )


async def test_disabled_widgets_have_disabled_pseudo_class() -> None:
    """All disabled widgets should have the :disabled pseudoclass."""
    async with DisableApp().run_test() as pilot:
        for node in pilot.app.screen.query("#test-container > *"):
            node.disabled = True
        assert all(
            node.has_pseudo_class("disabled") and not node.has_pseudo_class("enabled")
            for node in pilot.app.screen.query("#test-container > *")
        )


async def test_disable_via_container() -> None:
    """All child widgets should appear (to CSS) as disabled by a container being disabled."""
    async with DisableApp().run_test() as pilot:
        pilot.app.screen.query_one("#test-container", VerticalScroll).disabled = True
        assert all(
            node.has_pseudo_class("disabled") and not node.has_pseudo_class("enabled")
            for node in pilot.app.screen.query("#test-container > *")
        )


class ChildrenNoFocusDisabledContainer(App[None]):
    """App for regression test for https://github.com/Textualize/textual/issues/2772."""

    def compose(self) -> ComposeResult:
        with Vertical():
            with Vertical():
                yield Button()
                yield Checkbox()
                yield DataTable()
                yield DirectoryTree(".")
                yield Input()
                with ListView():
                    yield ListItem(Label("one"))
                    yield ListItem(Label("two"))
                    yield ListItem(Label("three"))
                yield OptionList("one", "two", "three")
                with RadioSet():
                    yield RadioButton("one")
                    yield RadioButton("two")
                    yield RadioButton("three")
                yield Select([("one", 1), ("two", 2), ("three", 3)])
                yield Switch()

    def on_mount(self):
        dt = self.query_one(DataTable)
        dt.add_columns("one", "two", "three")
        dt.add_rows([["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]])


@pytest.mark.parametrize(
    "widget",
    [
        Button,
        Checkbox,
        DataTable,
        DirectoryTree,
        Input,
        ListView,
        OptionList,
        RadioSet,
        Select,
        Switch,
    ],
)
async def test_children_loses_focus_if_container_is_disabled(widget):
    """Regression test for https://github.com/Textualize/textual/issues/2772."""
    app = ChildrenNoFocusDisabledContainer()
    async with app.run_test() as pilot:
        app.query(widget).first().focus()
        await pilot.pause()
        assert isinstance(app.focused, widget)
        app.query(Vertical).first().disabled = True
        await pilot.pause()
        assert app.focused is None
