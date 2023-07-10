# Scrollbar-color-hover

The `scrollbar-color-hover` style sets the color of the scrollbar when the cursor is over it.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_color_hover">scrollbar-color-hover</a>: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-color-hover` accepts a [`<color>`](../../../css_types/color) (with an optional opacity level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the color of a scrollbar when the cursor is over it.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.css"

    ```sass hl_lines="7"
    --8<-- "docs/examples/styles/scrollbars2.css"
    ```

## CSS

```sass
scrollbar-color-hover: pink;
```

## Python

```py
widget.styles.scrollbar_color_hover = "pink"
```

## See also

 - [`scrollbar-bakcground-hover`](./scrollbar_color_hover.md) to set the scrollbar bakcground color when the mouse pointer is over it.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
 - [`scrollbar-color-active`](./scrollbar_color_active.md) to set the scrollbar color when the scrollbar is being dragged.
