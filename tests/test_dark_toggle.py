from textual.app import App


class OnLoadDarkSwitch(App[None]):
    """App for testing toggling dark mode in on_load."""

    def on_load(self) -> None:
        self.dark = not self.dark


async def test_toggle_dark_on_load() -> None:
    """It should be possible to toggle dark mode in on_load."""
    async with OnLoadDarkSwitch().run_test() as pilot:
        assert not pilot.app.dark


class OnMountDarkSwitch(App[None]):
    """App for testing toggling dark mode in on_mount."""

    def on_mount(self) -> None:
        self.dark = not self.dark


async def test_toggle_dark_on_mount() -> None:
    """It should be possible to toggle dark mode in on_mount."""
    async with OnMountDarkSwitch().run_test() as pilot:
        assert not pilot.app.dark


class ActionDarkSwitch(App[None]):
    """App for testing toggling dark mode from an action."""

    BINDINGS = [("d", "toggle", "Toggle Dark Mode")]

    def action_toggle(self) -> None:
        self.dark = not self.dark


async def test_toggle_dark_in_action() -> None:
    """It should be possible to toggle dark mode with an action."""
    async with OnMountDarkSwitch().run_test() as pilot:
        await pilot.press("d")
        assert not pilot.app.dark
