from __future__ import annotations

import weakref
from asyncio import CancelledError, Event, Task, create_task, sleep
from contextlib import contextmanager
from functools import partial
from typing import Callable, ContextManager, NamedTuple

try:
    from tree_sitter import Language, Node, Parser, Query, Tree

    TREE_SITTER = True
except ImportError:
    TREE_SITTER = False


from textual.document._document import Document, EditResult, Location, _utf8_encode


@contextmanager
def temporary_query_point_range(
    query: Query,
    start_point: tuple[int, int] | None,
    end_point: tuple[int, int] | None,
) -> ContextManager[None]:
    """Temporarily change the start and/or end point for a tree-sitter Query.

    Args:
        query: The tree-sitter Query.
        start_point: The (row, column byte) to start the query at.
        end_point: The (row, column byte) to end the query at.
    """
    # Note: Although not documented for the tree-sitter Python API, an
    # end-point of (0, 0) means 'end of document'.
    default_point_range = [(0, 0), (0, 0)]

    point_range = list(default_point_range)
    if start_point is not None:
        point_range[0] = start_point
    if end_point is not None:
        point_range[1] = end_point
    query.set_point_range(point_range)
    try:
        yield None
    finally:
        query.set_point_range(default_point_range)


class SyntaxTreeEdit(NamedTuple):
    """Details of a tree-sitter syntax tree edit operation."""

    start_byte: int
    old_end_byte: int
    new_end_byte: int
    start_point: int
    old_end_point: int
    new_end_point: int


class SyntaxAwareDocumentError(Exception):
    """General error raised when SyntaxAwareDocument is used incorrectly."""


