import pytest

from textual import constants
from textual.app import App
from textual.constants import _get_textual_animations


@pytest.mark.parametrize(
    ["env_variable", "value"],
    [
        ("", "full"),  # default
        ("FULL", "full"),
        ("BASIC", "basic"),
        ("NONE", "none"),
        ("garbanzo beans", "full"),  # fallback
    ],
)
def test__get_textual_animations(monkeypatch, env_variable, value):  # type: ignore
    """Test that we parse the correct values from the env variable."""
    monkeypatch.setenv("TEXTUAL_ANIMATIONS", env_variable)
    assert _get_textual_animations() == value


@pytest.mark.parametrize(
    ["value"],
    [("full",), ("basic",), ("none",)],
)
def test_app_show_animations(monkeypatch, value):  # type: ignore
    """Test that the app gets the value of `show_animations` correctly."""
    monkeypatch.setattr(constants, "TEXTUAL_ANIMATIONS", value)
    app = App()
    assert app.animation_level == value
