from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.demo2.page import Page
from textual.widgets import Label, Static


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
] * 4


class Project(Vertical, can_focus=True):
    DEFAULT_CSS = """
    Project {
    
        # margin: 1 2;    
        width: 1fr;
       
        padding: 1 2;
        # background: $boost;

        border: tall transparent;

        &:focus-within {
            border: tall $accent;
            background: $boost;
        }
        #title {
            text-style: bold;            
        }
        .stars {
            color: $secondary;
            text-align: right;
            width: 1fr;
        }
    }
    """

    def __init__(self, project_info: ProjectInfo) -> None:
        self.project_info = project_info
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.project_info.title, id="title")
            yield Label("★ 23K", classes="stars")
        yield Static(self.project_info.description)


class ProjectsPage(Page):
    DEFAULT_CSS = """
    ProjectsPage {
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
          
           
            # keyline:thin $success;
          
        }
    }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            for project in PROJECTS:
                yield Project(project)
