from __future__ import annotations


import os
import re
from typing import Any, Callable, Generator, Iterable

from . import log
from . import events
from ._types import MessageTarget
from ._parser import Awaitable, Parser, TokenCallback
from ._ansi_sequences import ANSI_SEQUENCES_KEYS, ANSI_SEQUENCES_MODE_REPORTS

_re_mouse_event = re.compile("^" + re.escape("\x1b[") + r"(<?[\d;]+[mM]|M...)\Z")


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
        get_mode_report_sequence = ANSI_SEQUENCES_MODE_REPORTS.get
        more_data = self.more_data

        while not self.is_eof:
            character = yield read1()
            self.debug_log(f"character={character!r}")
            if character == ESC:
                # Could be the escape key was pressed OR the start of an escape sequence
                sequence: str = character
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
                    mode_report_match = get_mode_report_sequence(sequence, None)
                    if mode_report_match is not None:
                        mode_report, parameter = mode_report_match
                        event = events.ModeReport(self.sender, mode_report, parameter)
                        on_token(event)
                        break
            else:
                keys = get_key_ansi_sequence(character, None)
                if keys is not None:
                    for key in keys:
                        on_token(events.Key(self.sender, key=key))
                else:
                    on_token(events.Key(self.sender, key=character))
