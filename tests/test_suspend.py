import sys

from pytest import CaptureFixture

from textual.app import App


async def test_suspend(capfd: CaptureFixture[str]) -> None:
    async with App().run_test() as pilot:
        with pilot.app.suspend():
            _ = capfd.readouterr()  # clear existing buffer

            print("foo")
            print("bar", file=sys.stderr)

            assert ("foo\n", "bar\n") == capfd.readouterr()
