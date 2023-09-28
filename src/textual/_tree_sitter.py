from __future__ import annotations

try:
    from tree_sitter import Language, Parser, Tree
    from tree_sitter.binding import Query
    from tree_sitter_languages import get_language, get_parser

    TREE_SITTER = True
except ImportError:
    TREE_SITTER = False
