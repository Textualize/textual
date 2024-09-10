from __future__ import annotations

from pathlib import Path

import pytest

from textual.app import App

APP_DIR = Path(__file__).parent


class RelativePathObjectApp(App[None]):
    CSS_PATH = Path("test.tcss")


class RelativePathStrApp(App[None]):
    CSS_PATH = "test.tcss"


class AbsolutePathObjectApp(App[None]):
    CSS_PATH = Path("/tmp/test.tcss")


class AbsolutePathStrApp(App[None]):
    CSS_PATH = "/tmp/test.tcss"


class ListPathApp(App[None]):
    CSS_PATH = ["test.tcss", Path("/another/path.tcss")]


@pytest.mark.parametrize(
    "app_class,expected_css_path_attribute",
    [
        (RelativePathObjectApp, [APP_DIR / "test.tcss"]),
        (RelativePathStrApp, [APP_DIR / "test.tcss"]),
        (AbsolutePathObjectApp, [Path("/tmp/test.tcss")]),
        (AbsolutePathStrApp, [Path("/tmp/test.tcss")]),
        (ListPathApp, [APP_DIR / "test.tcss", Path("/another/path.tcss")]),
    ],
)
def test_css_paths_of_various_types(app_class, expected_css_path_attribute):
    app = app_class()
    assert app.css_path == [path.absolute() for path in expected_css_path_attribute]
