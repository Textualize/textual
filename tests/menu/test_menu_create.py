from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Menu
from textual.widgets.menu import MenuOption, MenuSeparator


class MenuApp(App[None]):
    """Test menu application."""

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Menu(
            "bare string",
            MenuOption("bare option"),
            MenuSeparator(),
            MenuOption("disabled option", disabled=True),
            None,
            MenuOption("with id option", id="42"),
            MenuOption("with id and disabled option", id="23", disabled=True),
        )


async def test_all_parameters_become_menu_options() -> None:
    """All input parameters to a menu should become MenuOptions."""
    async with MenuApp().run_test() as pilot:
        menu = pilot.app.query_one(Menu)
        assert menu.option_count == 5
        for n in range(5):
            assert isinstance(menu.get_option_at_index(n), MenuOption)
