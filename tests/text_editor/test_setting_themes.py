import pytest

from textual._text_editor_theme import TextEditorTheme
from textual.app import App, ComposeResult
from textual.widgets import TextEditor
from textual.widgets._text_editor import ThemeDoesNotExist


class TextEditorApp(App):
    def compose(self) -> ComposeResult:
        yield TextEditor("print('hello')", language="python")


async def test_default_theme():
    app = TextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        assert text_editor.theme is None


async def test_setting_builtin_themes():
    class MyTextEditorApp(App):
        def compose(self) -> ComposeResult:
            yield TextEditor("print('hello')", language="python", theme="vscode_dark")

    app = MyTextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        assert text_editor.theme == "vscode_dark"

        text_editor.theme = "monokai"
        assert text_editor.theme == "monokai"


async def test_setting_theme_to_none():
    app = TextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        text_editor.theme = None
        assert text_editor.theme is None
        # When theme is None, we use the default theme.
        assert text_editor._theme.name == TextEditorTheme.default().name


async def test_setting_unknown_theme_raises_exception():
    app = TextEditorApp()
    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        with pytest.raises(ThemeDoesNotExist):
            text_editor.theme = "this-theme-doesnt-exist"


async def test_registering_and_setting_theme():
    app = TextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        text_editor.register_theme(TextEditorTheme("my-theme"))

        assert "my-theme" in text_editor.available_themes

        text_editor.theme = "my-theme"

        assert text_editor.theme == "my-theme"
