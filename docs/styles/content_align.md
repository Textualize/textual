# Content-align

The `content-align` style aligns content _inside_ a widget.

You can specify the alignment of content on both the horizontal and vertical axes.

## Syntax

```
content-align: <HORIZONTAL> <VERTICAL>;
```

### Values

#### `HORIZONTAL`

| Value            | Description                                        |
| ---------------- | -------------------------------------------------- |
| `left` (default) | Align content on the left of the horizontal axis   |
| `center`         | Align content in the center of the horizontal axis |
| `right`          | Align content on the right of the horizontal axis  |

#### `VERTICAL`

| Value           | Description                                      |
| --------------- | ------------------------------------------------ |
| `top` (default) | Align content at the top of the vertical axis    |
| `middle`        | Align content in the middle of the vertical axis |
| `bottom`        | Align content at the bottom of the vertical axis |

## Example

=== "content_align.py"

    ```python
    --8<-- "docs/examples/styles/content_align.py"
    ```

=== "content_align.css"

    ```scss
    --8<-- "docs/examples/styles/content_align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/content_align.py"}
    ```

## CSS

```sass
/* Align content in the very center of a widget */
content-align: center middle;
/* Align content at the top right of a widget */
content-align: right top;
```

## Python
```python
# Align content in the very center of a widget
widget.styles.content_align = ("center", "middle")
# Align content at the top right of a widget
widget.styles.content_align = ("right", "top")
```
