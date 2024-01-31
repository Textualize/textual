import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label

CSS_PATH = (Path(__file__) / "../css_reloading.tcss").resolve()


class BaseScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Label("I am the base screen")


class TopScreen(Screen[None]):
    DEFAULT_CSS = """
    TopScreen {
        opacity: 1;
        background: green 0%;
    }
    """


class MyApp(App[None]):
    CSS_PATH = CSS_PATH

    def on_mount(self) -> None:
        self.push_screen(BaseScreen())
        self.push_screen(TopScreen())


async def test_css_reloading_applies_to_non_top_screen(monkeypatch) -> None:  # type: ignore
    """Regression test for https://github.com/Textualize/textual/issues/3931"""

    monkeypatch.setenv(
        "TEXTUAL", "debug"
    )  # This will make sure we create a file monitor.

    # Write some initial CSS.
    Path(CSS_PATH).write_text(
        """\
Label {
    height: 5;
    border: panel white;
}
"""
    )

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        first_label = pilot.app.screen_stack[-2].query(Label).first()
        # Sanity check.
        assert first_label.styles.height is not None
        assert first_label.styles.height.value == 5

        # Clear the CSS from the file.
        Path(CSS_PATH).write_text("/* This file has no rules intentionally. */\n")
        await pilot.pause()
        await pilot.app._on_css_change()
        # Height should fall back to 1.
        assert first_label.styles.height is not None
        assert first_label.styles.height.value == 1


async def test_css_reloading_file_not_found(monkeypatch, tmp_path):
    """Regression test for https://github.com/Textualize/textual/issues/3996

    Files can become temporarily unavailable during saving on certain environments.
    """
    monkeypatch.setenv("TEXTUAL", "debug")

    css_path = tmp_path / "test_css_reloading_file_not_found.tcss"
    with open(css_path, "w") as css_file:
        css_file.write("#a {color: red;}")

    class TextualApp(App):
        CSS_PATH = css_path

    app = TextualApp()
    async with app.run_test() as pilot:
        await pilot.app._on_css_change()
        os.remove(css_path)
        assert not css_path.exists()
        await pilot.app._on_css_change()
