from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.demo2.page import Page
from textual.demo2.projects import ProjectsPage
from textual.demo2.welcome import WelcomePage
from textual.screen import Screen
from textual.widgets import Footer


class DemoScreen(Screen):
    DEFAULT_CSS = """
    DemoScreen {
        layout: horizontal;
    }
    """

    BINDINGS = [
        Binding("1", "page(1)", "page 1", tooltip="Go to page 1"),
        Binding("2", "page(2)", "page 2", tooltip="Go to page 2"),
        Binding("3", "page(3)", "page 3", tooltip="Go to page 3"),
        Binding("4", "page(4)", "page 4", tooltip="Go to page 4"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield WelcomePage(id="page1")
        yield ProjectsPage(id="page2")
        yield Page(id="page3")
        yield Page(id="page4")

    @property
    def allow_horizontal_scroll(self) -> bool:
        return True

    def action_page(self, page: int) -> None:
        self.query_one(f"#page{page}").scroll_visible()


class DemoApp(App):
    def get_default_screen(self) -> Screen:
        return DemoScreen()
