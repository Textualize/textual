"""Regression tests for event handler dispatch with specialized message types.

Verifies the three acceptance criteria:
1. @on(SpecializedButton.Pressed) fires only when a SpecializedButton is pressed.
2. @on(Button.Pressed) fires for both regular and specialized buttons (polymorphism).
3. Specialized-button handlers do NOT fire when a plain Button.Pressed is dispatched.
"""
from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button


class SpecializedButton(Button):
    """A button subclass that defines its own Pressed message type."""

    class Pressed(Button.Pressed):
        """Pressed message for SpecializedButton."""


class _ButtonApp(App):
    """Base app with both button types for dispatch tests."""

    def compose(self) -> ComposeResult:
        yield Button("Plain", id="plain")
        yield SpecializedButton("Special", id="special")


# ---------------------------------------------------------------------------
# AC-1 & AC-3: decorator-based handlers
# ---------------------------------------------------------------------------


async def test_specialized_handler_fires_only_for_specialized_button() -> None:
    """@on(SpecializedButton.Pressed) must not fire when a plain Button is pressed."""
    fired: list[str] = []

    class MyApp(_ButtonApp):
        @on(SpecializedButton.Pressed)
        def on_specialized(self, event: SpecializedButton.Pressed) -> None:
            fired.append(f"specialized:{type(event).__name__}")

    async with MyApp().run_test() as pilot:
        await pilot.click("#plain")
        await pilot.pause()

    assert fired == [], f"Expected no fires but got: {fired}"


async def test_specialized_handler_fires_for_specialized_button() -> None:
    """@on(SpecializedButton.Pressed) must fire when a SpecializedButton is pressed."""
    fired: list[str] = []

    class MyApp(_ButtonApp):
        @on(SpecializedButton.Pressed)
        def on_specialized(self, event: SpecializedButton.Pressed) -> None:
            fired.append(f"specialized:{type(event).__name__}")

    async with MyApp().run_test() as pilot:
        await pilot.click("#special")
        await pilot.pause()

    assert fired == ["specialized:Pressed"]


# ---------------------------------------------------------------------------
# AC-2: @on(Button.Pressed) fires for BOTH button types
# ---------------------------------------------------------------------------


async def test_parent_handler_fires_for_both_buttons() -> None:
    """@on(Button.Pressed) must fire for both plain and specialized buttons."""
    fired: list[str] = []

    class MyApp(_ButtonApp):
        @on(Button.Pressed)
        def on_any_button(self, event: Button.Pressed) -> None:
            fired.append(event.button.id or "?")

    async with MyApp().run_test() as pilot:
        await pilot.click("#plain")
        await pilot.click("#special")
        await pilot.pause()

    assert fired == ["plain", "special"]


# ---------------------------------------------------------------------------
# AC-1 & AC-2 combined: both handler types present simultaneously
# ---------------------------------------------------------------------------


async def test_both_handlers_with_specialized_button() -> None:
    """When both handlers exist, only Button.Pressed fires for the plain button,
    and both fire for the specialized button."""
    fired: list[str] = []

    class MyApp(_ButtonApp):
        @on(Button.Pressed)
        def on_any_button(self, event: Button.Pressed) -> None:
            fired.append(f"parent:{event.button.id}")

        @on(SpecializedButton.Pressed)
        def on_specialized(self, event: SpecializedButton.Pressed) -> None:
            fired.append(f"specialized:{event.button.id}")

    async with MyApp().run_test() as pilot:
        await pilot.click("#plain")
        await pilot.pause()
        plain_fires = list(fired)
        fired.clear()

        await pilot.click("#special")
        await pilot.pause()
        special_fires = list(fired)

    # Plain button: only parent handler fires
    assert plain_fires == ["parent:plain"], f"plain: {plain_fires}"

    # Specialized button: both parent and specialized handler fire
    assert "parent:special" in special_fires, f"special: {special_fires}"
    assert "specialized:special" in special_fires, f"special: {special_fires}"


# ---------------------------------------------------------------------------
# AC-3 regression: naming-convention specialized handler is exact-type only
# ---------------------------------------------------------------------------


async def test_naming_convention_specialized_handler_not_for_plain() -> None:
    """on_specialized_button_pressed must not fire when a plain Button is pressed."""
    fired: list[str] = []

    class MyApp(_ButtonApp):
        def on_specialized_button_pressed(
            self, event: SpecializedButton.Pressed
        ) -> None:
            fired.append("specialized")

    async with MyApp().run_test() as pilot:
        await pilot.click("#plain")
        await pilot.pause()

    assert fired == []
