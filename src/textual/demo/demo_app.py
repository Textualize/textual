from __future__ import annotations

from textual.app import App
from textual.binding import Binding
from textual.demo.game import GameScreen
from textual.demo.home import HomeScreen
from textual.demo.projects import ProjectsScreen
from textual.demo.widgets import WidgetsScreen


class DemoApp(App):
    """The demo app defines the modes and sets a few bindings."""

    CSS = """
    .column {          
        align: center top;
        &>*{ max-width: 100; }        
    }
    Screen .-maximized {
        margin: 1 2;        
        max-width: 100%;
        &.column { margin: 1 2; padding: 1 2; }
        &.column > * {        
            max-width: 100%;           
        }        
    }
    """

    MODES = {
        "game": GameScreen,
        "home": HomeScreen,
        "projects": ProjectsScreen,
        "widgets": WidgetsScreen,
    }
    DEFAULT_MODE = "home"
    BINDINGS = [
        Binding(
            "h",
            "app.switch_mode('home')",
            "Home",
            tooltip="Show the home screen",
        ),
        Binding(
            "g",
            "app.switch_mode('game')",
            "Game",
            tooltip="Unwind with a Textual game",
        ),
        Binding(
            "p",
            "app.switch_mode('projects')",
            "Projects",
            tooltip="A selection of Textual projects",
        ),
        Binding(
            "w",
            "app.switch_mode('widgets')",
            "Widgets",
            tooltip="Test the builtin widgets",
        ),
        Binding(
            "ctrl+s",
            "app.screenshot",
            "Screenshot",
            tooltip="Save an SVG 'screenshot' of the current screen",
        ),
        Binding(
            "ctrl+a",
            "app.maximize",
            "Maximize",
            tooltip="Maximize the focused widget (if possible)",
        ),
    ]

    def action_maximize(self) -> None:
        if self.screen.is_maximized:
            return
        if self.screen.focused is None:
            self.notify(
                "Nothing to be maximized (try pressing [b]tab[/b])",
                title="Maximize",
                severity="warning",
            )
        else:
            if self.screen.maximize(self.screen.focused):
                self.notify(
                    "You are now in the maximized view. Press [b]escape[/b] to return.",
                    title="Maximize",
                )
            else:
                self.notify(
                    "This widget may not be maximized.",
                    title="Maximize",
                    severity="warning",
                )

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Disable switching to a mode we are already on."""
        if (
            action == "switch_mode"
            and parameters
            and self.current_mode == parameters[0]
        ):
            return None
        return True
