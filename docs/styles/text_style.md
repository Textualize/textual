# Text-style

The `text-style` style sets the style for the text in a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-style: <a href="../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`text-style` will take all the values specified and will apply that styling combination to the text in the widget.

## Examples

### Basic usage

Each of the three text panels has a different text style, respectively `bold`, `italic`, and `reverse`, from left to right.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style.py" lines=14}
    ```

=== "text_style.py"

    ```python
    --8<-- "docs/examples/styles/text_style.py"
    ```

=== "text_style.css"

    ```sass hl_lines="9 13 17"
    --8<-- "docs/examples/styles/text_style.css"
    ```

### All text styles

The next example shows all different text styles on their own, as well as some combinations of styles in a single widget.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style_all.py"}
    ```

=== "text_style_all.py"

    ```python
    --8<-- "docs/examples/styles/text_style_all.py"
    ```

=== "text_style_all.css"

    ```sass hl_lines="2 6 10 14 18 22 26 30"
    --8<-- "docs/examples/styles/text_style_all.css"
    ```

## CSS

```sass
text-style: italic;
```

## Python

```python
widget.styles.text_style = "italic"
```
