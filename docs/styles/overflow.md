# Overflow

The `overflow` rule specifies if and when scrollbars should be displayed on the `x` and `y` axis. The rule takes two overflow values; one for the horizontal bar (x axis), followed by the vertical bar (y-axis).

| Overflow value | Effect                                                                    |
| -------------- | ------------------------------------------------------------------------- |
| `"auto"`       | Automatically show the scrollbar if the content doesn't fit (the default) |
| `"hidden"`     | Never show the scrollbar                                                  |
| `"scroll"`     | Always show the scrollbar                                                 |

The default value for overflow is `"auto auto"` which will show scrollbars automatically for both scrollbars if content doesn't fit within container.

Overflow may also be set independently by setting the `overflow-x` rule for the horizontal bar, and `overflow-y` for the vertical bar.

## Example

Here we split the screen in to left and right sections, each with three vertically scrolling widgets that do not fit in to the height of the terminal.

The left side has `overflow-y: auto` (the default) and will automatically show a scrollbar. The right side has `overflow-y: hidden` which will prevent a scrollbar from being show.

=== "overflow.py"

    ```python
    --8<-- "docs/examples/styles/overflow.py"
    ```

=== "overflow.css"

    ```css
    --8<-- "docs/examples/styles/overflow.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/overflow.py"}
    ```

## CSS

```sass
/* Automatic scrollbars on both axies (the default) */
overflow: auto auto;

/* Hide the vertical scrollbar */
overflow-y: hidden;

/* Always show the horizontal scrollbar */
overflow-x: scroll;
```

## Python

```python
# Hide the vertical scrollbar
widget.styles.overflow_y = "hidden"

# Always show the horizontal scrollbar
widget.styles.overflow_x = "scroll"

```
