import functools
import itertools
import logging

import pytest

from textual._ansi_sequences import ANSI_SEQUENCES_KEYS
from textual._xterm_parser import (
    _BRACKETED_PASTE_END,
    _BRACKETED_PASTE_START,
    XTermParser,
)
from textual.events import (
    Key,
    MouseDown,
    MouseMove,
    MouseScrollDown,
    MouseScrollUp,
    MouseUp,
    Paste,
)
from textual.messages import TerminalSupportsSynchronizedOutput


@pytest.fixture(autouse=True)
def set_logging_level(caplog):
    caplog.set_level(logging.DEBUG)


class Chunks:
    def __init__(self, sequence, chunk_size=None):
        chunk_size = len(sequence) if chunk_size is None else chunk_size
        self._chunks = [
            sequence[i : i + chunk_size] for i in range(0, len(sequence), chunk_size)
        ]
        print(
            f"Chunks(sequence={sequence!r}, chunk_size={chunk_size!r}): {self._chunks!r}"
        )
        self.more_data_calls = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._chunks:
            return self._chunks.pop(0)
        else:
            raise StopIteration()

    def more_data(self):
        self.more_data_calls += 1
        return len(self._chunks) > 0

    @functools.cached_property
    def parser(self):
        return XTermParser(
            more_data=self.more_data,
            debug=logging.getLogger().debug,
        )

    @property
    def as_events(self):
        """List of events from passing our chunked sequence to XTermParser.feed()"""
        return [event for chunk in self for event in self.parser.feed(chunk)]


def assert_events_equal(events_a, events_b):
    """Compare two sequences of events"""
    for event_a, event_b in itertools.zip_longest(events_a, events_b):
        print(repr(event_a))
        print(repr(event_b))
        if event_a is None:
            raise AssertionError(f"Event never happened: {event_b}")
        elif event_b is None:
            raise AssertionError(f"Missing event: {event_a}")
        elif type(event_a) != type(event_b):
            raise AssertionError(
                f"Mismatching event types: {type(event_a)} != {type(event_b)}"
            )
        elif isinstance(event_a, Key):
            assert event_a.key == event_b.key
            assert event_a.character == event_b.character
        elif isinstance(event_a, Paste):
            assert event_a.text == event_b.text
        elif isinstance(
            event_a, (MouseMove, MouseDown, MouseUp, MouseScrollDown, MouseScrollUp)
        ):
            assert event_a.x == event_b.x
            assert event_a.y == event_b.y
            assert event_a.delta_x == event_b.delta_x
            assert event_a.delta_y == event_b.delta_y
            assert event_a.button == event_b.button
            assert event_a.shift == event_b.shift
            assert event_a.meta == event_b.meta
            assert event_a.ctrl == event_b.ctrl
            assert event_a.screen_x == event_b.screen_x
            assert event_a.screen_y == event_b.screen_y
        elif isinstance(event_a, TerminalSupportsSynchronizedOutput):
            assert type(event_a) is type(event_b)
        else:
            raise RuntimeError(f"Unsupported event type: {type(event_a)}")


