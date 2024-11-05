from dataclasses import dataclass

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, ItemGrid, Vertical, VerticalScroll
from textual.demo.page import PageScreen
from textual.widgets import Footer, Label, Link, Markdown, Static


@dataclass
class ProjectInfo:
    """Dataclass for storing project information."""

    title: str
    author: str
    url: str
    description: str
    stars: str


PROJECTS_MD = """\
# Projects

There are many amazing Open Source Textual apps available for download.
And many more still in development.

See below for a small selection!
"""

PROJECTS = [
    ProjectInfo(
        "Posting",
        "Darren Burns",
        "https://posting.sh/",
        """Posting is an HTTP client, not unlike Postman and Insomnia. As a TUI application, it can be used over SSH and enables efficient keyboard-centric workflows. """,
        "4.7k",
    ),
    ProjectInfo(
        "Memray",
        "Bloomberg",
        "https://github.com/bloomberg/memray",
        """Memray is a memory profiler for Python. It can track memory allocations in Python code, in native extension modules, and in the Python interpreter itself.""",
        "13.2k",
    ),
    ProjectInfo(
        "Toolong",
        "Will McGugan",
        "https://github.com/Textualize/toolong",
        """A terminal application to view, tail, merge, and search log files (plus JSONL).""",
        "3.1k",
    ),
    ProjectInfo(
        "Dolphie",
        "Charles Thompson",
        "https://github.com/charles-001/dolphie",
        "Your single pane of glass for real-time analytics into MySQL/MariaDB & ProxySQL",
        "608",
    ),
    ProjectInfo(
        "Harlequin",
        "Ted Conbeer",
        "https://harlequin.sh/",
        """Portable, powerful, colorful. An easy, fast, and beautiful database client for the terminal.""",
        "3.7k",
    ),
    ProjectInfo(
        "Elia",
        "Darren Burns",
        "https://github.com/darrenburns/elia",
        """A snappy, keyboard-centric terminal user interface for interacting with large language models.
Chat with Claude 3, ChatGPT, and local models like Llama 3, Phi 3, Mistral and Gemma.""",
        "1.8k",
    ),
    ProjectInfo(
        "Trogon",
        "Textualize",
        "https://github.com/Textualize/trogon",
        "Auto-generate friendly terminal user interfaces for command line apps.",
        "2.5k",
    ),
    ProjectInfo(
        "TFTUI - The Terraform textual UI",
        "Ido Avraham",
        "https://github.com/idoavrah/terraform-tui",
        "TFTUI is a powerful textual UI that empowers users to effortlessly view and interact with their Terraform state.",
        "1k",
    ),
    ProjectInfo(
        "RecoverPy",
        "Pablo Lecolinet",
        "https://github.com/PabloLec/RecoverPy",
        """RecoverPy is a powerful tool that leverages your system capabilities to recover lost files.""",
        "1.3k",
    ),
    ProjectInfo(
        "Frogmouth",
        "Dave Pearson",
        "https://github.com/Textualize/frogmouth",
        """Frogmouth is a Markdown viewer / browser for your terminal, built with Textual.""",
        "2.5k",
    ),
    ProjectInfo(
        "oterm",
        "Yiorgis Gozadinos",
        "https://github.com/ggozad/oterm",
        "The text-based terminal client for Ollama.",
        "1k",
    ),
    ProjectInfo(
        "logmerger",
        "Paul McGuire",
        "https://github.com/ptmcg/logmerger",
        "logmerger is a TUI for viewing a merged display of multiple log files, merged by timestamp.",
        "162",
    ),
    ProjectInfo(
        "doit",
        "Murli Tawari",
        "https://github.com/kraanzu/dooit",
        "A todo manager that you didn't ask for, but needed!",
        "2.1k",
    ),
]


class Project(Vertical, can_focus=True, can_focus_children=False):
    """Display project information and open repo links."""

    ALLOW_MAXIMIZE = True
    DEFAULT_CSS = """
    Project {
        width: 1fr;
        height: auto;      
        padding: 0 1;
        border: tall transparent;
        opacity: 0.8;
        box-sizing: border-box;
        &:focus {
            border: tall $accent;
            background: $primary 40%;
            opacity: 1.0;            
        }
        #title { text-style: bold; width: 1fr; }
        #author { text-style: italic; }
        .stars {
            color: $secondary;
            text-align: right;
            text-style: bold;
            width: auto;
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
        info = self.project_info
        with Horizontal(classes="header"):
            yield Label(info.title, id="title")
            yield Label(f"★ {info.stars}", classes="stars")
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
            keyline:thin $foreground 50%;        
        }              
        Markdown { margin: 0; padding: 0 2; max-width: 100;}
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
