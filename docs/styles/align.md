# Align

The `align` style aligns children within a container.

## Syntax

```
align: <HORIZONTAL> <VERTICAL>;
align-horizontal: <HORIZONTAL>;
align-vertical: <VERTICAL>;
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

This example contains a simple app with two labels centered on the screen with `align: center middle;`:

=== "align.py"

    ```python
    --8<-- "docs/examples/styles/align.py"
    ```

=== "align.css"

    ```scss hl_lines="2"
    --8<-- "docs/examples/styles/align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/align.py"}

    ```

The next example shows a 3 by 3 grid of containers with text labels.
Each label has been aligned differently inside its container, and its text shows its `align: ...` value.

=== "align_all.py"

    ```python
    --8<-- "docs/examples/styles/align_all.py"
    ```

=== "align_all.css"

    ```css
    --8<-- "docs/examples/styles/align_all.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/align_all.py"}
    ```

## CSS

```sass
/* Align child widgets to the center. */
align: center middle;
/* Align child widget to th top right */
align: right top;
```

## Python
```python
# Align child widgets to the center
widget.styles.align = ("center", "middle")
# Align child widgets to the top right
widget.styles.align = ("right", "top")
```
