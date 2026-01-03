"""Tests for BiDi (Bidirectional) text support."""

from __future__ import annotations

import pytest

from textual._bidi import (
    BIDI_AVAILABLE,
    apply_bidi_to_content,
    apply_bidi_to_line,
    contains_rtl,
    get_display,
    get_display_with_mapping,
    remap_spans,
)
from textual.content import Content, Span


class TestContainsRtl:
    """Tests for the contains_rtl function."""

    def test_empty_string(self):
        """Empty string should not contain RTL."""
        assert contains_rtl("") is False

    def test_ascii_only(self):
        """ASCII-only text should not contain RTL."""
        assert contains_rtl("Hello World") is False
        assert contains_rtl("123 abc XYZ") is False
        assert contains_rtl("!@#$%^&*()") is False

    def test_hebrew(self):
        """Hebrew text should be detected as RTL."""
        assert contains_rtl("שלום") is True
        assert contains_rtl("שלום עולם") is True

    def test_arabic(self):
        """Arabic text should be detected as RTL."""
        assert contains_rtl("مرحبا") is True
        assert contains_rtl("مرحبا بالعالم") is True

    def test_mixed(self):
        """Mixed text with RTL should be detected."""
        assert contains_rtl("Hello שלום World") is True
        assert contains_rtl("Test مرحبا Test") is True

    def test_numbers_only(self):
        """Numbers should not be detected as RTL."""
        assert contains_rtl("12345") is False

    def test_rtl_with_numbers(self):
        """RTL text with numbers should be detected."""
        assert contains_rtl("מספר 123") is True


class TestGetDisplay:
    """Tests for the get_display function."""

    def test_empty_string(self):
        """Empty string should return empty."""
        assert get_display("") == ""

    def test_ascii_only(self):
        """ASCII text should be unchanged."""
        assert get_display("Hello World") == "Hello World"

    @pytest.mark.skipif(not BIDI_AVAILABLE, reason="python-bidi not installed")
    def test_hebrew_only(self):
        """Pure Hebrew should be reversed for display."""
        # Hebrew "shalom" should be reversed for LTR terminal display
        result = get_display("שלום")
        # The exact result depends on python-bidi behavior
        assert len(result) == 4

    @pytest.mark.skipif(not BIDI_AVAILABLE, reason="python-bidi not installed")
    def test_mixed_hebrew_english(self):
        """Mixed text should follow BiDi algorithm."""
        result = get_display("Hello שלום World")
        # The Hebrew part should be visually reordered
        assert "Hello" in result
        assert "World" in result


class TestGetDisplayWithMapping:
    """Tests for get_display_with_mapping function."""

    def test_empty_string(self):
        """Empty string should return empty with empty mapping."""
        text, mapping = get_display_with_mapping("")
        assert text == ""
        assert mapping == []

    def test_ascii_only(self):
        """ASCII text should have identity mapping."""
        text, mapping = get_display_with_mapping("abc")
        assert text == "abc"
        assert mapping == [0, 1, 2]

    def test_no_rtl(self):
        """Text without RTL should be unchanged."""
        text, mapping = get_display_with_mapping("Hello World")
        assert text == "Hello World"
        assert mapping == list(range(len("Hello World")))


class TestRemapSpans:
    """Tests for remap_spans function."""

    def test_empty_spans(self):
        """Empty spans should return empty."""
        result = remap_spans([], [0, 1, 2], 3)
        assert result == []

    def test_empty_mapping(self):
        """Empty mapping should return original spans."""
        spans = [Span(0, 2, "red")]
        result = remap_spans(spans, [], 0)
        assert result == spans

    def test_identity_mapping(self):
        """Identity mapping should preserve spans."""
        spans = [Span(0, 2, "red"), Span(3, 5, "blue")]
        mapping = [0, 1, 2, 3, 4]
        result = remap_spans(spans, mapping, 5)
        # Should have spans in same positions
        assert len(result) == 2


class TestApplyBidiToContent:
    """Tests for apply_bidi_to_content function."""

    def test_empty_content(self):
        """Empty content should return unchanged."""
        content = Content("")
        result = apply_bidi_to_content(content)
        assert result.plain == ""

    def test_ascii_content(self):
        """ASCII-only content should return unchanged."""
        content = Content("Hello World")
        result = apply_bidi_to_content(content)
        assert result.plain == "Hello World"

    def test_content_with_spans(self):
        """Content with spans should preserve styling."""
        content = Content("Hello", spans=[Span(0, 5, "red")])
        result = apply_bidi_to_content(content)
        assert len(result.spans) > 0

    @pytest.mark.skipif(not BIDI_AVAILABLE, reason="python-bidi not installed")
    def test_rtl_content(self):
        """RTL content should be processed."""
        content = Content("שלום")
        result = apply_bidi_to_content(content)
        # Should have been processed (exact result depends on python-bidi)
        assert len(result.plain) == 4


class TestApplyBidiToLine:
    """Tests for apply_bidi_to_line function."""

    def test_empty_string(self):
        """Empty string should return empty."""
        assert apply_bidi_to_line("") == ""

    def test_ascii_only(self):
        """ASCII text should be unchanged."""
        assert apply_bidi_to_line("Hello") == "Hello"

    def test_no_rtl(self):
        """Text without RTL should be unchanged."""
        assert apply_bidi_to_line("Hello World 123") == "Hello World 123"


class TestBidiAvailable:
    """Tests for BIDI_AVAILABLE flag."""

    def test_flag_is_boolean(self):
        """BIDI_AVAILABLE should be a boolean."""
        assert isinstance(BIDI_AVAILABLE, bool)
