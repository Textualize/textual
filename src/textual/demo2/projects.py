from dataclasses import dataclass

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.demo2.page import PageScreen
from textual.widgets import Footer, Label, Static


@dataclass
class ProjectInfo:
    title: str
    url: str
    description: str


PROJECTS = [
    ProjectInfo(
        "Posting",
        "https://posting.sh/",
        "Posting is a beautiful open-source terminal app for developing and testing APIs.",
    )
] * 5


class Link(Label):
    """The link in the Project widget."""

    DEFAULT_CSS = """
    Link {
        color: $accent;
        text-style: underline;
        &:hover { text-style: reverse;}
    }
    """

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.url = url
        self.tooltip = "Click to open Repository URL"

    def on_click(self) -> None:
        self.app.open_url(self.url)


class Project(VerticalScroll, can_focus=True):
    ALLOW_MAXIMIZE = True
    DEFAULT_CSS = """
    Project {
        width: 1fr;
        min-height: 8;
        padding: 0 1;
        border: tall transparent;
        opacity: 0.5;

        &:focus-within {
            border: tall $accent;
            background: $boost;
            opacity: 1.0;
        }
        #title { text-style: bold; }
        .stars {
            color: $secondary;
            text-align: right;
            width: 1fr;
        }
        .header { height: 1; }
        .link {
            color: $accent;
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
        with Horizontal(classes="header"):
            yield Label(self.project_info.title, id="title")
            yield Label("★ 23K", classes="stars")
        yield Link(self.project_info.url)
        yield Static(self.project_info.description, classes="description")

    @on(events.Enter)
    @on(events.Leave)
    def on_enter(self, event: events.Enter):
        event.stop()
        self.set_class(self.is_mouse_over, "-hover")

    def action_open_repository(self) -> None:
        self.app.open_url(self.project_info.url)


class ProjectsScreen(PageScreen):
    DEFAULT_CSS = """
    ProjectsScreen {
        layout: grid;
        
        margin: 1;
        Grid {
            margin: 1 2;
            padding: 1 2;
            background: $boost;
            width: 1fr;
            height: 1fr;
            grid-size: 2; 
            grid-gutter: 1 1;
            hatch: right $primary 50%;        
            keyline:heavy $background;
          
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            for project in PROJECTS:
                yield Project(project)
        yield Footer()
