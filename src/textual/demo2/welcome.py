from importlib.metadata import version

import httpx

from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.demo2.page import PageScreen
from textual.reactive import reactive
from textual.widgets import Digits, Footer, Label, Markdown

WHAT_IS_TEXTUAL_MD = """\
# What is Textual?

**The fastest way to build sophisticated data applications that run *anywhere*.**

Textual apps can run on virtually anything from a $5 single-board computer upwards.
Deploy as a terminal application, over SSH, or serve as a web application [web application](https://github.com/Textualize/textual-web).



* Build sophisticated applications — fast!
* No front-end skills required.
* Elegant Python API from the developer of [Rich](https://github.com/Textualize/rich).
* Deploy Textual as a terminal application, over SSH, *or* a [web application](https://github.com/Textualize/textual-web)!
"""


class StarCount(Vertical):
    """Widget to get and display GitHub star count."""

    DEFAULT_CSS = """
    StarCount {
        dock: top;
        height: 5;
        border-bottom: hkey $background;
        border-top: hkey $background;
        layout: horizontal;
        background: $boost;
        padding: 0 1;
        color: $warning;
        Label { text-style: bold; }
        LoadingIndicator { background: transparent !important; }
        Digits { margin-right: 1; }
        Label { margin-right: 1; }
        #stars { align: center middle; }
        #forks { align: right middle; }
    }
    """
    stars = reactive(25251, recompose=True)
    forks = reactive(776, recompose=True)

    @work
    async def get_stars(self):
        """Worker to get stars from GitHub API."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                repository_json = (
                    await client.get("https://api.github.com/repos/textualize/textual")
                ).json()
            self.stars = repository_json["stargazers_count"]
            self.forks = repository_json["forks"]
        except Exception:
            self.notify(
                "Unable to get star count (maybe rate-limited)",
                title="GitHub stars",
                severity="error",
            )
        self.loading = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="version"):
            yield Label("Version")
            yield Digits(version("textual"))
        with Horizontal(id="stars"):
            yield Label("GitHub ★")
            stars = f"{self.stars / 1000:.1f}K"
            yield Digits(stars).with_tooltip(f"{self.stars} GitHub stars")
        with Horizontal(id="forks"):
            yield Label("Forks")
            yield Digits(str(self.forks)).with_tooltip(f"{self.forks} Forks")

    def on_mount(self) -> None:
        self.tooltip = "Click to refresh"
        self.get_stars()

    def on_click(self) -> None:
        self.get_stars()


class WelcomeScreen(PageScreen):
    DEFAULT_CSS = """
    WelcomeScreen {
        align: center middle;
        Digits { width: auto; }
        Markdown {
            # background: $boost;
            margin: 2 2;
            padding: 1 2 0 2;
            max-width: 80;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield StarCount()
        with Center():
            yield Markdown(WHAT_IS_TEXTUAL_MD)
        yield Footer()
