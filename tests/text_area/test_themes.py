import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea("print('hello')", language="python")


@pytest.mark.xfail(reason="refactoring")
async def test_default_theme():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.theme == "monokai"


async def test_setting_theme_via_constructor():
    class MyTextAreaApp(App):
        def compose(self) -> ComposeResult:
            yield TextArea("print('hello')", language="python", theme="vscode_dark")

    app = MyTextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.theme == "vscode_dark"
