# Border

The `border` style enables the drawing of a box around a widget.

A border style may also be applied to individual edges with `border-top`, `border-right`, `border-bottom`, and `border-left`.

!!! note

    [`border`](./border.md) and [`outline`](./outline.md) cannot coexist in the same edge of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>] [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];

border-top: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>] [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
border-right: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
border-bottom: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
border-left: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
--8<-- "docs/snippets/syntax_block_end.md"

In CSS, the border is set with a [border style](./border.md) and a color. Both are optional. An optional percentage may be added to blend the border with the background color.

In Python, the border is set with a tuple of [border style](./border.md) and a color.


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

=== "border.tcss"

    ```css hl_lines="4 10 16"
    --8<-- "docs/examples/styles/border.tcss"
    ```

### All border types

The next example shows a grid with all the available border types.

=== "Output"

    ```{.textual path="docs/examples/styles/border_all.py"}
    ```

=== "border_all.py"

    ```py
    --8<-- "docs/examples/styles/border_all.py"
    ```

=== "border_all.tcss"

    ```css
    --8<-- "docs/examples/styles/border_all.tcss"
    ```

### Borders and outlines

--8<-- "docs/snippets/border_vs_outline_example.md"

## CSS

```css
/* Set a heavy white border */
border: heavy white;

/* Set a red border on the left */
border-left: outer red;

/* Set a rounded orange border, 50% opacity. */
border: round orange 50%;
```

## Python

```python
# Set a heavy white border
widget.styles.border = ("heavy", "white")

# Set a red border on the left
widget.styles.border_left = ("outer", "red")
```

## See also

 - [`box-sizing`](./box_sizing.md) to specify how to account for the border in a widget's dimensions.
 - [`outline`](./outline.md) to add an outline around the content of a widget.
--8<-- "docs/snippets/see_also_border.md"
