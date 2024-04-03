# Offset

The `offset` style defines an offset for the position of the widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
offset: <a href="../../css_types/scalar">&lt;scalar&gt;</a> <a href="../../css_types/scalar">&lt;scalar&gt;</a>;

offset-x: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
offset-y: <a href="../../css_types/scalar">&lt;scalar&gt;</a>
--8<-- "docs/snippets/syntax_block_end.md"

The two [`<scalar>`](../css_types/scalar.md) in the `offset` define, respectively, the offsets in the horizontal and vertical axes for the widget.

To specify an offset along a single axis, you can use `offset-x` and `offset-y`.

## Example

In this example, we have 3 widgets with differing offsets.

=== "Output"

    ```{.textual path="docs/examples/styles/offset.py"}
    ```

=== "offset.py"

    ```python
    --8<-- "docs/examples/styles/offset.py"
    ```

=== "offset.tcss"

    ```css hl_lines="13 20 27"
    --8<-- "docs/examples/styles/offset.tcss"
    ```

## CSS

```css
/* Move the widget 8 cells in the x direction and 2 in the y direction */
offset: 8 2;

/* Move the widget 4 cells in the x direction
offset-x: 4;
/* Move the widget -3 cells in the y direction
offset-y: -3;
```

## Python

You cannot change programmatically the offset for a single axis.
You have to set the two axes at the same time.

```python
# Move the widget 2 cells in the x direction, and 4 in the y direction.
widget.styles.offset = (2, 4)
```

## See also

 - The [layout guide](../guide/layout.md#offsets) section on offsets.
