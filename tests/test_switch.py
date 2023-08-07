from textual.app import App, ComposeResult
from textual.widgets import Switch


async def test_switch_click_doesnt_bubble_up():
    """Regression test for https://github.com/Textualize/textual/issues/2366"""

    class SwitchApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Switch()

        async def on_click(self) -> None:
            raise AssertionError(
                "The app should never receive a click event when Switch is clicked."
            )

    async with SwitchApp().run_test() as pilot:
        await pilot.click(Switch)
