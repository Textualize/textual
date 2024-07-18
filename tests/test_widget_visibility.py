from textual.app import App, ComposeResult
from textual.widgets import Label


async def test_hide() -> None:
    """Check that setting visibility produces Hide messages."""
    # https://github.com/Textualize/textual/issues/3460
    visibility: list[bool] = []

    class ShowHideLabel(Label):
        def on_show(self) -> None:
            visibility.append(True)

        def on_hide(self) -> None:
            visibility.append(False)

    class ShowHideApp(App[None]):
        BINDINGS = [("space", "toggle_label")]

        def compose(self) -> ComposeResult:
            yield ShowHideLabel("Here I am")

        def action_toggle_label(self) -> None:
            self.query_one(ShowHideLabel).visible = not self.query_one(
                ShowHideLabel
            ).visible

    app = ShowHideApp()
    async with app.run_test() as pilot:
        assert visibility == [True]
        await pilot.press("space")
        assert visibility == [True, False]
        await pilot.press("space")
        assert visibility == [True, False, True]
