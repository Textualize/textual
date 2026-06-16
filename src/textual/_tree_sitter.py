from __future__ import annotations

from importlib import import_module

from textual import log

try:
    from tree_sitter import Language

except ImportError:
    _tree_sitter = False

    def get_language(language_name: str) -> Language | None:
        return None

else:
    _tree_sitter = True
    try:
        import tree_sitter_language_pack

    except ImportError:
        _LANGUAGE_CACHE: dict[str, Language] = {}

        def get_language(language_name: str) -> Language | None:
            if language_name in _LANGUAGE_CACHE:
                return _LANGUAGE_CACHE[language_name]

            try:
                module = import_module(f"tree_sitter_{language_name}")
            except ImportError:
                return None
            else:
                try:
                    if language_name == "xml":
                        # xml uses language_xml() instead of language()
                        # it's the only outlier amongst the languages in the `textual[syntax]` extra
                        language = Language(module.language_xml())
                    else:
                        language = Language(module.language())
                except (OSError, AttributeError):
                    log.warning(f"Could not load language {language_name!r}.")
                    return None
                else:
                    _LANGUAGE_CACHE[language_name] = language
                    return language

    else:

        def get_language(language_name: str) -> Language | None:
            try:
                return tree_sitter_language_pack.get_language(language_name)
            # Need to use "Exception" because the current version of tree_sitter_language_pack doesn't have "DownloadError"
            # Should be fixed in version 1.9, see: https://github.com/kreuzberg-dev/tree-sitter-language-pack/issues/133
            except (tree_sitter_language_pack.LanguageNotFoundError, Exception):
                log.warning(f"Could not load language {language_name!r}.")
                return None


TREE_SITTER = _tree_sitter
