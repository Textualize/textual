from __future__ import annotations

import functools
import re
from typing import Any, Callable, Generator, Iterable, Literal, Set, Tuple

from . import events, messages
from ._ansi_sequences import ANSI_SEQUENCES_KEYS
from ._parser import Awaitable, Parser, TokenCallback
from .keys import Keys, _character_to_key

_ESCAPE = "\x1b"

# Usually "alt" or "meta"
ALT_NAME = "alt"

# Sequences that define the beginning and end of bracketed pasting.
_BRACKETED_PASTE_START = "\x1b[200~"
_BRACKETED_PASTE_END = "\x1b[201~"

# Maximum length of any escape sequence.
_MAX_ESCAPE_SEQUENCE_LENGTH = 20


class XTermParser(Parser[events.Event]):
    _re_terminal_mode_report = re.compile(
        # fmt: off
        r"^\x1b\[\?"
        r"(?P<mode_id>\d+);"
        r"(?P<setting_parameter>\d)"
        r"\$y$"
        # fmt: on
    )
    _re_mouse_event = re.compile(
        # fmt: off
        r"^\x1b\["
        r"<(?P<buttons>\d+);"
        r"(?P<x>\d+);"
        r"(?P<y>\d+)"
        r"(?P<state>[Mm])"
        r"$"
        # fmt: on
    )

    def __init__(
        self,
        more_data: Callable[[], bool],
        debug: Callable[[str], None] | None = None,
    ) -> None:
        self.more_data = more_data
        self.last_x = 0
        self.last_y = 0
        self._debug_logger = debug
        super().__init__()

    def debug_log(self, *args: Any) -> None:  # pragma: no cover
        if self._debug_logger is not None:
            message = " ".join((str(arg) for arg in args))
            self._debug_logger(message)

    def feed(self, data: str) -> Iterable[events.Event]:
        self.debug_log(f"FEED {data!r}")
        return super().feed(data)

    def _more_data_available(self) -> bool:
        # Bytes have been read but not consumed yet?
        peek = yield self.peek_buffer()
        if peek:
            return True

        # Bytes buffered by the OS?
        more_data = self.more_data()
        if more_data:
            return True

        return False

    @functools.cached_property
    def _known_escape_sequences(self) -> set[str]:
        return {
            sequence
            for sequence in ANSI_SEQUENCES_KEYS
            if sequence[0] == _ESCAPE and len(sequence) >= 2
        }.union(
            {
                # We only need _BRACKETED_PASTE_START to detect the beginning of
                # a paste. _parse_bracketed_paste() finds _BRACKETED_PASTE_END.
                _BRACKETED_PASTE_START,
            }
        )

    def _sequence_to_key_events(self, sequence: str) -> Iterable[events.Key]:
        """Translate sequence of characters to sequence of Key events.

        Args:
            sequence: Complete sequence of characters.

        Returns:
            Keys
        """
        keys = ANSI_SEQUENCES_KEYS.get(sequence)
        if keys is not None:
            if len(keys) == 2 and keys[0] == Keys.Escape:
                # Alt key combination from special sequence, e.g. Alt+F1.
                yield events.Key(
                    key=f"{ALT_NAME}+{keys[1].value}",
                    character=None,
                )
            else:
                # Sequence maps to a single key or a sequence that doesn't
                # start with Escape/Alt.
                for key in keys:
                    yield events.Key(
                        key=key.value,
                        character=sequence if len(sequence) == 1 else None,
                    )

        elif len(sequence) == 2 and sequence[0] == _ESCAPE:
            # Regular Alt combination (e.g. Alt+f, Alt+Enter) or Alt+Ctrl
            # combination (e.g. Alt+Ctrl+d).
            if sequence[1] in ANSI_SEQUENCES_KEYS:
                # The byte after Alt is a control character or otherwise special
                # (Enter, Space, Backspace, Ctrl+c, etc) and we need the name,
                # not the literal byte.
                keys = ANSI_SEQUENCES_KEYS[sequence[1]]
                assert len(keys) == 1, keys
                key_name = keys[0].value
            else:
                # ASCII or Unicode character with a length of 1, e.g. "a", "%",
                # "ñ", etc.
                key_name = sequence[1]
            yield events.Key(
                key=f"{ALT_NAME}+{key_name}",
                character=None,
            )

        elif len(sequence) == 1:
            # Not an escape sequence.
            name = _character_to_key(sequence)
            yield events.Key(name, sequence)

        else:
            self.debug_log("Ignoring unknown private escape sequence:", repr(sequence))

        # Any other sequences should be handled by a _parse_*() method or they
        # will be silently ignored.

    def _send_sequence_as_key_events(
        self, sequence: str, on_token: TokenCallback
    ) -> None:
        for event in self._sequence_to_key_events(sequence):
            self.debug_log(event)
            on_token(event)

    # Match escape sequences.
    #
    # - An escape sequence starts with 0x1b followed by ASCII characters from
    #   0x20 (" ") to 0x7e ("~") (inclusive).
    #
    # - Alt+Enter and Alt+Ctrl+<letter> sends 0x1b followed by a ASCII control
    #   character from 0x00 to 0x1f (inclusive). Note that Backspace (0x7f) is
    #   outside of that range.
    #
    # - Escape key sends 0x1b. Alt+Escape sends 0x1b0x1b.
    #
    # - VT terminals (rxvt) send two 0x1b for many Alt combinations,
    #   e.g. Alt+F1.
    #
    # References:
    # https://en.wikipedia.org/wiki/ANSI_escape_code#Terminal_input_sequences
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    _re_escape_sequence = re.compile(r"^\x1b{1,2}[\x21-\x7e]*$")

    @functools.cached_property
    def _re_alt_key_combination_only(self) -> re.Pattern:
        # Match escape sequences that cannot be the beginning of any sequence
        # from ANSI_SEQUENCES_KEYS. For example, "\x1bf" should match because no
        # escape sequence begins with "\x1bf", but many escape sequences begin
        # with "\x1b[", so that must not match.
        continuation_characters = {
            sequence[1] for sequence in self._known_escape_sequences
        }
        return re.compile(
            # fmt: off
            r"^" r"\x1b[^"
            + re.escape("".join(continuation_characters))
            + "]$"
            + r"$"
            # fmt: on
        )

    def parse(self, on_token: TokenCallback) -> Generator[Awaitable, str, None]:
        """Read input and pass each complete sequence to _parse(). A complete
        sequence can be a single character (e.g. "a", "ñ" or "\x03" / Ctrl+c)
        or an escape ("\x1b") followed by one or more non-escape characters.
        """
        sequence: str = ""
        remainder: str = ""
        while True:
            sequence = remainder
            remainder = ""
            # self.debug_log("parse(): old sequence:", repr(sequence))
            # self.debug_log("parse(): read1: ...")
            if not sequence:
                sequence += yield self.read1()
                self.debug_log("parse(): Read sequence:", repr(sequence))

            if sequence[0] == _ESCAPE:
                # Read until sequence is complete or reading times out.
                while (yield from self._more_data_available()):
                    sequence += yield self.read1()

                    # Optimization that triggers mouse events immediately
                    # without waiting for a timeout.
                    if self._re_mouse_event.search(sequence):
                        self.debug_log("parse(): Mouse sequence:", repr(sequence))
                        break

                    # Optimization that triggers ANSI_SEQUENCES_KEYS immediately
                    # without waiting for a timeout.
                    #
                    # NOTE: This is problematic if any sequence in
                    #       ANSI_SEQUENCES_KEYS starts with the same characters
                    #       as any other complete sequence. For example, with
                    #       the sequences "\x1bfoo" and "\x1bfooO", "\x1bfooO"
                    #       is impossible to reach.
                    elif sequence in self._known_escape_sequences:
                        self.debug_log(
                            "parse(): Known escape sequence:", repr(sequence)
                        )
                        break

                    # Optimization that triggers most Alt key combinations
                    # immediately without waiting for a timeout.
                    elif self._re_alt_key_combination_only.search(sequence):
                        self.debug_log("parse(): Alt key combination:", repr(sequence))
                        break

                    # Continue completing escape sequence until we find an
                    # invalid character.
                    elif not self._re_escape_sequence.search(sequence):
                        # We have read one character too much, the one that
                        # tells us the unknown escape sequence ended.
                        remainder = sequence[-1:]
                        sequence = sequence[:-1]
                        self.debug_log(
                            "parse(): Escape sequence ended:", repr(sequence)
                        )
                        break

                    else:
                        self.debug_log(
                            "parse(): Unknown escape sequence continued:",
                            repr(sequence),
                        )

                self.debug_log(
                    "parse(): sequence:", repr(sequence), "remainder:", repr(remainder)
                )
                yield from self._parse(sequence, on_token)
                sequence = ""

            else:
                self.debug_log("parse(): Not an escape sequence:", repr(sequence))
                yield from self._parse(sequence, on_token)
                sequence = ""

    def _parse(
        self,
        sequence: str,
        on_token: TokenCallback,
    ) -> Generator[Awaitable, str, None]:
        if sequence == _BRACKETED_PASTE_START:
            self.debug_log("Bracketed paste starts:", repr(sequence))
            yield from self._parse_bracketed_paste(on_token)

        elif mouse_event_match := self._re_mouse_event.match(sequence):
            self._parse_mouse_event(
                buttons=int(mouse_event_match["buttons"]),
                position=(
                    int(mouse_event_match["x"]) - 1,
                    int(mouse_event_match["y"]) - 1,
                ),
                state=mouse_event_match["state"],
                on_token=on_token,
            )

        # Mode report (i.e. the terminal saying it supports a mode we requested)
        elif mode_report_match := self._re_terminal_mode_report.match(sequence):
            self._parse_mode_report(
                mode_id=mode_report_match["mode_id"],
                setting_parameter=int(mode_report_match["setting_parameter"]),
                on_token=on_token,
            )

        else:
            self._send_sequence_as_key_events(sequence, on_token)

    def _parse_bracketed_paste(self, on_token: TokenCallback) -> Generator[None]:
        paste_buffer: list[str] = []
        while (yield from self._more_data_available()):
            character = yield self.read1()
            paste_buffer.append(character)
            tail = "".join(paste_buffer[-len(_BRACKETED_PASTE_END) :])
            if tail == _BRACKETED_PASTE_END:
                paste_buffer = paste_buffer[: -len(_BRACKETED_PASTE_END)]
                break

        pasted_text = "".join(paste_buffer)
        self.debug_log("Pasted:", repr(pasted_text))

        # Remove NUL bytes inserted by Windows Terminal:
        # https://github.com/Textualize/textual/issues/1661
        pasted_text = pasted_text.replace("\x00", "")

        on_token(events.Paste(pasted_text))

    def _parse_mouse_event(
        self,
        buttons: int,
        position: Tuple[int, int],
        state: Literal["m", "M"],
        on_token: TokenCallback,
    ) -> None:
        x, y = position
        delta_x = x - self.last_x
        delta_y = y - self.last_y
        self.last_x = x
        self.last_y = y
        event_class: type[events.MouseEvent]

        if buttons & 64:
            event_class = (
                events.MouseScrollDown if buttons & 1 else events.MouseScrollUp
            )
            button = 0
        else:
            if buttons & 32:
                event_class = events.MouseMove
            else:
                event_class = events.MouseDown if state == "M" else events.MouseUp

            button = (buttons + 1) & 3

        event = event_class(
            x,
            y,
            delta_x,
            delta_y,
            button,
            shift=bool(buttons & 4),
            meta=bool(buttons & 8),
            ctrl=bool(buttons & 16),
            screen_x=x,
            screen_y=y,
        )
        self.debug_log("Mouse event:", repr(event))
        on_token(event)

    def _parse_mode_report(
        self,
        mode_id: str,
        setting_parameter: int,
        on_token: TokenCallback,
    ) -> None:
        self.debug_log("Terminal mode report:", repr(mode_id), repr(setting_parameter))
        if mode_id == "2026" and int(setting_parameter) > 0:
            on_token(messages.TerminalSupportsSynchronizedOutput())
