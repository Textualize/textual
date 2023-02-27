import itertools
from unittest import mock

import pytest

from textual._xterm_parser import XTermParser
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


def chunks(data, size):
    if size == 0:
        yield data
        return

    chunk_start = 0
    chunk_end = size
    while True:
        yield data[chunk_start:chunk_end]
        chunk_start = chunk_end
        chunk_end += size
        if chunk_end >= len(data):
            yield data[chunk_start:chunk_end]
            break


@pytest.fixture
def parser():
    return XTermParser(sender=mock.sentinel, more_data=lambda: False)


@pytest.mark.parametrize("chunk_size", [2, 3, 4, 5, 6])
def test_varying_parser_chunk_sizes_no_missing_data(parser, chunk_size):
    end = "\x1b[8~"
    text = "ABCDEFGH"

    data = end + text
    events = []
    for chunk in chunks(data, chunk_size):
        events.append(parser.feed(chunk))

    events = list(itertools.chain.from_iterable(list(event) for event in events))

    assert events[0].key == "end"
    assert [event.key for event in events[1:]] == list(text)


def test_bracketed_paste(parser):
    """When bracketed paste mode is enabled in the terminal emulator and
    the user pastes in some text, it will surround the pasted input
    with the escape codes "\x1b[200~" and "\x1b[201~". The text between
    these codes corresponds to a single `Paste` event in Textual.
    """
    pasted_text = "PASTED"
    events = list(parser.feed(f"\x1b[200~{pasted_text}\x1b[201~"))

    assert len(events) == 1
    assert isinstance(events[0], Paste)
    assert events[0].text == pasted_text
    assert events[0].sender == mock.sentinel


def test_bracketed_paste_content_contains_escape_codes(parser):
    """When performing a bracketed paste, if the pasted content contains
    supported ANSI escape sequences, it should not interfere with the paste,
    and no escape sequences within the bracketed paste should be converted
    into Textual events.
    """
    pasted_text = "PAS\x0fTED"
    events = list(parser.feed(f"\x1b[200~{pasted_text}\x1b[201~"))
    assert len(events) == 1
    assert events[0].text == pasted_text


def test_bracketed_paste_amongst_other_codes(parser):
    pasted_text = "PASTED"
    events = list(parser.feed(f"\x1b[8~\x1b[200~{pasted_text}\x1b[201~\x1b[8~"))
    assert len(events) == 3  # Key.End -> Paste -> Key.End
    assert events[0].key == "end"
    assert events[1].text == pasted_text
    assert events[2].key == "end"


def test_cant_match_escape_sequence_too_long(parser):
    """The sequence did not match, and we hit the maximum sequence search
    length threshold, so each character should be issued as a key-press instead.
    """
    sequence = "\x1b[123456789123456789123"
    events = list(parser.feed(sequence))

    # Every character in the sequence is converted to a key press
    assert len(events) == len(sequence)
    assert all(isinstance(event, Key) for event in events)

    # When we backtrack '\x1b' is translated to '^'
    assert events[0].key == "circumflex_accent"

    # The rest of the characters correspond to the expected key presses
    events = events[1:]
    for index, character in enumerate(sequence[1:]):
        assert events[index].character == character


@pytest.mark.parametrize(
    "chunk_size",
    [
        pytest.param(
            2, marks=pytest.mark.xfail(reason="Fails when ESC at end of chunk")
        ),
        3,
        pytest.param(
            4, marks=pytest.mark.xfail(reason="Fails when ESC at end of chunk")
        ),
        5,
        6,
    ],
)
def test_unknown_sequence_followed_by_known_sequence(parser, chunk_size):
    """When we feed the parser an unknown sequence followed by a known
    sequence. The characters in the unknown sequence are delivered as keys,
    and the known escape sequence that follows is delivered as expected.
    """
    unknown_sequence = "\x1b[?"
    known_sequence = "\x1b[8~"  # key = 'end'

    sequence = unknown_sequence + known_sequence

    events = []
    parser.more_data = lambda: True
    for chunk in chunks(sequence, chunk_size):
        events.append(parser.feed(chunk))

    events = list(itertools.chain.from_iterable(list(event) for event in events))

    assert [event.key for event in events] == [
        "circumflex_accent",
        "left_square_bracket",
        "question_mark",
        "end",
    ]


def test_simple_key_presses_all_delivered_correct_order(parser):
    sequence = "123abc"
    events = parser.feed(sequence)
    assert "".join(event.key for event in events) == sequence


