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


async def test_setting_language_to_none():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)
        text_area.language = None
        assert text_area.language is None


@pytest.mark.syntax
async def test_setting_unknown_language():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        with pytest.raises(LanguageDoesNotExist):
            text_area.language = "this-language-doesnt-exist"


@pytest.mark.syntax
async def test_register_language():
    app = TextAreaApp()

    async with app.run_test():
        text_area = app.query_one(TextArea)

        from textual._tree_sitter import get_language

        language = get_language("python")
        assert language is not None
        # ...and register it with no highlights
        text_area.register_language("python-test", language, "")

        assert "python-test" in text_area.available_languages
        text_area.language = "python-test"
        assert text_area.language == "python-test"


@pytest.mark.syntax
async def test_update_highlight_query():
    app = TextAreaApp()
    async with app.run_test():
        text_area = app.query_one(TextArea)

        # Before registering the language, we have highlights as expected.
        assert len(text_area._highlights) > 0

        # Overwriting the highlight query for Python...
        text_area.update_highlight_query("python", "")

        # We've overridden the highlight query with a blank one, so there are no highlights.
        assert text_area._highlights == {}
