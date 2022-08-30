# Text-align

The `text-align` rule aligns text within a widget.

## Syntax

```
text-align: [left|start|center|right|end|justify];
```

### Values

| Value     | Description                      |
|-----------|----------------------------------|
| `left`    | Left aligns text in the widget   |
| `start`   | Left aligns text in the widget   |
| `center`  | Center aligns text in the widget |
| `right`   | Right aligns text in the widget  |
| `end`     | Right aligns text in the widget  |
| `justify` | Justifies text in the widget     |

## Example

This example shows, from top to bottom: `left`, `center`, `right`, and `justify` text alignments.

=== "text_align.py"

    ```python
    --8<-- "docs/examples/styles/text_align.py"
    ```

=== "text_align.css"

    ```css
    --8<-- "docs/examples/styles/text_align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/text_align.py"}
    ```

## CSS

```sass
/* Set text in all Widgets to be right aligned */
Widget {
    text-align: right;
}
```

## Python

```python
# Set text in the widget to be right aligned
widget.styles.text_align = "right"
```
