# TextArea

!!! tip "Added in version 0.34.0"

A widget for editing text which may span multiple lines.

- [x] Focusable
- [ ] Container


## Guide

### Basic example

Here's an example app which loads some Python code, sets the syntax highlighting language
to Python, and selects some text.

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area.py"}
    ```

=== "text_area_example.py"

    ```python
    --8<-- "docs/examples/widgets/text_area.py"
    ```


## Reactive attributes

| Name                | Type                      | Default                 | Description                                       |
|---------------------|---------------------------|-------------------------|---------------------------------------------------|
| `language`          | `str \| Language \| None` | `None`                  | The language to use for syntax highlighting.      |
| `theme`             | `str \| SyntaxTheme`      | `SyntaxTheme.default()` | The theme to use for syntax highlighting.         |
| `selection`         | `Selection`               | `Selection()`           | The current selection.                            |
| `show_line_numbers` | `bool`                    | `True`                  | Show or hide line numbers.                        |
| `indent_width`      | `int`                     | `4`                     | The number of spaces to indent and width of tabs. |

## Bindings

The `TextArea` widget defines the following bindings:

::: textual.widgets._text_area.TextArea.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Component classes

The `TextArea` widget provides the following component classes:

::: textual.widgets._text_area.TextArea.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Additional notes

### Tab characters

The character(s) inserted when you press tab is controlled by setting the `indent_type` attribute to either `tabs` or `spaces`.

If `indent_type == "spaces"`, pressing ++tab++ will insert `indent_width` spaces.

### Python 3.7 is not supported

Syntax highlighting is not available on Python 3.7. Highlighting will fail _silently_, so end-users who are running Python 3.7 can still edit text without highlighting, even if a `language` and `syntax_theme` is set.

## See also

- [`Input`][textual.widgets.Input] - for single-line text input.

---


::: textual.widgets.TextArea
    options:
      heading_level: 2
