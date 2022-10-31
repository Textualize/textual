import sys

import pytest

from textual.app import App, ScreenStackError
from textual.screen import Screen

skip_py310 = pytest.mark.skipif(
    sys.version_info.minor == 10 and sys.version_info.major == 3,
    reason="segfault on py3.10",
)


@skip_py310
@pytest.mark.asyncio
async def test_screens():

    app = App()
    app._set_active()

    with pytest.raises(ScreenStackError):
        app.screen

    assert not app._installed_screens

    screen1 = Screen(name="screen1")
    screen2 = Screen(name="screen2")
    screen3 = Screen(name="screen3")

    # installs screens
    app.install_screen(screen1, "screen1")
    app.install_screen(screen2, "screen2")

    # Check they are installed
    assert app.is_screen_installed("screen1")
    assert app.is_screen_installed("screen2")

    assert app.get_screen("screen1") is screen1
    with pytest.raises(KeyError):
        app.get_screen("foo")

    # Check screen3 is not installed
    assert not app.is_screen_installed("screen3")

    # Installs screen3
    app.install_screen(screen3, "screen3")
    # Confirm installed
    assert app.is_screen_installed("screen3")

    # Check screen stack is empty
    assert app.screen_stack == []
    # Push a screen
    app.push_screen("screen1")
    # Check it is on the stack
    assert app.screen_stack == [screen1]
    # Check it is current
    assert app.screen is screen1

    # Switch to another screen
    app.switch_screen("screen2")
    # Check it has changed the stack and that it is current
    assert app.screen_stack == [screen2]
    assert app.screen is screen2

    # Push another screen
    app.push_screen("screen3")
    assert app.screen_stack == [screen2, screen3]
    assert app.screen is screen3

    # Pop a screen
    assert app.pop_screen() is screen3
    assert app.screen is screen2
    assert app.screen_stack == [screen2]

    # Uninstall screens
    app.uninstall_screen(screen1)
    assert not app.is_screen_installed(screen1)
    app.uninstall_screen("screen3")
    assert not app.is_screen_installed(screen1)

    # Check we can't uninstall a screen on the stack
    with pytest.raises(ScreenStackError):
        app.uninstall_screen(screen2)

    # Check we can't pop last screen
    with pytest.raises(ScreenStackError):
        app.pop_screen()

    screen1.remove()
    screen2.remove()
    screen3.remove()
    await app._shutdown()
