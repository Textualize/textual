from textual.app import App, ComposeResult
from textual.widgets import Log


def test_process_line():
    log = Log()
    assert log._process_line("foo") == "foo"
    assert log._process_line("foo\t") == "foo     "
    assert log._process_line("\0foo") == "�foo"


async def test_disabled_log_no_attribute_error() -> None:
    """Ensure that initializing the log with disabled=True does not
    raise an AttributeError.
    Regression test for https://github.com/Textualize/textual/issues/5028
    """

    class DisabledLogApp(App):
        def compose(self) -> ComposeResult:
            yield Log(disabled=True)

    async with DisabledLogApp().run_test() as pilot:
        # If no exception is raised, the test will pass
        log = pilot.app.query_one(Log)
        assert log.disabled == True
