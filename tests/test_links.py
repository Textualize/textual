from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label


async def test_links() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4536"""
    messages: list[str] = []

    class LinkLabel(Label):
        def action_bell_message(self, message: str) -> None:
            nonlocal messages
            messages.append(f"label {message}")

    class HomeScreen(Screen[None]):
        def compose(self) -> ComposeResult:
            yield LinkLabel("[@click=app.bell_message('foo')]Ring the bell![/]")
            yield LinkLabel("[@click=screen.bell_message('bar')]Ring the bell![/]")
            yield LinkLabel("[@click=bell_message('baz')]Ring the bell![/]")

        def action_bell_message(self, message: str) -> None:
            nonlocal messages
            messages.append(f"screen {message}")

    class ScreenNamespace(App[None]):
        def get_default_screen(self) -> HomeScreen:
            return HomeScreen()

        def action_bell_message(self, message: str) -> None:
            nonlocal messages
            messages.append(f"app {message}")

    async with ScreenNamespace().run_test() as pilot:
        await pilot.click(offset=(5, 0))
        await pilot.click(offset=(5, 1))
        await pilot.click(offset=(5, 2))
        assert messages == ["app foo", "screen bar", "label baz"]
