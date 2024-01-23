import pytest

from textual.app import App, SuspendNotSupported


async def test_suspend_not_supported() -> None:
    """Suspending when not supported should raise an error."""
    async with App().run_test() as pilot:
        # Pilot uses the headless driver, the headless driver doesn't
        # support suspend, and so...
        with pytest.raises(SuspendNotSupported):
            with pilot.app.suspend():
                pass
