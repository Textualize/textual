# Content-align

The `content-align` style aligns content _inside_ a widget.
Not to be confused with [`align`](../align).

You can specify the alignment of content on both the horizontal and vertical axes at the same time,
or on each of the axis separately.


## Syntax

```
content-align: <HORIZONTAL> <VERTICAL>;
content-align-horizontal: <HORIZONTAL>;
content-align-vertical: <VERTICAL>;
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

## Examples

This first example shows three labels stacked vertically, each with different content alignments.

=== "content_align.py"

    ```python
    --8<-- "docs/examples/styles/content_align.py"
    ```

=== "content_align.css"

    ```scss hl_lines="2 7-8 13"
    --8<-- "docs/examples/styles/content_align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/content_align.py"}
    ```

The next example shows a 3 by 3 grid of labels.
Each label has its text aligned differently.

=== "content_align_all.py"

    ```py
    --8<-- "docs/examples/styles/content_align_all.py"
    ```

=== "content_align_all.css"

    ```css
    --8<-- "docs/examples/styles/content_align_all.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/content_align_all.py"}
    ```

## CSS

```sass
/* Align content in the very center of a widget */
content-align: center middle;
/* Align content at the top right of a widget */
content-align: right top;

/* Change the horizontal alignment of the content of a widget */
content-align-horizontal: right;
/* Change the vertical alignment of the content of a widget */
content-align-vertical: middle;
```

## Python
```python
# Align content in the very center of a widget
widget.styles.content_align = ("center", "middle")
# Align content at the top right of a widget
widget.styles.content_align = ("right", "top")

# Change the horizontal alignment of the content of a widget
widget.styles.content_align_horizontal = "right"
# Change the vertical alignment of the content of a widget
widget.styles.content_align_vertical = "middle"
```
