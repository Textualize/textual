from __future__ import annotations
from importlib import import_module

from textual import log


try:
    from tree_sitter import Language

    _LANGUAGE_CACHE: dict[str, Language] = {}

    _tree_sitter = True

    def get_language(language_name: str) -> Language | None:
        if language_name in _LANGUAGE_CACHE:
            return _LANGUAGE_CACHE[language_name]

        try:
            module = import_module(f"tree_sitter_{language_name}")
        except ImportError:
            return None
        else:
            try:
                language = Language(module.language(), name=language_name)
            except (OSError, AttributeError):
                log.warning(f"Could not load language {language_name!r}.")
                return None
            else:
                _LANGUAGE_CACHE[language_name] = language
                return language

except ImportError:
    _tree_sitter = False

    def get_language(language_name: str) -> Language | None:
        return None


TREE_SITTER = _tree_sitter
