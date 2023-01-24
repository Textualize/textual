import sys

from pytest import CaptureFixture

from textual.app import App


async def test_suspend(capfd: CaptureFixture[str]) -> None:
    async with App().run_test() as pilot:
        with pilot.app.suspend():
            _ = capfd.readouterr()  # clear existing buffer

            print("foo", end="", flush=True)
            print("bar", file=sys.stderr, end="", flush=True)

            assert ("foo", "bar") == capfd.readouterr()
