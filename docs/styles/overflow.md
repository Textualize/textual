# Overflow

The `overflow` rule specifies if and when scrollbars should be displayed on the `x` and `y` axis. There are two values for each scrollbar, which may be set together or independently to one of the follow three values:

- `"auto"` Automatically show the scrollbar if the content doesn't fit
- `"hidden"` Never show the scrollbar
- `"scroll"` Always show the scrollbar

The default is "auto" which will show the scrollbar if content doesn't fit within container, otherwise the scrollbar will be hidden.

## Example

Here we split the screen in to left and right sections, each with three vertically scrolling widgets that do not fit in to the height of the terminal.

The left side has `overflow-y: auto` (the default) and will automatically show a scrollbar. The right side has `overflow-y: hidden` which will prevent a scrollbar from being show.

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/overflow.py"
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
