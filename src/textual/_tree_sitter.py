from __future__ import annotations

try:
    import tree_sitter_bash
    import tree_sitter_css
    import tree_sitter_go
    import tree_sitter_html
    import tree_sitter_java
    import tree_sitter_javascript
    import tree_sitter_json
    import tree_sitter_markdown
    import tree_sitter_python
    import tree_sitter_regex
    import tree_sitter_rust
    import tree_sitter_sql
    import tree_sitter_toml
    import tree_sitter_xml
    import tree_sitter_yaml
    from tree_sitter import Language

    _tree_sitter = True

    _languages = {
        "python": Language(tree_sitter_python.language()),
        "json": Language(tree_sitter_json.language()),
        "markdown": Language(tree_sitter_markdown.language()),
        "yaml": Language(tree_sitter_yaml.language()),
        "toml": Language(tree_sitter_toml.language()),
        "rust": Language(tree_sitter_rust.language()),
        "html": Language(tree_sitter_html.language()),
        "css": Language(tree_sitter_css.language()),
        "xml": Language(tree_sitter_xml.language_xml()),
        "regex": Language(tree_sitter_regex.language()),
        "sql": Language(tree_sitter_sql.language()),
        "javascript": Language(tree_sitter_javascript.language()),
        "java": Language(tree_sitter_java.language()),
        "bash": Language(tree_sitter_bash.language()),
        "go": Language(tree_sitter_go.language()),
    }

    def get_language(language_name: str) -> Language | None:
        return _languages.get(language_name)

except ImportError:
    _tree_sitter = False
    _languages = {}

TREE_SITTER = _tree_sitter
BUILTIN_LANGUAGES: dict[str, "Language"] = _languages
