"""Unit tests aimed at ensuring the menu option class can be subclassed."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Menu
from textual.widgets.menu import MenuOption


class MenuOptionWithExtras(MenuOption):
    """An example subclass of a menu option."""

    def __init__(self, test: int) -> None:
        super().__init__(str(test), str(int), False)
        self.test = test


class MenuApp(App[None]):
    """Test menu application."""

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Menu(*[MenuOptionWithExtras(n) for n in range(100)])


async def test_menu_with_subclassed_options() -> None:
    """It should be possible to build a menu with subclassed options."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        assert menu.option_count == 100
        for n in range(100):
            for option in (menu.get_option(str(n)), menu.get_option_at_index(n)):
                assert isinstance(option, MenuOptionWithExtras)
                assert option.prompt == str(n)
                assert option.id == str(n)
                assert option.test == n
