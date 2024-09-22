from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import RichLog


def test_make_renderable_expand_tabs():
    # Regression test for https://github.com/Textualize/textual/issues/3007
    text_log = RichLog()
    renderable = text_log._make_renderable("\tfoo")
    assert isinstance(renderable, Text)
    assert renderable.plain == "        foo"


async def test_disabled_rich_log_no_attribute_error() -> None:
    """Ensure that initializing the RichLog with disabled=True does not
    raise an AttributeError.

    Regression test for https://github.com/Textualize/textual/issues/5028
    """

    class DisabledRichLogApp(App):
        def compose(self) -> ComposeResult:
            yield RichLog(disabled=True)

    async with DisabledRichLogApp().run_test() as pilot:
        # If no exception is raised, the test will pass
        log = pilot.app.query_one(RichLog)
        assert log.disabled == True
