# Border

The `border` rule enables the drawing of a box around a widget.

!!! note

    Due to a Textual limitation, [`border`](./border.md) and [`outline`](./outline.md) cannot coexist in the same edge of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];

border-top: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
border-right: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
border-bottom: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
border-left: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The style `border` accepts an optional [`<border>`](../../css_types/border) that sets the visual style of the widget border and an optional [`<color>`](../../css_types/color) to set the color of the border.

Borders may also be set individually for the four edges of a widget with the `border-top`, `border-right`, `border-bottom` and `border-left` rules.

### Multiple edge rules

If multiple border rules target the same edge, the last rule that targets a specific edge is the one that is applied to that edge.
For example, consider the CSS below:

```sass
Static {
    border-top: dashed red;
    border: solid green;  /* overrides the border-top rule above */
    /* Change the border but just for the bottom edge: */
    border-bottom: double blue;
}
```

The CSS snippet above will add a solid green border around `Static` widgets, except for the bottom edge, which will be double blue.

### Defaults

If `<color>` is specified but `<border>` is not, it defaults to `"solid"`.
If `<border>` is specified but `<color>`is not, it defaults to green (RGB color `"#00FF00"`).

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively:

```
textual borders
```

Alternatively, you can see the examples below.

## Examples

### Basic usage

This examples shows three widgets with different border styles.

=== "Output"

    ```{.textual path="docs/examples/styles/border.py"}
    ```

=== "border.py"

    ```python
    --8<-- "docs/examples/styles/border.py"
    ```

=== "border.css"

    ```sass hl_lines="4 10 16"
    --8<-- "docs/examples/styles/border.css"
    ```

### All border types

The next example shows a grid with all the available border types.

=== "Output"

    ```{.textual path="docs/examples/styles/border_all.py"}
    ```

=== "border_all.py"

    ```py hl_lines="2 6 10 14 18 22 26 30 34 38 42 46 50 54 58"
    --8<-- "docs/examples/styles/border_all.py"
    ```

=== "border_all.css"

    ```sass
    --8<-- "docs/examples/styles/border_all.css"
    ```

### Borders and outlines

The next example makes the difference between [`border`](./border.md) and [`outline`](./outline.md) clearer by having three labels side-by-side.
They contain the same text, have the same width and height, and are styled exactly the same up to their `outline` and [`border`](./border.md) rules.

This example also shows that a widget cannot contain both a `border` and an `outline`:

=== "Output"

    ```{.textual path="docs/examples/styles/outline_vs_border.py"}
    ```

=== "outline_vs_border.py"

    ```python
    --8<-- "docs/examples/styles/outline_vs_border.py"
    ```

=== "outline_vs_border.css"

    ```sass hl_lines="5-7 9-11"
    --8<-- "docs/examples/styles/outline_vs_border.css"
    ```

## CSS

```sass
/* Set a heavy white border */
border: heavy white;

/* set a red border on the left */
border-left: outer red;
```

## Python

```python
# Set a heavy white border
widget.border = ("heavy", "white")

# Set a red border on the left
widget.border_left = ("outer", "red")
```

## See also

 - [`box-sizing`](./box_sizing.md) to specify how to account for the border in a widget's dimensions.
 - [`outline`](./outline.md) to add an outline around the content of a widget.
