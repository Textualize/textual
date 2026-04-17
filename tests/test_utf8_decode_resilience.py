"""Regression test for https://github.com/Textualize/textual/issues/6456

Verify that the UTF-8 incremental decoders used in drivers are configured
with ``errors="replace"`` so that invalid byte sequences produce U+FFFD
instead of raising ``UnicodeDecodeError`` and crashing the input thread.
"""

from codecs import getincrementaldecoder


def test_utf8_decoder_replace_mode() -> None:
    """The decoder must not raise on invalid UTF-8 bytes."""
    decoder = getincrementaldecoder("utf-8")(errors="replace")
    # 0xFF is never valid in UTF-8
    result = decoder.decode(b"\xff")
    assert result == "\ufffd"


def test_utf8_decoder_replace_mixed() -> None:
    """Valid bytes surrounding an invalid byte must decode correctly."""
    decoder = getincrementaldecoder("utf-8")(errors="replace")
    result = decoder.decode(b"hello\xffworld")
    assert result == "hello\ufffdworld"


def test_utf8_decoder_replace_truncated_multibyte() -> None:
    """A truncated multi-byte sequence at end of chunk must not raise."""
    decoder = getincrementaldecoder("utf-8")(errors="replace")
    # \xc3 is the start of a 2-byte sequence; passing final=True forces
    # the decoder to flush, which would raise under strict mode.
    result = decoder.decode(b"\xc3", final=True)
    assert result == "\ufffd"
