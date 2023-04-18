# Outline

The `outline` style enables the drawing of a box around the content of a widget, which means the outline is drawn _over_ the content area.

!!! note

    [`border`](./border.md) and [`outline`](./outline.md) cannot coexist in the same edge of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
outline: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];

outline-top: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-right: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-bottom: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-left: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The style `outline` accepts an optional [`<border>`](../../css_types/border) that sets the visual style of the widget outline and an optional [`<color>`](../../css_types/color) to set the color of the outline.

Unlike the style [`border`](./border.md), the frame of the outline is drawn over the content area of the widget.
This rule can be useful to add temporary emphasis on the content of a widget, if you want to draw the user's attention to it.

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively, when applied to the CSS rule [`border`](../styles/border.md):

```
textual borders
```

## Examples

### Basic usage

This example shows a widget with an outline.
Note how the outline occludes the text area.

=== "Output"

    ```{.textual path="docs/examples/styles/outline.py"}
    ```

=== "outline.py"

    ```python
    --8<-- "docs/examples/styles/outline.py"
    ```

=== "outline.css"

    ```sass hl_lines="8"
    --8<-- "docs/examples/styles/outline.css"
    ```

### All outline types

The next example shows a grid with all the available outline types.

=== "Output"

    ```{.textual path="docs/examples/styles/outline_all.py"}
    ```

=== "outline_all.py"

    ```py
    --8<-- "docs/examples/styles/outline_all.py"
    ```

=== "outline_all.css"

    ```sass hl_lines="2 6 10 14 18 22 26 30 34 38 42 46 50 54 58"
    --8<-- "docs/examples/styles/outline_all.css"
    ```

### Borders and outlines

--8<-- "docs/snippets/border_vs_outline_example.md"

## CSS

```sass
/* Set a heavy white outline */
outline:heavy white;

/* set a red outline on the left */
outline-left:outer red;
```

## Python

```python
# Set a heavy white outline
widget.outline = ("heavy", "white")

# Set a red outline on the left
widget.outline_left = ("outer", "red")
```

## See also

 - [`border`](./border.md) to add a border around a widget.
