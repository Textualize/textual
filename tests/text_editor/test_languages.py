import sys

import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextEditor
from textual.widgets.text_editor import LanguageDoesNotExist


class TextEditorApp(App):
    def compose(self) -> ComposeResult:
        yield TextEditor("print('hello')", language="python")


async def test_setting_builtin_language_via_constructor():
    class MyTextEditorApp(App):
        def compose(self) -> ComposeResult:
            yield TextEditor("print('hello')", language="python")

    app = MyTextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        assert text_editor.language == "python"

        text_editor.language = "markdown"
        assert text_editor.language == "markdown"


async def test_setting_builtin_language_via_attribute():
    class MyTextEditorApp(App):
        def compose(self) -> ComposeResult:
            text_editor = TextEditor("print('hello')")
            text_editor.language = "python"
            yield text_editor

    app = MyTextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        assert text_editor.language == "python"

        text_editor.language = "markdown"
        assert text_editor.language == "markdown"


async def test_setting_language_to_none():
    app = TextEditorApp()
    async with app.run_test():
        text_editor = app.query_one(TextEditor)
        text_editor.language = None
        assert text_editor.language is None


async def test_setting_unknown_language():
    app = TextEditorApp()
    async with app.run_test():
        text_editor = app.query_one(TextEditor)

        with pytest.raises(LanguageDoesNotExist):
            text_editor.language = "this-language-doesnt-exist"


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="tree-sitter requires python3.8 or higher"
)
async def test_register_language():
    app = TextEditorApp()

    async with app.run_test():
        text_editor = app.query_one(TextEditor)

        from tree_sitter_languages import get_language

        language = get_language("elm")

        # ...and register it with no highlights
        text_editor.register_language(language, "")

        # Ensure that registered language is now available.
        assert "elm" in text_editor.available_languages

        # Switch to the newly registered language
        text_editor.language = "elm"

        assert text_editor.language == "elm"


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="tree-sitter requires python3.8 or higher"
)
async def test_register_language_existing_language():
    app = TextEditorApp()
    async with app.run_test():
        text_editor = app.query_one(TextEditor)

        # Before registering the language, we have highlights as expected.
        assert len(text_editor._highlights) > 0

        # Overwriting the highlight query for Python...
        text_editor.register_language("python", "")

        # We've overridden the highlight query with a blank one, so there are no highlights.
        assert text_editor._highlights == {}