@pytest.mark.parametrize(
    argnames="sequence, exp_events",
    argvalues=(
        pytest.param(
            "a",
            [Key(key="a", character="a")],
            id="One single character",
        ),
        pytest.param(
            "abç👍",
            [
                Key(key="a", character="a"),
                Key(key="b", character="b"),
                Key(key="ç", character="ç"),
                Key(key="thumbs_up_sign", character="👍"),
            ],
            id="Multiple single characters",
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_single_characters(sequence, exp_events, chunk_size):
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    assert_events_equal(chunks.as_events, exp_events)


# Make sure any performance optimizations or other shenangians mess with known
# escape sequences.
@pytest.mark.parametrize(
    argnames="sequence, keys",
    argvalues=ANSI_SEQUENCES_KEYS.items(),
    ids=lambda v: repr(v),
)
def test_ansi_escape_keys(sequence, keys):
    chunks = Chunks(sequence=sequence)
    assert_events_equal(
        chunks.as_events, chunks.parser._sequence_to_key_events(sequence)
    )


@pytest.mark.parametrize(
    argnames="sequence, exp_events",
    argvalues=(
        (
            "\x1b",
            [
                Key(key="escape", character="\x1b"),
            ],
        ),
        (
            "\x1b\x1b",
            [
                Key(key="alt+escape", character=None),
            ],
        ),
        (
            "\x1b\x1b\x1b",
            [
                Key(key="alt+escape", character=None),
                Key(key="escape", character="\x1b"),
            ],
        ),
        (
            "\x1b\x1b\x1b\x1b",
            [
                Key(key="alt+escape", character=None),
                Key(key="alt+escape", character=None),
            ],
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize("chunk_size", (1, 2, None), ids=lambda s: f"chunk_size={s}")
def test_consecutive_escapes(sequence, exp_events, chunk_size):
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    assert_events_equal(chunks.as_events, exp_events)


@pytest.mark.parametrize(
    argnames="sequence, exp_events",
    argvalues=(
        pytest.param(
            "\x1bOP" + "\x1bOQ",  # F1, F2
            [Key(key="f1", character=None), Key(key="f2", character=None)],
            id="Only known escape sequences",
        ),
        pytest.param(
            "\x1bOP" + "\x1bf" + "\x1bOQ",
            [
                Key(key="f1", character=None),
                Key(key="alt+f", character=None),
                Key(key="f2", character=None),
            ],
            id="Known and short unknown escape sequences",
        ),
        pytest.param(
            "\x1bOP" + "\x1b[?foo;bar|baz~" + "\x1bOQ",
            [Key(key="f1", character=None), Key(key="f2", character=None)],
            id="Known and long unknown escape sequences",
        ),
        pytest.param(
            "\x1b[?foo" + "\x1b[?bar" + "\x1b[?baa",
            [],
            id="Only unknown escape sequences",
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize(
    "chunk_size",
    (1, 2, 3, 4, None),
    ids=lambda s: f"chunk_size={s}",
)
def test_multiple_escape_sequences_in_chunks(sequence, exp_events, chunk_size):
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    assert_events_equal(chunks.as_events, exp_events)


@pytest.mark.parametrize(
    argnames="sequence, exp_events",
    argvalues=(
        pytest.param(
            "\x1b[foo",
            [],
            id="Nothing",
        ),
        pytest.param(
            "\x1b[foo\x1b[2~",
            [Key(key="insert", character=None)],
            id="Normal escape sequence",
        ),
        pytest.param(
            "\x1b[foo\x1bOP",
            [Key(key="f1", character=None)],
            id="Exotic escape sequence",
        ),
        pytest.param(
            "\x1b[foo\r",
            [Key(key="enter", character="\r")],
            id="Control character",
        ),
        pytest.param(
            "\x1b[fooş",
            [Key(key="ş", character="ş")],
            id="Non-ASCII character",
        ),
    ),
    ids=lambda v: repr(v),
)
def test_unknown_escape_sequence_followed_by(sequence, exp_events):
    chunks = Chunks(sequence=sequence)
    assert_events_equal(chunks.as_events, exp_events)


@pytest.mark.parametrize(
    argnames="pasted_text, exp_events",
    argvalues=(
        pytest.param(
            "PASTED TEXT",
            [Paste("PASTED TEXT")],
            id="Normal text",
        ),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize(
    argnames="prefix, exp_pre_events",
    argvalues=(
        ("", []),
        ("\x1bOP", [Key(key="f1", character=None)]),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize(
    argnames="postfix, exp_post_events",
    argvalues=(
        ("", []),
        ("\x1bOQ", [Key(key="f2", character=None)]),
    ),
    ids=lambda v: repr(v),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_bracketed_paste(
    pasted_text,
    exp_events,
    prefix,
    exp_pre_events,
    postfix,
    exp_post_events,
    chunk_size,
):
    sequence = (
        prefix + _BRACKETED_PASTE_START + pasted_text + _BRACKETED_PASTE_END + postfix
    )
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    assert_events_equal(
        chunks.as_events,
        exp_pre_events + exp_events + exp_post_events,
    )


@pytest.mark.parametrize(
    argnames="modifiers_code, exp_modifiers",
    argvalues=(
        pytest.param(
            0, {"shift": False, "meta": False, "ctrl": False}, id="No modifiers"
        ),
        pytest.param(4, {"shift": True, "meta": False, "ctrl": False}, id="Shift"),
        pytest.param(8, {"shift": False, "meta": True, "ctrl": False}, id="Meta"),
        pytest.param(16, {"shift": False, "meta": False, "ctrl": True}, id="Ctrl"),
        pytest.param(
            12, {"shift": True, "meta": True, "ctrl": False}, id="Shift + Meta"
        ),
        pytest.param(
            20, {"shift": True, "meta": False, "ctrl": True}, id="Shift + Ctrl"
        ),
        pytest.param(
            24, {"shift": False, "meta": True, "ctrl": True}, id="Meta + Ctrl"
        ),
        pytest.param(
            28, {"shift": True, "meta": True, "ctrl": True}, id="Shift + Meta + Ctrl"
        ),
    ),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_mouse_move_event(
    modifiers_code,
    exp_modifiers,
    chunk_size,
):
    x, y = 50, 25
    button_value = 35 + modifiers_code
    sequence = f"\x1b[<{button_value};{x};{y}M"
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    exp_event = MouseMove(
        x=x - 1, y=y - 1, delta_x=x - 1, delta_y=y - 1, button=0, **exp_modifiers
    )
    assert_events_equal(chunks.as_events, [exp_event])


@pytest.mark.parametrize(
    argnames="modifiers_code, exp_modifiers",
    argvalues=(
        pytest.param(0, {"shift": False, "meta": False, "ctrl": False}, id=""),
        pytest.param(4, {"shift": True, "meta": False, "ctrl": False}, id="Shift"),
        pytest.param(8, {"shift": False, "meta": True, "ctrl": False}, id="Meta"),
        pytest.param(16, {"shift": False, "meta": False, "ctrl": True}, id="Ctrl"),
        pytest.param(12, {"shift": True, "meta": True, "ctrl": False}, id="Shift+Meta"),
        pytest.param(20, {"shift": True, "meta": False, "ctrl": True}, id="Shift+Ctrl"),
        pytest.param(24, {"shift": False, "meta": True, "ctrl": True}, id="Meta+Ctrl"),
        pytest.param(
            28, {"shift": True, "meta": True, "ctrl": True}, id="Shift+Meta+Ctrl"
        ),
    ),
)
@pytest.mark.parametrize(
    argnames="button_code, exp_button",
    argvalues=(
        pytest.param(0, 1, id="Button1"),
        pytest.param(1, 2, id="Button2"),
        pytest.param(2, 3, id="Button3"),
    ),
)
@pytest.mark.parametrize(
    argnames="event_code, exp_event_class",
    argvalues=(
        pytest.param("M", MouseDown, id="MouseDown"),
        pytest.param("m", MouseUp, id="MouseUp"),
    ),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_mouse_click_event(
    button_code,
    exp_button,
    event_code,
    exp_event_class,
    modifiers_code,
    exp_modifiers,
    chunk_size,
):
    x, y = 50, 25
    button_value = modifiers_code + button_code
    sequence = f"\x1b[<{button_value};{x};{y}{event_code}"
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    exp_event = exp_event_class(
        x=x - 1,
        y=y - 1,
        delta_x=x - 1,
        delta_y=y - 1,
        button=exp_button,
        **exp_modifiers,
    )
    assert_events_equal(chunks.as_events, [exp_event])


@pytest.mark.parametrize(
    argnames="modifiers_code, exp_modifiers",
    argvalues=(
        pytest.param(
            0, {"shift": False, "meta": False, "ctrl": False}, id="No modifiers"
        ),
        pytest.param(4, {"shift": True, "meta": False, "ctrl": False}, id="Shift"),
        pytest.param(8, {"shift": False, "meta": True, "ctrl": False}, id="Meta"),
        pytest.param(16, {"shift": False, "meta": False, "ctrl": True}, id="Ctrl"),
        pytest.param(
            12, {"shift": True, "meta": True, "ctrl": False}, id="Shift + Meta"
        ),
        pytest.param(
            20, {"shift": True, "meta": False, "ctrl": True}, id="Shift + Ctrl"
        ),
        pytest.param(
            24, {"shift": False, "meta": True, "ctrl": True}, id="Meta + Ctrl"
        ),
        pytest.param(
            28, {"shift": True, "meta": True, "ctrl": True}, id="Shift + Meta + Ctrl"
        ),
    ),
)
@pytest.mark.parametrize(
    argnames="direction_code, exp_event_class",
    argvalues=(
        pytest.param(64, MouseScrollUp, id="ScrollUp"),
        pytest.param(65, MouseScrollDown, id="ScrollDown"),
    ),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_mouse_scroll_event(
    direction_code,
    exp_event_class,
    modifiers_code,
    exp_modifiers,
    chunk_size,
):
    x, y = 50, 25
    button_value = direction_code + modifiers_code
    sequence = f"\x1b[<{button_value};{x};{y}M"
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    exp_event = exp_event_class(
        x=x - 1, y=y - 1, delta_x=x - 1, delta_y=y - 1, button=0, **exp_modifiers
    )
    assert_events_equal(chunks.as_events, [exp_event])


@pytest.mark.parametrize(
    argnames="sequence, exp_events",
    argvalues=(
        pytest.param(
            "\x1b[?123;456$y",
            [],
            id="Unsupported mode",
        ),
        pytest.param(
            "\x1b[?2026;0$y",
            [],
            id="Synchronized Output (Mode is not recognized)",
        ),
        pytest.param(
            "\x1b[?2026;1$y",
            [TerminalSupportsSynchronizedOutput()],
            id="Synchronized Output (Set)",
        ),
        pytest.param(
            "\x1b[?2026;2$y",
            [TerminalSupportsSynchronizedOutput()],
            id="Synchronized Output (Reset)",
        ),
        pytest.param(
            "\x1b[?2026;3$y",
            [TerminalSupportsSynchronizedOutput()],
            id="Synchronized Output (Permanently set)",
        ),
        pytest.param(
            "\x1b[?2026;4$y",
            [TerminalSupportsSynchronizedOutput()],
            id="Synchronized Output (Permanently reset)",
        ),
    ),
)
@pytest.mark.parametrize("chunk_size", (1, 2, 3, None), ids=lambda s: f"chunk_size={s}")
def test_terminal_mode_report_event(sequence, exp_events, chunk_size):
    chunks = Chunks(sequence=sequence, chunk_size=chunk_size)
    assert_events_equal(chunks.as_events, exp_events)


@pytest.mark.parametrize(
    argnames="sequence, exp_immediacy",
    argvalues=(
        pytest.param(
            "\x1b[1234~",
            False,
            id="Unknown sequence",
        ),
        pytest.param(
            "\x1b[<35;30;12M",
            True,
            id="Mouse movement",
        ),
        pytest.param(
            "\x1b[17~",
            True,
            id="ANSI sequence key (Insert)",
        ),
        pytest.param(
            "\x1bx",
            True,
            id="Alt+x",
        ),
    ),
)
def test_optimization(sequence, exp_immediacy):
    chunks = Chunks(sequence=sequence, chunk_size=1)
    chunks.as_events  # Process sequences
    if exp_immediacy:
        exp_more_data_calls = len(sequence) - 1
    else:
        exp_more_data_calls = len(sequence)
    assert chunks.more_data_calls == exp_more_data_calls
