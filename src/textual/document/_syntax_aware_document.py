from __future__ import annotations

try:
    from tree_sitter import Language, Node, Parser, Query, QueryCursor, Tree

    TREE_SITTER = True
except ImportError:
    TREE_SITTER = False


from textual.document._document import Document, EditResult, Location, _utf8_encode

_UINT32_MAX = 0xFFFFFFFF


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

        self._syntax_tree: Tree = self._parser.parse(self._read_callable)  # type: ignore
        """The tree-sitter Tree (syntax tree) built from the document."""

    def prepare_query(self, query: str) -> Query | None:
        """Prepare a tree-sitter tree query.

        Queries should be prepared once, then reused.

        To execute a query, call `query_syntax_tree`.

        Args:
            query: The string query to prepare.

        Returns:
            The prepared query.
        """
        return Query(self.language, query)

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
        cursor = QueryCursor(query)

        if start_point is not None or end_point is not None:
            if start_point is None:
                start_point = (0, 0)
            if end_point is None:
                end_point = (_UINT32_MAX, _UINT32_MAX)

            cursor.set_point_range(start_point, end_point)

        captures = cursor.captures(self._syntax_tree.root_node)
        return captures

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
        self._syntax_tree.edit(
            start_byte=start_byte,
            old_end_byte=old_end_byte,
            new_end_byte=start_byte + text_byte_length,
            start_point=start_point,
            old_end_point=old_end_point,
            new_end_point=self._location_to_point(end_location),
        )
        # Incrementally parse the document.
        self._syntax_tree = self._parser.parse(
            self._read_callable,
            self._syntax_tree,  # type: ignore[arg-type]
        )

        return replace_result

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

    def _read_callable(self, byte_offset: int, point: tuple[int, int]) -> bytes:
        """A callable which informs tree-sitter about the document content.

        This is passed to tree-sitter which will call it frequently to retrieve
        the bytes from the document.

        Args:
            byte_offset: The number of (utf-8) bytes from the start of the document.
            point: A tuple (row index, column *byte* offset). Note that this differs
                from our Location tuple which is (row_index, column codepoint offset).

        Returns:
            All the utf-8 bytes between the byte_offset/point and the end of the current
                line _including_ the line separator character(s). Returns None if the
                offset/point requested by tree-sitter doesn't correspond to a byte.
        """
        row, column = point
        lines = self._lines
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
