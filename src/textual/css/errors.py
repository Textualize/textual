from .tokenize import Token


class DeclarationError(Exception):
    def __init__(self, name: str, token: Token, message: str) -> None:
        self.name = name
        self.token = token
        self.message = message
        super().__init__(message)


class UnresolvedVariableError(NameError):
    pass


class StyleTypeError(TypeError):
    pass


class StyleValueError(ValueError):
    pass


class StylesheetError(Exception):
    pass
