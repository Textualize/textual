# Scrollbar-corner-color

The `scrollbar-corner-color` style sets the color of the gap between the horizontal and vertical scrollbars.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_corner_color">scrollbar-corner-color</a>: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-corner-color` accepts a [`<color>`](../../../css_types/color) (with an optional opacity level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the color of the gap between the horizontal and vertical scrollbars of a widget.

## Example

The example below sets the scrollbar corner (bottom-right corner of the screen) to white.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_corner_color.py" lines=5}
    ```

=== "scrollbar_corner_color.py"

    ```py
    --8<-- "docs/examples/styles/scrollbar_corner_color.py"
    ```

=== "scrollbar_corner_color.css"

    ```sass hl_lines="3"
    --8<-- "docs/examples/styles/scrollbar_corner_color.css"
    ```

## CSS

```sass
scrollbar-corner-color: white;
```

## Python

```py
widget.styles.scrollbar_corner_color = "white"
```

## See also

 - [`scrollbar-background`](./scrollbar_background.md) to set the background color of scrollbars.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
