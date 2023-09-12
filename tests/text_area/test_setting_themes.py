import pytest

from textual._text_area_theme import TextAreaTheme
from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets._text_area import ThemeDoesNotExist


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea("print('hello')", language="python")


async def test_default_theme():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.theme is None


async def test_setting_builtin_themes():
    class MyTextAreaApp(App):
        def compose(self) -> ComposeResult:
            yield TextArea("print('hello')", language="python", theme="vscode_dark")

    app = MyTextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.theme == "vscode_dark"

        text_area.theme = "monokai"
        assert text_area.theme == "monokai"


async def test_setting_theme_to_none():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.theme = None
        assert text_area.theme is None
        # When theme is None, we use the default theme.
        assert text_area._theme.name == TextAreaTheme.default().name


async def test_setting_unknown_theme_raises_exception():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        with pytest.raises(ThemeDoesNotExist):
            text_area.theme = "this-theme-doesnt-exist"


async def test_registering_and_setting_theme():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.register_theme(TextAreaTheme("my-theme"))

        assert "my-theme" in text_area.available_themes

        text_area.theme = "my-theme"

        assert text_area.theme == "my-theme"
