"""Unit tests for testing the menu's disabled facility."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Menu
from textual.widgets.menu import MenuOption


class MenuApp(App[None]):
    """Test menu application."""

    def __init__(self, disabled: bool) -> None:
        super().__init__()
        self.initial_disabled = disabled

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Menu(
            *[
                MenuOption(str(n), id=str(n), disabled=self.initial_disabled)
                for n in range(100)
            ]
        )


async def test_default_enabled() -> None:
    """Menu options created enabled should remain enabled."""
    async with MenuApp(False).run_test() as pilot:
        for option in pilot.app.query_one(Menu).options:
            assert option.disabled is False


async def test_default_disabled() -> None:
    """Menu options created disabled should remain disabled."""
    async with MenuApp(True).run_test() as pilot:
        for option in pilot.app.query_one(Menu).options:
            assert option.disabled is True


async def test_enabled_to_disabled_via_index() -> None:
    """It should be possible to change enabled to disabled via index."""
    async with MenuApp(False).run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        for n in range(menu.option_count):
            assert menu.get_option_at_index(n).disabled is False
            menu.disable_option_at_index(n)
            assert menu.get_option_at_index(n).disabled is True


async def test_disabled_to_enabled_via_index() -> None:
    """It should be possible to change disabled to enabled via index."""
    async with MenuApp(True).run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        for n in range(menu.option_count):
            assert menu.get_option_at_index(n).disabled is True
            menu.enable_option_at_index(n)
            assert menu.get_option_at_index(n).disabled is False


async def test_enabled_to_disabled_via_id() -> None:
    """It should be possible to change enabled to disabled via id."""
    async with MenuApp(False).run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        for n in range(menu.option_count):
            assert menu.get_option(str(n)).disabled is False
            menu.disable_option(str(n))
            assert menu.get_option(str(n)).disabled is True


async def test_disabled_to_enabled_via_id() -> None:
    """It should be possible to change disabled to enabled via id."""
    async with MenuApp(True).run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        for n in range(menu.option_count):
            assert menu.get_option(str(n)).disabled is True
            menu.enable_option(str(n))
            assert menu.get_option(str(n)).disabled is False
