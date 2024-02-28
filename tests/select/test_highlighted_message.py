from __future__ import annotations

from textual import on
from textual.app import App
from textual.widgets import OptionList, Select


class SelectApp(App[None]):
    def __init__(self):
        super().__init__()
        self.highlighted_messages: list[str] = []

    def compose(self):
        yield Select[int]([(str(n), n) for n in range(3)])

    @on(OptionList.OptionHighlighted)
    @on(Select.SelectionHighlighted)
    def add_message(
        self,
        event: OptionList.OptionHighlighted | Select.SelectionHighlighted,
    ):
        self.highlighted_messages.append(event.__class__.__name__)


async def test_selection_highlighted_message():
    """Regression test for https://github.com/Textualize/textual/issues/4224

    A `Select.SelectionHighlighted` message should be posted when the
    highlighted option changes, instead of `OptionList.OptionHighlighted`
    bubbling."""

    app = SelectApp()
    async with app.run_test() as pilot:
        await pilot.press("down")
        assert app.highlighted_messages == ["SelectionHighlighted"]
