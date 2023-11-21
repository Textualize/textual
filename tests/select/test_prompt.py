from rich.text import Text

from textual.app import App
from textual.widgets import Select, Static
from textual.widgets._select import SelectCurrent, SelectOverlay


async def test_reactive_prompt_change():
    """Regression test for https://github.com/Textualize/textual/issues/2983"""

    class SelectApp(App):
        def compose(self):
            yield Select[int](
                [(str(n), n) for n in range(3)],
                prompt="Old prompt",
            )

    app = SelectApp()
    async with app.run_test() as pilot:
        select_widget = pilot.app.query_one(Select)
        select_current = select_widget.query_one(SelectCurrent)
        select_current_label = select_current.query_one("#label", Static)
        select_overlay = select_widget.query_one(SelectOverlay)

        assert select_current_label.renderable == Text("Old prompt")
        assert select_overlay._options[0].prompt == Text("Old prompt")

        select_widget.prompt = "New prompt"
        assert select_current_label.renderable == Text("New prompt")
        assert select_overlay._options[0].prompt == Text("New prompt")


async def test_reactive_prompt_change_when_allow_blank_is_false():
    class SelectApp(App):
        def compose(self):
            yield Select[int](
                [(str(n), n) for n in range(3)],
                prompt="Old prompt",
                allow_blank=False,
            )

    app = SelectApp()
    async with app.run_test() as pilot:
        select_widget = pilot.app.query_one(Select)
        select_current = select_widget.query_one(SelectCurrent)
        select_current_label = select_current.query_one("#label", Static)
        select_overlay = select_widget.query_one(SelectOverlay)

        assert select_current_label.renderable == Text("0")
        assert select_overlay._options[0].prompt == "0"

        select_widget.prompt = "New prompt"
        assert select_current_label.renderable == Text("0")
        assert select_overlay._options[0].prompt == "0"
