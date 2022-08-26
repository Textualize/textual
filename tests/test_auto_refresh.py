from time import time

from textual.app import App


class RefreshApp(App[float]):
    def __init__(self):
        self.count = 0
        super().__init__()

    def on_mount(self):
        self.start = time()
        self.auto_refresh = 0.1

    def _automatic_refresh(self):
        self.count += 1
        if self.count == 3:
            self.exit(time() - self.start)
        super()._automatic_refresh()


def test_auto_refresh():
    app = RefreshApp()

    elapsed = app.run(quit_after=1, headless=True)
    assert elapsed is not None
    # CI can run slower, so we need to give this a bit of margin
    assert 0.2 <= elapsed < 0.8
