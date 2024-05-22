from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label


async def test_links():
    """Regression test for https://github.com/Textualize/textual/issues/4536"""
    messages: list[str] = []

    class HomeScreen(Screen[None]):
        def compose(self) -> ComposeResult:
            yield Label("[@click=app.bell_message('hi')]Ring the bell![/]")

    class ScreenNamespace(App[None]):
        def get_default_screen(self) -> HomeScreen:
            return HomeScreen()

        def action_bell_message(self, message: str) -> None:
            nonlocal messages
            messages.append(message)

    async with ScreenNamespace().run_test() as pilot:
        await pilot.click(offset=(5, 0))
        assert messages == ["hi"]
