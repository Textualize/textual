# Text-style

The `text-style` sets the style for the text in a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-style: <a href="../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`text-style` will take all the values specified and will apply that styling combination to the text in the widget.

### Values

--8<-- "docs/snippets/type_syntax/text_style.md"

## Examples

Each of the three text panels has a different text style, respectively `bold`, `italic`, and `reverse`, from left to right.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style.py" lines=14}
    ```

=== "text_style.py"

    ```python
    --8<-- "docs/examples/styles/text_style.py"
    ```

=== "text_style.css"

    ```css
    --8<-- "docs/examples/styles/text_style.css"
    ```

The next example shows all different styles on their own, as well as some combinations of styles in a single widget.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style_all.py"}
    ```

=== "text_style_all.py"

    ```python
    --8<-- "docs/examples/styles/text_style_all.py"
    ```

=== "text_style_all.css"

    ```css
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
