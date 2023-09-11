import pytest

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.widgets.text_area import LanguageDoesNotExist


class TextAreaApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea("print('hello')", language="python")


async def test_setting_builtin_language_via_constructor():
    class MyTextAreaApp(App):
        def compose(self) -> ComposeResult:
            yield TextArea("print('hello')", language="python")

    app = MyTextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.language == "python"

        text_area.language = "markdown"
        assert text_area.language == "markdown"


async def test_setting_builtin_language_via_attribute():
    class MyTextAreaApp(App):
        def compose(self) -> ComposeResult:
            text_area = TextArea("print('hello')")
            text_area.language = "python"
            yield text_area

    app = MyTextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)
        assert text_area.language == "python"

        text_area.language = "markdown"
        assert text_area.language == "markdown"


async def test_setting_unknown_language():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        with pytest.raises(LanguageDoesNotExist):
            text_area.language = "this-language-doesnt-exist"


async def test_register_language():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)

        # Get the language from py-tree-sitter-languages...
        from tree_sitter_languages import get_language

        language = get_language("elm")

        # ...and register it with no highlights
        text_area.register_language(language, "")

        # Ensure that registered language is now available.
        assert "elm" in text_area.available_languages

        # Switch to the newly registered language
        text_area.language = "elm"

        assert text_area.language == "elm"


async def test_register_language_existing_language():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # Before registering the language, we have highlights as expected.
        assert len(text_area._highlights) > 0

        # Overwriting the highlight query for Python...
        text_area.register_language("python", "")

        # We've overridden the highlight query with a blank one, so there are no highlights.
        assert text_area._highlights == {}
