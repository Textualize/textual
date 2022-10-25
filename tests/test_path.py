from typing import Type
from pathlib import Path

from textual.app import App

class RelativePathObjectApp(App[None]):

    CSS_PATH = Path("test.css")

class RelativePathStrApp(App[None]):

    CSS_PATH = "test.css"

class AbsolutePathObjectApp(App[None]):

    CSS_PATH = Path("/tmp/test.css")

class AbsolutePathStrApp(App[None]):

    CSS_PATH = "/tmp/test.css"

def path_tester(obj_type: Type[App[None]], str_type: Type[App[None]], intended_result: Path) -> None:
    assert isinstance(obj_type().css_path,Path), (
        "CSS_PATH didn't stay as an object"
    )
    assert isinstance(str_type().css_path,Path), (
        "CSS_PATH wasn't converted from str to Path"
    )
    assert obj_type().css_path == intended_result, (
        "CSS_PATH doesn't match the intended result."
    )
    assert str_type().css_path == intended_result, (
        "CSS_PATH doesn't match the intended result."
    )
    assert str_type().css_path == obj_type().css_path, (
        "CSS_PATH str to Path conversion gave a different result"
    )

def test_relative_path():
    path_tester(RelativePathObjectApp, RelativePathStrApp, ((Path(__file__).absolute().parent ) / "test.css").absolute())

def test_absolute_path():
    path_tester(AbsolutePathObjectApp, AbsolutePathStrApp, Path("/tmp/test.css").absolute())
