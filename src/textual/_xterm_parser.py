from __future__ import annotations


import re
from typing import Any, Callable, Generator, Iterable

from . import messages
from . import events
from ._types import MessageTarget
from ._parser import Awaitable, Parser, TokenCallback
from ._ansi_sequences import ANSI_SEQUENCES_KEYS

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

    def debug_log(self, *args: Any) -> None:
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
            button = (buttons + 1) & 3
            x = int(_x) - 1
            y = int(_y) - 1
            delta_x = x - self.last_x
            delta_y = y - self.last_y
            self.last_x = x
            self.last_y = y
            event: events.Event
            if buttons & 64:
                event = (
                    events.MouseScrollDown if button == 1 else events.MouseScrollUp
                )(sender, x, y)
            else:
                event = (
                    events.MouseMove
                    if buttons & 32
                    else (events.MouseDown if state == "M" else events.MouseUp)
                )(
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
        get_key_ansi_sequence = ANSI_SEQUENCES_KEYS.get
        more_data = self.more_data
        paste_buffer: list[str] = []
        bracketed_paste = False

        while not self.is_eof:
            if not bracketed_paste and paste_buffer:
                # We're at the end of the bracketed paste.
                # The paste buffer has content, but the bracketed paste has finished,
                # so we flush the paste buffer. We have to remove the final character
                # since if bracketed paste has come to an end, we'll have added the
                # ESC from the closing bracket, since at that point we didn't know what
                # the full escape code was.
                pasted_text = "".join(paste_buffer[:-1])
                self.debug_log(f"pasted_text={pasted_text!r}")
                on_token(events.Paste(self.sender, text=pasted_text))
                paste_buffer.clear()

            character = yield read1()

            # If we're currently performing a bracketed paste,
            if bracketed_paste:
                paste_buffer.append(character)
                self.debug_log(f"paste_buffer={paste_buffer!r}")

            self.debug_log(f"character={character!r}")
            if character == ESC:
                # Could be the escape key was pressed OR the start of an escape sequence
                sequence: str = character
                if not bracketed_paste:
                    peek_buffer = yield self.peek_buffer()
                    if not peek_buffer:
                        # An escape arrived without any following characters
                        on_token(events.Key(self.sender, key="escape"))
                        continue
                    if peek_buffer and peek_buffer[0] == ESC:
                        # There is an escape in the buffer, so ESC ESC has arrived
                        yield read1()
                        on_token(events.Key(self.sender, key="escape"))
                        # If there is no further data, it is not part of a sequence,
                        # So we don't need to go in to the loop
                        if len(peek_buffer) == 1 and not more_data():
                            continue

                while True:
                    sequence += yield read1()
                    self.debug_log(f"sequence={sequence!r}")

                    # Firstly, check if it's a bracketed paste escape code
                    bracketed_paste_start_match = _re_bracketed_paste_start.match(
                        sequence
                    )
                    self.debug_log(f"sequence = {repr(sequence)}")
                    self.debug_log(f"match = {repr(bracketed_paste_start_match)}")
                    if bracketed_paste_start_match is not None:
                        bracketed_paste = True
                        self.debug_log("BRACKETED PASTE START DETECTED")
                        break

                    bracketed_paste_end_match = _re_bracketed_paste_end.match(sequence)
                    if bracketed_paste_end_match is not None:
                        bracketed_paste = False
                        self.debug_log("BRACKETED PASTE ENDED")
                        break

                    if not bracketed_paste:
                        # Was it a pressed key event that we received?
                        keys = get_key_ansi_sequence(sequence, None)
                        if keys is not None:
                            for key in keys:
                                on_token(events.Key(self.sender, key=key))
                            break
                        # Or a mouse event?
                        mouse_match = _re_mouse_event.match(sequence)
                        if mouse_match is not None:
                            mouse_code = mouse_match.group(0)
                            event = self.parse_mouse_code(mouse_code, self.sender)
                            if event:
                                on_token(event)
                            break
                        # Or a mode report? (i.e. the terminal telling us if it supports a mode we requested)
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
                    keys = get_key_ansi_sequence(character, None)
                    if keys is not None:
                        for key in keys:
                            on_token(events.Key(self.sender, key=key))
                    else:
                        on_token(events.Key(self.sender, key=character))
