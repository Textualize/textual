from __future__ import annotations

import sys

import pytest


pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Win32 console input is only available on Windows."
)

if sys.platform == "win32":
    from textual.drivers.win32 import KEY_EVENT_RECORD, _is_bare_modifier


def make_key_event(
    character: str, *, virtual_key_code: int = 0, control_key_state: int = 0x0010
) -> KEY_EVENT_RECORD:
    key_event = KEY_EVENT_RECORD()
    key_event.wVirtualKeyCode = virtual_key_code
    key_event.uChar.UnicodeChar = character
    key_event.dwControlKeyState = control_key_state
    return key_event


def test_bare_modifier_is_ignored() -> None:
    assert _is_bare_modifier(make_key_event("\x00"))


def test_ime_character_with_modifier_is_preserved() -> None:
    assert not _is_bare_modifier(make_key_event("\uff1f"))


def test_regular_virtual_key_is_preserved() -> None:
    assert not _is_bare_modifier(make_key_event("\x00", virtual_key_code=0x10))
