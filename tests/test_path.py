from __future__ import annotations

from pathlib import Path

import pytest

from textual.app import App

APP_DIR = Path(__file__).parent


class RelativePathObjectApp(App[None]):
    CSS_PATH = Path("test.css")


class RelativePathStrApp(App[None]):
    CSS_PATH = "test.css"


class AbsolutePathObjectApp(App[None]):
    CSS_PATH = Path("/tmp/test.css")


class AbsolutePathStrApp(App[None]):
    CSS_PATH = "/tmp/test.css"


class ListPathApp(App[None]):
    CSS_PATH = ["test.css", Path("/another/path.css")]


@pytest.mark.parametrize(
    "app,expected_css_path_attribute",
    [
        (RelativePathObjectApp(), [APP_DIR / "test.css"]),
        (RelativePathStrApp(), [APP_DIR / "test.css"]),
        (AbsolutePathObjectApp(), [Path("/tmp/test.css")]),
        (AbsolutePathStrApp(), [Path("/tmp/test.css")]),
        (ListPathApp(), [APP_DIR / "test.css", Path("/another/path.css")]),
    ],
)
def test_css_paths_of_various_types(app, expected_css_path_attribute):
    assert app.css_path == [path.absolute() for path in expected_css_path_attribute]
