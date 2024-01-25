import pytest

from textual.app import App
from textual.constants import AnimationsEnum, _get_textual_animations


@pytest.mark.parametrize(
    ["env_variable", "value"],
    [
        ("", AnimationsEnum.FULL),  # default
        ("FULL", AnimationsEnum.FULL),
        ("BASIC", AnimationsEnum.BASIC),
        ("NONE", AnimationsEnum.NONE),
        ("garbanzo beans", AnimationsEnum.FULL),  # fallback
    ],
)
def test__get_textual_animations(monkeypatch, env_variable, value):  # type: ignore
    """Test that we parse the correct values from the env variable."""
    monkeypatch.setenv("TEXTUAL_ANIMATIONS", env_variable)
    assert _get_textual_animations() == value


@pytest.mark.parametrize(
    ["env_variable", "value"],
    [
        ("", AnimationsEnum.FULL),  # default
        ("FULL", AnimationsEnum.FULL),
        ("BASIC", AnimationsEnum.BASIC),
        ("NONE", AnimationsEnum.NONE),
        ("garbanzo beans", AnimationsEnum.FULL),  # fallback
    ],
)
def test_app_show_animations(monkeypatch, env_variable, value):  # type: ignore
    """Test that the app gets the value of `show_animations` correctly."""
    monkeypatch.setenv("TEXTUAL_ANIMATIONS", env_variable)
    app = App()
    assert app.show_animations == value
