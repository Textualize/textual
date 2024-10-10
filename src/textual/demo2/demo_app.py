from textual.app import App
from textual.binding import Binding
from textual.demo2.projects import ProjectsScreen
from textual.demo2.welcome import WelcomeScreen


class DemoApp(App):
    MODES = {"welcome": WelcomeScreen, "projects": ProjectsScreen}
    # DEFAULT_MODE = "welcome"

    BINDINGS = [
        Binding(
            "w",
            "app.switch_mode('welcome')",
            "welcome",
            tooltip="Show the welcome screen",
        ),
        Binding(
            "p",
            "app.switch_mode('projects')",
            "projects",
            tooltip="A selection of Textual projects",
        ),
    ]

    def on_mount(self) -> None:
        self.switch_mode("welcome")