class SyntaxAwareDocument(Document):
    """A subclass of Document which also maintains a tree-sitter syntax
    tree when the document is edited.
    """

    def __init__(
        self,
        text: str,
        language: Language,
    ):
        """Construct a SyntaxAwareDocument.

        Args:
            text: The initial text contained in the document.
            language: The tree-sitter language to use.
        """

        if not TREE_SITTER:
            raise RuntimeError(
                "SyntaxAwareDocument unavailable - tree-sitter is not installed."
            )

        super().__init__(text)
        self.language: Language = language
        """The tree-sitter Language."""

        self._parser = Parser(self.language)
        """The tree-sitter Parser or None if tree-sitter is unavailable."""

        self._syntax_tree: Tree = self._parser.parse(
            partial(self._read_callable, lines=self.lines)
        )  # type: ignore
        """The tree-sitter Tree (syntax tree) built from the document."""

        self._syntax_tree_update_callback: Callable[[], None] | None = None
        self._background_parser = BackgroundSyntaxParser(self)
        self._pending_syntax_edits: list[SyntaxTreeEdit] = []

    def clean_up(self) -> None:
        """Perform any pre-deletion clean up."""
        self._background_parser.stop()

    def copy_of_lines(self):
        """Provide a copy of the document's lines."""
        return list(self._lines)

    def apply_pending_syntax_edits(self) -> bool:
        """Apply any pending edits to the syntax tree.

        Returns:
            True if any edits were applied.
        """
        if self._pending_syntax_edits:
            for edit in self._pending_syntax_edits:
                self._syntax_tree.edit(**edit._asdict())
            self._pending_syntax_edits[:] = []
            return True
        else:
            return False

    def prepare_query(self, query: str) -> Query | None:
        """Prepare a tree-sitter tree query.

        Queries should be prepared once, then reused.

        To execute a query, call `query_syntax_tree`.

        Args:
            query: The string query to prepare.

        Returns:
            The prepared query.
        """
        return self.language.query(query)

    def query_syntax_tree(
        self,
        query: Query,
        start_point: tuple[int, int] | None = None,
        end_point: tuple[int, int] | None = None,
    ) -> dict[str, list["Node"]]:
        """Query the tree-sitter syntax tree.

        The default implementation always returns an empty list.

        To support querying in a subclass, this must be implemented.

        Args:
            query: The tree-sitter Query to perform.
            start_point: The (row, column byte) to start the query at.
            end_point: The (row, column byte) to end the query at.

        Returns:
            A tuple containing the nodes and text captured by the query.
        """
        with temporary_query_point_range(query, start_point, end_point):
            return query.captures(self._syntax_tree.root_node)

    def set_syntax_tree_update_callback(
        self,
        callback: Callable[[], None],
    ) -> None:
        """Set a callback function for signalling a rebuild of the syntax tree.

        Args:
            callback: A function that takes no arguments and returns None.
        """
        self._syntax_tree_update_callback = callback

    def trigger_syntax_tree_update(self, force_update: bool = False) -> None:
        """Trigger a new syntax tree update to run in the background.

        Args:
            force_update: When set, ensure that the syntax tree is regenerated
                unconditionally.
        """
        self._background_parser.trigger_syntax_tree_update(force_update)

    def replace_range(self, start: Location, end: Location, text: str) -> EditResult:
        """Replace text at the given range.

        Args:
            start: A tuple (row, column) where the edit starts.
            end: A tuple (row, column) where the edit ends.
            text: The text to insert between start and end.

        Returns:
            The new end location after the edit is complete.
        """
        top, bottom = sorted((start, end))

        # An optimisation would be finding the byte offsets as a single operation rather
        # than doing two passes over the document content.
        start_byte = self._location_to_byte_offset(top)
        start_point = self._location_to_point(top)
        old_end_byte = self._location_to_byte_offset(bottom)
        old_end_point = self._location_to_point(bottom)

        replace_result = super().replace_range(start, end, text)

        text_byte_length = len(_utf8_encode(text))
        end_location = replace_result.end_location
        assert self._syntax_tree is not None
        assert self._parser is not None
        self._pending_syntax_edits.append(
            SyntaxTreeEdit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=start_byte + text_byte_length,
                start_point=start_point,
                old_end_point=old_end_point,
                new_end_point=self._location_to_point(end_location),
            )
        )
        return replace_result

    def reparse(self, timeout_us: int, lines: list[str], syntax_tree=None) -> bool:
        """Reparse the document.

        Args:
            timeout_us: The parser timeout in microseconds.
            lines: A list of the lines being parsed.

        Returns:
            True if parsing succeeded and False if a timeout occurred.
        """
        assert timeout_us > 0
        read_source = partial(self._read_callable, lines=lines)
        tree = self._syntax_tree
        saved_timeout = self._parser.timeout_micros
        try:
            self._parser.timeout_micros = timeout_us
            try:
                tree = self._parser.parse(read_source, tree)  # type: ignore[arg-type]
            except ValueError:
                # The only known cause is a timeout.
                return False
            else:
                self._syntax_tree = tree
                if self._syntax_tree_update_callback is not None:
                    self._syntax_tree_update_callback()
                return True
        finally:
            self._parser.timeout_micros = saved_timeout

    def get_line(self, index: int) -> str:
        """Return the string representing the line, not including new line characters.

        Args:
            line_index: The index of the line.

        Returns:
            The string representing the line.
        """
        line_string = self[index]
        return line_string

    def _location_to_byte_offset(self, location: Location) -> int:
        """Given a document coordinate, return the byte offset of that coordinate.
        This method only does work if tree-sitter was imported, otherwise it returns 0.

        Args:
            location: The location to convert.

        Returns:
            An integer byte offset for the given location.
        """
        lines = self._lines
        row, column = location
        lines_above = lines[:row]
        end_of_line_width = len(self.newline)
        bytes_lines_above = sum(
            len(_utf8_encode(line)) + end_of_line_width for line in lines_above
        )
        if row < len(lines):
            bytes_on_left = len(_utf8_encode(lines[row][:column]))
        else:
            bytes_on_left = 0
        byte_offset = bytes_lines_above + bytes_on_left
        return byte_offset

    def _location_to_point(self, location: Location) -> tuple[int, int]:
        """Convert a document location (row_index, column_index) to a tree-sitter
        point (row_index, byte_offset_from_start_of_row). If tree-sitter isn't available
        returns (0, 0).

        Args:
            location: A location (row index, column codepoint offset)

        Returns:
            The point corresponding to that location (row index, column byte offset).
        """
        lines = self._lines
        row, column = location
        if row < len(lines):
            bytes_on_left = len(_utf8_encode(lines[row][:column]))
        else:
            bytes_on_left = 0
        return row, bytes_on_left

    def _read_callable(
        self,
        byte_offset: int,
        point: tuple[int, int],
        lines: list[str],
    ) -> bytes:
        """A callable which informs tree-sitter about the document content.

        This is passed to tree-sitter which will call it frequently to retrieve
        the bytes from the document.

        Args:
            byte_offset: The number of (utf-8) bytes from the start of the document.
            point: A tuple (row index, column *byte* offset). Note that this differs
                from our Location tuple which is (row_index, column codepoint offset).
            lines: The lines of the document being parsed.

        Returns:
            All the utf-8 bytes between the byte_offset/point and the end of the current
                line _including_ the line separator character(s). Returns None if the
                offset/point requested by tree-sitter doesn't correspond to a byte.
        """
        row, column = point
        newline = self.newline

        row_out_of_bounds = row >= len(lines)
        if row_out_of_bounds:
            return b""
        else:
            row_text = lines[row]

        encoded_row = _utf8_encode(row_text)
        encoded_row_length = len(encoded_row)

        if column < encoded_row_length:
            return encoded_row[column:] + _utf8_encode(newline)
        elif column == encoded_row_length:
            return _utf8_encode(newline[0])
        elif column == encoded_row_length + 1:
            if newline == "\r\n":
                return b"\n"

        return b""


