# Scrollbar-background-hover

The `scrollbar-background-hover` sets the background color of the scrollbar when the cursor is over it.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background_hover">scrollbar-background-hover</a>: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-background-hover` accepts a [`<color>`](../../../css_types/color) (with an optional transparency level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the background color of a scrollbar when the cursor is over it.

### Values

#### &lt;color&gt;

--8<-- "docs/snippets/type_syntax/color.md"

#### &lt;percentage&gt;

--8<-- "docs/snippets/type_syntax/percentage.md"

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

    ```sass hl_lines="4"
    --8<-- "docs/examples/styles/scrollbars2.css"
    ```

## CSS

```sass
scrollbar-background-hover: purple;
```

## Python

```py
widget.styles.scrollbar_background_hover = "purple"
```
