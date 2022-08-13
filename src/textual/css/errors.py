from __future__ import annotations

from rich.console import ConsoleOptions, Console, RenderResult
from rich.traceback import Traceback

from ._help_renderables import HelpText
from .tokenize import Token
from .tokenizer import TokenError


class DeclarationError(Exception):
    def __init__(self, name: str, token: Token, message: str | HelpText) -> None:
        self.name = name
        self.token = token
        self.message = message
        super().__init__(str(message))


class StyleTypeError(TypeError):
    pass


class UnresolvedVariableError(TokenError):
    pass


class StyleValueError(ValueError):
    """Raised when the value of a style property is not valid

    Attributes:
        help_text (HelpText | None): Optional HelpText to be rendered when this
            error is raised.
    """

    def __init__(self, *args, help_text: HelpText | None = None):
        super().__init__(*args)
        self.help_text = help_text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield Traceback.from_exception(type(self), self, self.__traceback__)
        if self.help_text is not None:
            yield ""
            yield self.help_text
            yield ""


class StylesheetError(Exception):
    pass
