import sys

import pytest

from textual.app import App, SuspendNotSupported
from textual.drivers.headless_driver import HeadlessDriver


async def test_suspend_not_supported() -> None:
    """Suspending when not supported should raise an error."""
    async with App().run_test() as pilot:
        # Pilot uses the headless driver, the headless driver doesn't
        # support suspend, and so...
        with pytest.raises(SuspendNotSupported):
            with pilot.app.suspend():
                pass


async def test_suspend_supported(capfd: pytest.CaptureFixture[str]) -> None:
    """Suspending when supported should call the relevant driver methods."""

    calls: set[str] = set()

    class HeadlessSuspendDriver(HeadlessDriver):
        @property
        def is_headless(self) -> bool:
            return False

        @property
        def can_suspend(self) -> bool:
            return True

        def start_application_mode(self) -> None:
            nonlocal calls
            calls.add("start")

        def stop_application_mode(self) -> None:
            nonlocal calls
            calls.add("stop")

        def close(self) -> None:
            nonlocal calls
            calls.add("close")

    async with App(driver_class=HeadlessSuspendDriver).run_test(
        headless=False
    ) as pilot:
        calls = set()
        with pilot.app.suspend():
            _ = capfd.readouterr()  # Clear the existing buffer.
            print("USE THEM TOGETHER.", end="", flush=True)
            print("USE THEM IN PEACE.", file=sys.stderr, end="", flush=True)
            assert ("USE THEM TOGETHER.", "USE THEM IN PEACE.") == capfd.readouterr()
        assert calls == {"start", "stop", "close"}
