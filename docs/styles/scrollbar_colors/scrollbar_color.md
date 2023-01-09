# Scrollbar-color

The `scrollbar-color` sets the color of the scrollbar.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_color">scrollbar-color</a>: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-color` accepts a [`<color>`](../../../css_types/color) (with an optional transparency level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the color of a scrollbar.

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

    ```sass hl_lines="5"
    --8<-- "docs/examples/styles/scrollbars2.css"
    ```

## CSS

```sass
scrollbar-color: cyan;
```

## Python

```py
widget.styles.scrollbar_color = "cyan"
```