class BackgroundSyntaxParser:
    """A provider of incremental background parsing for syntax highlighting.

    This runs tree-sitter parsing as a parallel, background asyncio task. This
    prevents occasional, relatively long parsing times from making `TextArea`
    editing become unresponsive.
    """

    PARSE_TIME_SLICE = 0.005
    PARSE_TIMEOUT_MICROSECONDS = int(PARSE_TIME_SLICE * 1_000_000)

    def __init__(self, document: SyntaxAwareDocument):
        self._document_ref = weakref.ref(document)
        self._event = Event()
        self._task: Task = create_task(self._execute_reparsing())
        self._force_update = False

    def stop(self):
        """Stop running as a background task."""
        self._task.cancel()

    def trigger_syntax_tree_update(self, force_update: bool) -> None:
        """Trigger a new syntax tree update to run in the background.

        Args:
            force_update: When set, ensure that the syntax tree is regenerated
                unconditionally.
        """
        if force_update:
            self._force_update = True
        self._event.set()

    async def _execute_reparsing(self) -> None:
        """Run, as a task, tree-sitter reparse operations on demand."""
        while True:
            try:
                try:
                    await self._event.wait()
                except Exception as e:
                    return
                self._event.clear()
                force_update = self._force_update
                self._force_update = False
                await self._perform_a_single_reparse(force_update)
            except CancelledError:
                return

    async def _perform_a_single_reparse(self, force_update: bool) -> None:
        document = self._document_ref()
        if document is None:
            return
        if not (document.apply_pending_syntax_edits() or force_update):
            return

        # In order to allow the user to continue editing without interruption, we reparse
        # a snapshot of the TextArea's document.
        copy_of_text_for_parsing = document.copy_of_lines()

        # Use tree-sitter's parser timeout mechanism, when necessary, break the
        # full reparse into multiple steps. Most of the time, tree-sitter is so
        # fast that no looping occurs.
        parsed_ok = False
        while not parsed_ok:
            parsed_ok = document.reparse(
                self.PARSE_TIMEOUT_MICROSECONDS, lines=copy_of_text_for_parsing
            )
            if not parsed_ok:
                # Sleeping for zero seconds allows other tasks, I/O, *etc.* to execute,
                # keeping the TextArea and other widgets responsive.
                await sleep(0.0)
