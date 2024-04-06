# Grid-gutter

The `grid-gutter` style sets the size of the gutter in the grid layout.
That is, it sets the space between adjacent cells in the grid.

Gutter is only applied _between_ the edges of cells.
No spacing is added between the edges of the cells and the edges of the container.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-gutter: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-gutter` style takes one or two [`<integer>`](../../css_types/integer.md) that set the length of the gutter along the vertical and horizontal axes.
If only one [`<integer>`](../../css_types/integer.md) is supplied, it sets the vertical and horizontal gutters.
If two are supplied, they set the vertical and horizontal gutters, respectively.

## Example

The example below employs a common trick to apply visually consistent spacing around all grid cells.

=== "Output"

    ```{.textual path="docs/examples/styles/grid_gutter.py"}
    ```

=== "grid_gutter.py"

    ```py
    --8<-- "docs/examples/styles/grid_gutter.py"
    ```

=== "grid_gutter.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_gutter.tcss"
    ```

    1. We set the horizontal gutter to be double the vertical gutter because terminal cells are typically two times taller than they are wide. Thus, the result shows visually consistent spacing around grid cells.

## CSS

```css
/* Set vertical and horizontal gutters to be the same */
grid-gutter: 5;

/* Set vertical and horizontal gutters separately */
grid-gutter: 1 2;
```

## Python

Vertical and horizontal gutters correspond to different Python properties, so they must be set separately:

```py
widget.styles.grid_gutter_vertical = "1"
widget.styles.grid_gutter_horizontal = "2"
```
