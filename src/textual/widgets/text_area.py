from textual._text_area_theme import TextAreaTheme
from textual.document._document import (
    Document,
    DocumentBase,
    EditResult,
    Location,
    Selection,
)
from textual.document._languages import BUILTIN_LANGUAGES
from textual.document._syntax_aware_document import SyntaxAwareDocument
from textual.widgets._text_area import (
    Edit,
    EndColumn,
    Highlight,
    HighlightName,
    StartColumn,
)

__all__ = [
    "Edit",
    "EndColumn",
    "Highlight",
    "HighlightName",
    "StartColumn",
    "TextAreaTheme",
    "Document",
    "DocumentBase",
    "Location",
    "EditResult",
    "Selection",
    "SyntaxAwareDocument",
    "BUILTIN_LANGUAGES",
]
