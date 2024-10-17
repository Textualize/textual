from textual.app import App
from textual.binding import Binding
from textual.demo2.home import HomeScreen
from textual.demo2.projects import ProjectsScreen
from textual.demo2.widgets import WidgetsScreen


class DemoApp(App):
    """The demo app defines the modes and sets a few bindings."""

    MODES = {
        "home": HomeScreen,
        "projects": ProjectsScreen,
        "widgets": WidgetsScreen,
    }
    DEFAULT_MODE = "home"
    BINDINGS = [
        Binding(
            "h",
            "app.switch_mode('home')",
            "home",
            tooltip="Show the home screen",
        ),
        Binding(
            "p",
            "app.switch_mode('projects')",
            "projects",
            tooltip="A selection of Textual projects",
        ),
        Binding(
            "w",
            "app.switch_mode('widgets')",
            "widgets",
            tooltip="Test the builtin widgets",
        ),
    ]
