from textual._windows_key_sequences import coalesce_alt_sequences


def test_plain_esc_is_preserved() -> None:
    assert coalesce_alt_sequences(["\x1b"]) == ["\x1b"]


def test_alt_followed_by_char_converts_to_kitty_sequence() -> None:
    assert coalesce_alt_sequences(["\x1b", "a"]) == ["\x1b[97;3u"]


def test_alt_shift_sequence_includes_shift_modifier() -> None:
    assert coalesce_alt_sequences(["\x1b", "A"]) == ["\x1b[65;4u"]


def test_escape_prefix_without_trailing_is_converted() -> None:
    assert coalesce_alt_sequences(["\x1b", "["]) == ["\x1b[91;3u"]


def test_escape_prefix_coalesces_when_no_trailing_input() -> None:
    assert coalesce_alt_sequences(["\x1b", "]"]) == ["\x1b[93;3u"]


def test_sequence_with_multiple_pairs() -> None:
    chars = ["\x1b", "a", "b", "\x1b", "c"]
    assert coalesce_alt_sequences(chars) == ["\x1b[97;3u", "b", "\x1b[99;3u"]


def test_escape_prefix_not_coalesced_when_followed_by_more_input() -> None:
    chars = ["\x1b", "[", "A"]
    assert coalesce_alt_sequences(chars) == ["\x1b", "[", "A"]


def test_mixed_escape_sequences_only_convert_valid_pairs() -> None:
    chars = ["x", "\x1b", "[", "A", "\x1b", "d"]
    assert coalesce_alt_sequences(chars) == ["x", "\x1b", "[", "A", "\x1b[100;3u"]


def test_control_characters_become_alt_ctrl() -> None:
    assert coalesce_alt_sequences(["\x1b", "\x01"]) == ["\x1b[97;7u"]


def test_ctrl_space_is_identified() -> None:
    assert coalesce_alt_sequences(["\x1b", "\x00"]) == ["\x1b[64;7u"]


def test_ctrl_delete_is_identified() -> None:
    assert coalesce_alt_sequences(["\x1b", "\x7f"]) == ["\x1b[127;7u"]


def test_control_brackets_remain_literal() -> None:
    assert coalesce_alt_sequences(["\x1b", "\x1b"]) == ["\x1b", "\x1b"]


def test_ctrl_newline_is_converted() -> None:
    assert coalesce_alt_sequences(["\x1b", "\n"]) == ["\x1b[106;7u"]


def test_multi_byte_strings_are_passed_through() -> None:
    assert coalesce_alt_sequences(["\x1b", "ab", "c"]) == ["\x1b", "ab", "c"]


def test_original_sequence_is_not_modified() -> None:
    chars = ["\x1b", "a", "b"]
    snapshot = list(chars)
    coalesce_alt_sequences(chars)
    assert chars == snapshot
