from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable, Generator, Iterable

from . import events, messages
from ._ansi_sequences import ANSI_SEQUENCES_KEYS
from ._parser import Awaitable, Parser, TokenCallback
from ._types import MessageTarget
from .keys import KEY_NAME_REPLACEMENTS

# When trying to determine whether the current sequence is a supported/valid
# escape sequence, at which length should we give up and consider our search
# to be unsuccessful?
_MAX_SEQUENCE_SEARCH_THRESHOLD = 20

_re_mouse_event = re.compile("^" + re.escape("\x1b[") + r"(<?[\d;]+[mM]|M...)\Z")
_re_terminal_mode_response = re.compile(
    "^" + re.escape("\x1b[") + r"\?(?P<mode_id>\d+);(?P<setting_parameter>\d)\$y"
)
_re_bracketed_paste_start = re.compile(r"^\x1b\[200~$")
_re_bracketed_paste_end = re.compile(r"^\x1b\[201~$")


class XTermParser(Parser[events.Event]):
    _re_sgr_mouse = re.compile(r"\x1b\[<(\d+);(\d+);(\d+)([Mm])")

    def __init__(
        self, sender: MessageTarget, more_data: Callable[[], bool], debug: bool = False
    ) -> None:
        self.sender = sender
        self.more_data = more_data
        self.last_x = 0
        self.last_y = 0

        self._debug_log_file = open("keys.log", "wt") if debug else None

        super().__init__()

    def debug_log(self, *args: Any) -> None:  # pragma: no cover
        if self._debug_log_file is not None:
            self._debug_log_file.write(" ".join(args) + "\n")
            self._debug_log_file.flush()

    def feed(self, data: str) -> Iterable[events.Event]:
        self.debug_log(f"FEED {data!r}")
        return super().feed(data)

    def parse_mouse_code(self, code: str, sender: MessageTarget) -> events.Event | None:
        sgr_match = self._re_sgr_mouse.match(code)
        if sgr_match:
            _buttons, _x, _y, state = sgr_match.groups()
            buttons = int(_buttons)
            x = int(_x) - 1
            y = int(_y) - 1
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
                sender,
                x,
                y,
                delta_x,
                delta_y,
                button,
                bool(buttons & 4),
                bool(buttons & 8),
                bool(buttons & 16),
                screen_x=x,
                screen_y=y,
            )
            return event
        return None

    def parse(self, on_token: TokenCallback) -> Generator[Awaitable, str, None]:
        ESC = "\x1b"
        read1 = self.read1
        sequence_to_key_events = self._sequence_to_key_events
        more_data = self.more_data
        paste_buffer: list[str] = []
        bracketed_paste = False
        use_prior_escape = False

        def reissue_sequence_as_keys(reissue_sequence: str) -> None:
            for character in reissue_sequence:
                key_events = sequence_to_key_events(character)
                for event in key_events:
                    if event.key == "escape":
                        event = events.Key(event.sender, "circumflex_accent", "^")
                    on_token(event)

        while not self.is_eof:
            if not bracketed_paste and paste_buffer:
                # We're at the end of the bracketed paste.
                # The paste buffer has content, but the bracketed paste has finished,
                # so we flush the paste buffer. We have to remove the final character
                # since if bracketed paste has come to an end, we'll have added the
                # ESC from the closing bracket, since at that point we didn't know what
                # the full escape code was.
                pasted_text = "".join(paste_buffer[:-1])
                # Note the removal of NUL characters: https://github.com/Textualize/textual/issues/1661
                on_token(
                    events.Paste(self.sender, text=pasted_text.replace("\x00", ""))
                )
                paste_buffer.clear()

            character = ESC if use_prior_escape else (yield read1())
            use_prior_escape = False

            if bracketed_paste:
                paste_buffer.append(character)

            self.debug_log(f"character={character!r}")
            if character == ESC:
                # Could be the escape key was pressed OR the start of an escape sequence
                sequence: str = character
                if not bracketed_paste:
                    # TODO: There's nothing left in the buffer at the moment,
                    #  but since we're on an escape, how can we be sure that the
                    #  data that next gets fed to the parser isn't an escape sequence?

                    #  This problem arises when an ESC falls at the end of a chunk.
                    #  We'll be at an escape, but peek_buffer will return an empty
                    #  string because there's nothing in the buffer yet.

                    #  This code makes an assumption that an escape sequence will never be
                    #  "chopped up", so buffers would never contain partial escape sequences.
                    peek_buffer = yield self.peek_buffer()
                    if not peek_buffer:
                        # An escape arrived without any following characters
                        on_token(events.Key(self.sender, "escape", "\x1b"))
                        continue
                    if peek_buffer and peek_buffer[0] == ESC:
                        # There is an escape in the buffer, so ESC ESC has arrived
                        yield read1()
                        on_token(events.Key(self.sender, "escape", "\x1b"))
                        # If there is no further data, it is not part of a sequence,
                        # So we don't need to go in to the loop
                        if len(peek_buffer) == 1 and not more_data():
                            continue

                # Look ahead through the suspected escape sequence for a match
                while True:
                    # If we run into another ESC at this point, then we've failed
                    # to find a match, and should issue everything we've seen within
                    # the suspected sequence as Key events instead.
                    sequence_character = yield read1()
                    new_sequence = sequence + sequence_character

                    threshold_exceeded = len(sequence) > _MAX_SEQUENCE_SEARCH_THRESHOLD
                    found_escape = sequence_character and sequence_character == ESC

                    if threshold_exceeded:
                        # We exceeded the sequence length threshold, so reissue all the
                        # characters in that sequence as key-presses.
                        reissue_sequence_as_keys(new_sequence)
                        break

                    if found_escape:
                        # We've hit an escape, so we need to reissue all the keys
                        # up to but not including it, since this escape could be
                        # part of an upcoming control sequence.
                        use_prior_escape = True
                        reissue_sequence_as_keys(sequence)
                        break

                    sequence = new_sequence

                    self.debug_log(f"sequence={sequence!r}")

                    bracketed_paste_start_match = _re_bracketed_paste_start.match(
                        sequence
                    )
                    if bracketed_paste_start_match is not None:
                        bracketed_paste = True
                        break

                    bracketed_paste_end_match = _re_bracketed_paste_end.match(sequence)
                    if bracketed_paste_end_match is not None:
                        bracketed_paste = False
                        break

                    if not bracketed_paste:
                        # Was it a pressed key event that we received?
                        key_events = list(sequence_to_key_events(sequence))
                        for key_event in key_events:
                            on_token(key_event)
                        if key_events:
                            break
                        # Or a mouse event?
                        mouse_match = _re_mouse_event.match(sequence)
                        if mouse_match is not None:
                            mouse_code = mouse_match.group(0)
                            event = self.parse_mouse_code(mouse_code, self.sender)
                            if event:
                                on_token(event)
                            break

                        # Or a mode report?
                        # (i.e. the terminal saying it supports a mode we requested)
                        mode_report_match = _re_terminal_mode_response.match(sequence)
                        if mode_report_match is not None:
                            if (
                                mode_report_match["mode_id"] == "2026"
                                and int(mode_report_match["setting_parameter"]) > 0
                            ):
                                on_token(
                                    messages.TerminalSupportsSynchronizedOutput(
                                        self.sender
                                    )
                                )
                            break
            else:
                if not bracketed_paste:
                    for event in sequence_to_key_events(character):
                        on_token(event)

    def _sequence_to_key_events(
        self, sequence: str, _unicode_name=unicodedata.name
    ) -> Iterable[events.Key]:
        """Map a sequence of code points on to a sequence of keys.

        Args:
            sequence: Sequence of code points.

        Returns:
            Keys

        """
        keys = ANSI_SEQUENCES_KEYS.get(sequence)
        if keys is not None:
            for key in keys:
                yield events.Key(
                    self.sender, key.value, sequence if len(sequence) == 1 else None
                )
        elif len(sequence) == 1:
            try:
                if not sequence.isalnum():
                    name = (
                        _unicode_name(sequence)
                        .lower()
                        .replace("-", "_")
                        .replace(" ", "_")
                    )
                else:
                    name = sequence
                name = KEY_NAME_REPLACEMENTS.get(name, name)
                yield events.Key(self.sender, name, sequence)
            except:
                yield events.Key(self.sender, sequence, sequence)
