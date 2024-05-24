# Scrollbar colors

There are a number of styles to set the colors used in Textual scrollbars.
You won't typically need to do this, as the default themes have carefully chosen colors, but you can if you want to.

| Style                                                             | Applies to                                               |
|-------------------------------------------------------------------|----------------------------------------------------------|
| [`scrollbar-background`](./scrollbar_background.md)               | Scrollbar background.                                    |
| [`scrollbar-background-active`](./scrollbar_background_active.md) | Scrollbar background when the thumb is being dragged.    |
| [`scrollbar-background-hover`](./scrollbar_background_hover.md)   | Scrollbar background when the mouse is hovering over it. |
| [`scrollbar-color`](./scrollbar_color.md)                         | Scrollbar "thumb" (movable part).                        |
| [`scrollbar-color-active`](./scrollbar_color_active.md)           | Scrollbar thumb when it is active (being dragged).       |
| [`scrollbar-color-hover`](./scrollbar_color_hover.md)             | Scrollbar thumb when the mouse is hovering over it.      |
| [`scrollbar-corner-color`](./scrollbar_corner_color.md)           | The gap between the horizontal and vertical scrollbars.  |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background">scrollbar-background</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_background_active">scrollbar-background-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_background_hover">scrollbar-background-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color">scrollbar-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color_active">scrollbar-color-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color_hover">scrollbar-color-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_corner_color">scrollbar-corner-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

## Example

This example shows two panels that contain oversized text.
The right panel sets `scrollbar-background`, `scrollbar-color`, and `scrollbar-corner-color`, and the left panel shows the default colors for comparison.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbars.py"}
    ```

=== "scrollbars.py"

    ```python
    --8<-- "docs/examples/styles/scrollbars.py"
    ```

=== "scrollbars.tcss"

    ```css
    --8<-- "docs/examples/styles/scrollbars.tcss"
    ```
