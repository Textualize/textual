from .tokenize import Token


class DeclarationError(Exception):
    def __init__(self, name: str, token: Token, message: str) -> None:
        self.token = token
        super().__init__(message)


class StyleTypeError(TypeError):
    pass


class StyleValueError(ValueError):
    pass


class StylesheetError(Exception):
    pass
