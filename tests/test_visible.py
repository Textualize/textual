from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget


async def test_visibility_changes() -> None:
    """Test changing visibility via code and CSS.

    See https://github.com/Textualize/textual/issues/1355 as the motivation for these tests.
    """

    class VisibleTester(App[None]):
        """An app for testing visibility changes."""

        CSS = """
        Widget {
            height: 1fr;
        }
        .hidden {
            visibility: hidden;
        }
        """

        def compose(self) -> ComposeResult:
            yield VerticalScroll(
                Widget(id="keep"), Widget(id="hide-via-code"), Widget(id="hide-via-css")
            )

    async with VisibleTester().run_test() as pilot:
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is True
        assert pilot.app.query_one("#hide-via-css").visible is True

        pilot.app.query_one("#hide-via-code").styles.visibility = "hidden"
        await pilot.pause(0)
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is False
        assert pilot.app.query_one("#hide-via-css").visible is True

        pilot.app.query_one("#hide-via-css").set_class(True, "hidden")
        await pilot.pause(0)
        assert pilot.app.query_one("#keep").visible is True
        assert pilot.app.query_one("#hide-via-code").visible is False
        assert pilot.app.query_one("#hide-via-css").visible is False


async def test_visible_is_inherited() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3071"""

    class InheritedVisibilityApp(App[None]):
        CSS = """
        #four {
            visibility: visible;
        }

        #six {
            visibility: hidden;
        }
        """

        def compose(self):
            yield Widget(id="one")
            with VerticalScroll(id="two"):
                yield Widget(id="three")
                with VerticalScroll(id="four"):
                    yield Widget(id="five")
                    with VerticalScroll(id="six"):
                        yield Widget(id="seven")

    app = InheritedVisibilityApp()
    async with app.run_test():
        assert app.query_one("#one").visible
        assert app.query_one("#two").visible
        assert app.query_one("#three").visible
        assert app.query_one("#four").visible
        assert app.query_one("#five").visible
        assert not app.query_one("#six").visible
        assert not app.query_one("#seven").visible
