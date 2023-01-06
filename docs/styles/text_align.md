# Text-align

The `text-align` rule sets the text alignment in a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-align: <a href="../../css_types/text_align">&lt;text-align&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `text-align` rule accepts a value of the type [`<text-align>`](../css_types/text_align.md) that defines how text is aligned inside the widget.

### Values

--8<-- "docs/snippets/type_syntax/text_align.md"

### Defaults

The default value is `start`.

## Example

This example shows, from top to bottom: `left`, `center`, `right`, and `justify` text alignments.

=== "Output"

    ```{.textual path="docs/examples/styles/text_align.py"}
    ```

=== "text_align.py"

    ```python
    --8<-- "docs/examples/styles/text_align.py"
    ```

=== "text_align.css"

    ```css hl_lines="2 7 12 17"
    --8<-- "docs/examples/styles/text_align.css"
    ```

[//]: # (TODO: Add an example that shows how `start` and `end` change when RTL support is added.)

## CSS

```sass
/* Set text in the widget to be right aligned */
text-align: right;
```

## Python

```python
# Set text in the widget to be right aligned
widget.styles.text_align = "right"
```