def test_simple_keypress_non_character_key(parser):
    sequence = "\x09"
    events = list(parser.feed(sequence))
    assert len(events) == 1
    assert events[0].key == "tab"


def test_key_presses_and_escape_sequence_mixed(parser):
    sequence = "abc\x1b[13~123"
    events = list(parser.feed(sequence))

    assert len(events) == 7
    assert "".join(event.key for event in events) == "abcf3123"


def test_single_escape(parser):
    """A single \x1b should be interpreted as a single press of the Escape key"""
    events = parser.feed("\x1b")
    assert [event.key for event in events] == ["escape"]


def test_double_escape(parser):
    """Windows Terminal writes double ESC when the user presses the Escape key once."""
    events = parser.feed("\x1b\x1b")
    assert [event.key for event in events] == ["escape"]


@pytest.mark.parametrize(
    "sequence, event_type, shift, meta",
    [
        # Mouse down, with and without modifiers
        ("\x1b[<0;50;25M", MouseDown, False, False),
        ("\x1b[<4;50;25M", MouseDown, True, False),
        ("\x1b[<8;50;25M", MouseDown, False, True),
        # Mouse up, with and without modifiers
        ("\x1b[<0;50;25m", MouseUp, False, False),
        ("\x1b[<4;50;25m", MouseUp, True, False),
        ("\x1b[<8;50;25m", MouseUp, False, True),
    ],
)
def test_mouse_click(parser, sequence, event_type, shift, meta):
    """ANSI codes for mouse should be converted to Textual events"""
    events = list(parser.feed(sequence))

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, event_type)
    assert event.x == 49
    assert event.y == 24
    assert event.screen_x == 49
    assert event.screen_y == 24
    assert event.meta is meta
    assert event.shift is shift


@pytest.mark.parametrize(
    "sequence, shift, meta, button",
    [
        ("\x1b[<32;15;38M", False, False, 1),  # Click and drag
        ("\x1b[<35;15;38M", False, False, 0),  # Basic cursor movement
        ("\x1b[<39;15;38M", True, False, 0),  # Shift held down
        ("\x1b[<43;15;38M", False, True, 0),  # Meta held down
    ],
)
def test_mouse_move(parser, sequence, shift, meta, button):
    events = list(parser.feed(sequence))

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, MouseMove)
    assert event.x == 14
    assert event.y == 37
    assert event.shift is shift
    assert event.meta is meta
    assert event.button == button


@pytest.mark.parametrize(
    "sequence, shift, meta",
    [
        ("\x1b[<64;18;25M", False, False),
        ("\x1b[<68;18;25M", True, False),
        ("\x1b[<72;18;25M", False, True),
    ],
)
def test_mouse_scroll_up(parser, sequence, shift, meta):
    """Scrolling the mouse with and without modifiers held down.
    We don't currently capture modifier keys in scroll events.
    """
    events = list(parser.feed(sequence))

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, MouseScrollUp)
    assert event.x == 17
    assert event.y == 24
    assert event.shift is shift
    assert event.meta is meta


@pytest.mark.parametrize(
    "sequence, shift, meta",
    [
        ("\x1b[<65;18;25M", False, False),
        ("\x1b[<69;18;25M", True, False),
        ("\x1b[<73;18;25M", False, True),
    ],
)
def test_mouse_scroll_down(parser, sequence, shift, meta):
    events = list(parser.feed(sequence))

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, MouseScrollDown)
    assert event.x == 17
    assert event.y == 24
    assert event.shift is shift
    assert event.meta is meta


def test_mouse_event_detected_but_info_not_parsed(parser):
    # I don't know if this can actually happen in reality, but
    # there's a branch in the code that allows for the possibility.
    events = list(parser.feed("\x1b[<65;18;20;25M"))
    assert len(events) == 0


def test_escape_sequence_resulting_in_multiple_keypresses(parser):
    """Some sequences are interpreted as more than 1 keypress"""
    events = list(parser.feed("\x1b[2;4~"))
    assert len(events) == 2
    assert events[0].key == "escape"
    assert events[1].key == "shift+insert"


def test_terminal_mode_reporting_synchronized_output_supported(parser):
    sequence = "\x1b[?2026;1$y"
    events = list(parser.feed(sequence))
    assert len(events) == 1
    assert isinstance(events[0], TerminalSupportsSynchronizedOutput)
    assert events[0].sender == mock.sentinel


def test_terminal_mode_reporting_synchronized_output_not_supported(parser):
    sequence = "\x1b[?2026;0$y"
    events = list(parser.feed(sequence))
    assert events == []
