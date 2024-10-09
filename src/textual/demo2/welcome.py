from importlib.metadata import version

import httpx

from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.demo2.page import Page
from textual.reactive import reactive
from textual.widgets import Digits, Label, Markdown

WHAT_IS_TEXTUAL = """\
### Turbo charge your developers!

* Build sophisticated applications — fast!
* No front-end skills required.
* Elegant Python API from the developer of [Rich](https://github.com/Textualize/rich).


* Deploy Textual as a terminal application, over SSH, *or* a [web application](https://github.com/Textualize/textual-web)!
"""


class StarCount(Vertical):
    DEFAULT_CSS = """
    StarCount {
        dock: top;
        height: 5;
        border-bottom: hkey $background;
        border-top: hkey $background;
        layout: horizontal;
        Layout {
            margin-top: 1;
        }
        background: $boost;
        padding: 0 1;
        color: $warning;
        Label {
            text-style: bold;
        }
        LoadingIndicator {
            background: transparent !important;
        }
    }
    """
    stars = reactive(25251, recompose=True)
    forks = reactive(776, recompose=True)

    @work
    async def get_stars(self):
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

    def on_mount(self) -> None:
        self.loading = True
        self.get_stars()

    def compose(self) -> ComposeResult:
        def thousands(number: int) -> str:
            if number > 2000:
                return f"{number / 1000:.1f}K "
            return str(number)

        with Horizontal():
            yield Label("GitHub ★ ")
            yield Digits(thousands(self.stars)).with_tooltip(
                f"{self.stars} GitHub stars"
            )
            yield Label("Forks ")
            yield Digits(str(self.forks)).with_tooltip(f"{self.forks} Forks")


class WelcomePage(Page):
    DEFAULT_CSS = """
    WelcomePage {
        align: center middle;
        Digits {
            width: auto;
           
        }
        Collapsible {
            margin: 2 4;
        }
        Markdown {
            background: $boost;
            margin: 2 2;
            padding: 1 2 0 2;
            max-width: 80;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield StarCount()
        with Center():
            yield Label("Textual")
        with Center():
            yield Digits(version("textual"))
        with Center():
            yield Label("The [i]lean application[/i] framework")
        with Center():
            yield Markdown(WHAT_IS_TEXTUAL)
