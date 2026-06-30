import asyncio

import pytest

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input


class DefaultScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input()
        yield Input("Hello, world!")


class InputApp(App):
    DEFAULT_MODE = "default"
    MODES = {"default": DefaultScreen}


@pytest.mark.skipif(
    not hasattr(asyncio, "eager_task_factory"), reason="only occurs with eager tasks"
)
async def test_input_default_mode():
    """Test that Input in a DEFAULT_MODE Screen doesn't crash.

    Regression test for https://github.com/textualize/textual/issues/6444.

    """
    # changing this will not affect other tests since pytest-asyncio runs every function
    # in a new event loop by default
    asyncio.get_running_loop().set_task_factory(asyncio.eager_task_factory)
    async with InputApp().run_test():
        pass
