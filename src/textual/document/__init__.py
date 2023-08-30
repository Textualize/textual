from ._document import Document, DocumentBase, EditResult, Location, Selection
from ._languages import VALID_LANGUAGES
from ._syntax_aware_document import (
    EndColumn,
    Highlight,
    HighlightName,
    StartColumn,
    SyntaxAwareDocument,
)
from ._text_area_theme import DEFAULT_SYNTAX_THEME, TextAreaTheme

__all__ = [
    "Document",
    "DocumentBase",
    "EndColumn",
    "Highlight",
    "HighlightName",
    "Location",
    "EditResult",
    "Selection",
    "StartColumn",
    "SyntaxAwareDocument",
    "TextAreaTheme",
    "VALID_LANGUAGES",
]
