"""
Utilities related to content markup.


"""


from __future__ import annotations


from operator import itemgetter


from textual.css.parse import substitute_references
from textual.css.tokenizer import UnexpectedEnd


__all__ = ["MarkupError", "escape", "to_content"]


import re
from string import Template
from typing import TYPE_CHECKING, Callable, Mapping, Match


from textual._context import active_app
from textual.color import Color
from textual.css.tokenize import (
    COLOR,
    PERCENT,
    TOKEN,
    VARIABLE_REF,
    Expect,
    TokenizerState,
    tokenize_values,
)
from textual.style import Style


if TYPE_CHECKING:
    from textual.content import Content




class MarkupError(Exception):
