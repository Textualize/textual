"""Test https://github.com/Textualize/textual/issues/4248"""

from textual.app import App, ComposeResult
from textual.widgets import Label


async def test_issue_4248() -> None:
    """Various forms of click parameters should be fine."""

    bumps = 0

    class ActionApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Label("[@click=]click me and crash[/]", id="no-params")
            yield Label("[@click=()]click me and crash[/]", id="empty-params")
            yield Label("[@click=foobar]click me[/]", id="unknown-sans-parens")
            yield Label("[@click=foobar()]click me[/]", id="unknown-with-parens")
            yield Label("[@click=app.bump]click me[/]", id="known-sans-parens")
            yield Label("[@click=app.bump()]click me[/]", id="known-empty-parens")
            yield Label("[@click=app.bump(100)]click me[/]", id="known-with-param")

        def action_bump(self, by_value: int = 1) -> None:
            nonlocal bumps
            bumps += by_value

    app = ActionApp()
    async with app.run_test() as pilot:
        assert bumps == 0
        await pilot.click("#no-params")
        assert bumps == 0
        await pilot.click("#empty-params")
        assert bumps == 0
        await pilot.click("#unknown-sans-parens")
        assert bumps == 0
        await pilot.click("#unknown-with-parens")
        assert bumps == 0
        await pilot.click("#known-sans-parens")
        assert bumps == 1
        await pilot.click("#known-empty-parens")
        assert bumps == 2
        await pilot.click("#known-with-param")
        assert bumps == 102
