from __future__ import annotations

from dataclasses import dataclass

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, ItemGrid, Vertical, VerticalScroll
from textual.demo.page import PageScreen
from textual.widgets import Footer, Label, Link, Markdown, Static
from textual.demo._project_stars import STARS
from textual.demo._project_data import PROJECTS, ProjectInfo

PROJECTS_MD = """\
# Projects

There are many amazing Open Source Textual apps available for download.
And many more still in development.

See below for a small selection!
"""


class Project(Vertical, can_focus=True, can_focus_children=False):
    """Display project information and open repo links."""

    ALLOW_MAXIMIZE = True
    DEFAULT_CSS = """
    Project {
        width: 1fr;
        height: auto;
        padding: 0 1;
        border: tall transparent;
        box-sizing: border-box;
        &:focus {
            border: tall $text-primary;
            background: $primary 20%;
            &.link {
                color: red !important;
            }
        }
        #title { text-style: bold; width: 1fr; }
        #author { text-style: italic; }
        .stars {
            color: $text-accent;
            text-align: right;
            text-style: bold;
            width: auto;
        }
        .header { height: 1; }
        .link {
            color: $text-accent;
            text-style: underline;
        }
        .description { color: $text-muted; }
        &.-hover { opacity: 1; }
    }
    """

    BINDINGS = [
        Binding(
            "enter",
            "open_repository",
            "open repo",
            tooltip="Open the GitHub repository in your browser",
        )
    ]

    def __init__(self, project_info: ProjectInfo) -> None:
        self.project_info = project_info
        super().__init__()

    def compose(self) -> ComposeResult:
        info = self.project_info
        with Horizontal(classes="header"):
            yield Label(info.title, id="title")
            yield Label(f"★ {STARS[info.title]}", classes="stars")
        yield Label(info.author, id="author")
        yield Link(info.url, tooltip="Click to open project repository")
        yield Static(info.description, classes="description")

    @on(events.Enter)
    @on(events.Leave)
    def on_enter(self, event: events.Enter):
        event.stop()
        self.set_class(self.is_mouse_over, "-hover")

    def action_open_repository(self) -> None:
        self.app.open_url(self.project_info.url)


class ProjectsScreen(PageScreen):
    AUTO_FOCUS = None
    CSS = """
    ProjectsScreen {
        align-horizontal: center;
        ItemGrid {
            margin: 2 4;
            padding: 1 2;
            background: $boost;
            width: 1fr;
            height: auto;
            grid-gutter: 1 1;
            grid-rows: auto;
            keyline:thin $foreground 30%;
        }
        Markdown { margin: 0; padding: 0 2; max-width: 100; background: transparent; }
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll() as container:
            container.can_focus = False
            with Center():
                yield Markdown(PROJECTS_MD)
            with ItemGrid(min_column_width=40):
                for project in PROJECTS:
                    yield Project(project)
        yield Footer()


if __name__ == "__main__":
    from textual.app import App

    class GameApp(App):
        def get_default_screen(self) -> Screen:
            return ProjectsScreen()

    app = GameApp()
    app.run()
