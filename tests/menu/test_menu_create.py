"""Core menu unit tests, aimed at testing basic menu creation."""

from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import Menu
from textual.widgets.menu import MenuOption, MenuSeparator


class MenuApp(App[None]):
    """Test menu application."""

    MENU_ONE = "23"
    MENU_TWO = "42"

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Menu(
            "0",
            MenuOption("1"),
            MenuSeparator(),
            MenuOption("2", disabled=True),
            None,
            MenuOption("3", id=self.MENU_ONE),
            MenuOption("4", id=self.MENU_TWO, disabled=True),
        )


async def test_all_parameters_become_menu_options() -> None:
    """All input parameters to a menu should become MenuOptions."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        assert menu.option_count == 5
        for n in range(5):
            assert isinstance(menu.get_option_at_index(n), MenuOption)


async def test_id_capture() -> None:
    """All options given an ID should retain the ID."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        with_id = 0
        without_id = 0
        for n in range(5):
            if menu.get_option_at_index(n).id is None:
                without_id += 1
            else:
                with_id += 1
        assert with_id == 2
        assert without_id == 3


async def test_get_option_by_id() -> None:
    """It should be possible to get a menu option by ID."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        assert menu.get_option(MenuApp.MENU_ONE).prompt == "3"
        assert menu.get_option(MenuApp.MENU_TWO).prompt == "4"


async def test_get_option_with_bad_id() -> None:
    """Asking for an option with a bad ID should give an error."""
    async with MenuApp().run_test() as pilot:
        with pytest.raises(KeyError):
            _ = pilot.app.query_one(Menu).get_option("this does not exist")


async def test_get_option_by_index() -> None:
    """It should be possible to get a menu option by index."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        for n in range(5):
            assert menu.get_option_at_index(n).prompt == str(n)
        assert menu.get_option_at_index(-1).prompt == "4"


async def test_get_option_at_bad_index() -> None:
    """Asking for an option at a bad index should give an error."""
    async with MenuApp().run_test() as pilot:
        with pytest.raises(IndexError):
            _ = pilot.app.query_one(Menu).get_option_at_index(42)
        with pytest.raises(IndexError):
            _ = pilot.app.query_one(Menu).get_option_at_index(-42)


async def test_clear_menu() -> None:
    """It should be possible to clear the menu of all content."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        assert menu.option_count == 5
        menu.clear()
        assert menu.option_count == 0
