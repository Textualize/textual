from textual.widgets._input import _InputRenderable, Input


def test_input_renderable():
    input_widget = Input(value="a1あ１１bcdaef１２３a1a")

    renderable_cursor = _InputRenderable(input_widget, cursor_visible=True)
    renderable_no_cursor = _InputRenderable(input_widget, cursor_visible=False)
