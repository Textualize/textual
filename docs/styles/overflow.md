# Overflow

The `overflow` style specifies if and when scrollbars should be displayed.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
overflow: <a href="../../css_types/overflow">&lt;overflow&gt;</a> <a href="../../css_types/overflow">&lt;overflow&gt;</a>;

overflow-x: <a href="../../css_types/overflow">&lt;overflow&gt;</a>;
overflow-y: <a href="../../css_types/overflow">&lt;overflow&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `overflow` accepts two values that determine when to display scrollbars in a container widget.
The two values set the overflow for the horizontal and vertical axes, respectively.

Overflow may also be set individually for each axis:

 - `overflow-x` sets the overflow for the horizontal axis; and
 - `overflow-y` sets the overflow for the vertical axis.

### Defaults

The default setting for containers is `overflow: auto auto`.

!!! warning

    Some built-in containers like `Horizontal` and `VerticalScroll` override these defaults.

## Example

Here we split the screen into left and right sections, each with three vertically scrolling widgets that do not fit into the height of the terminal.

The left side has `overflow-y: auto` (the default) and will automatically show a scrollbar.
The right side has `overflow-y: hidden` which will prevent a scrollbar from being shown.

=== "Output"

    ```{.textual path="docs/examples/styles/overflow.py"}
    ```

=== "overflow.py"

    ```python
    --8<-- "docs/examples/styles/overflow.py"
    ```

=== "overflow.css"

    ```sass hl_lines="19"
    --8<-- "docs/examples/styles/overflow.css"
    ```

## CSS

```sass
/* Automatic scrollbars on both axes (the default) */
overflow: auto auto;

/* Hide the vertical scrollbar */
overflow-y: hidden;

/* Always show the horizontal scrollbar */
overflow-x: scroll;
```

## Python

Overflow cannot be programmatically set for both axes at the same time.

```python
# Hide the vertical scrollbar
widget.styles.overflow_y = "hidden"

# Always show the horizontal scrollbar
widget.styles.overflow_x = "scroll"
```
