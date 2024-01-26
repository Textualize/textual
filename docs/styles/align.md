# Align

The `align` style aligns children within a container.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `align` style takes a [`<horizontal>`](../css_types/horizontal.md) followed by a [`<vertical>`](../css_types/vertical.md).

You can also set the alignment for each axis individually with `align-horizontal` and `align-vertical`.

## Examples

### Basic usage

This example contains a simple app with two labels centered on the screen with `align: center middle;`:

=== "Output"

    ```{.textual path="docs/examples/styles/align.py"}
    ```

=== "align.py"

    ```python
    --8<-- "docs/examples/styles/align.py"
    ```

=== "align.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/align.tcss"
    ```

### All alignments

The next example shows a 3 by 3 grid of containers with text labels.
Each label has been aligned differently inside its container, and its text shows its `align: ...` value.

=== "Output"

    ```{.textual path="docs/examples/styles/align_all.py"}
    ```

=== "align_all.py"

    ```python
    --8<-- "docs/examples/styles/align_all.py"
    ```

=== "align_all.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30 34"
    --8<-- "docs/examples/styles/align_all.tcss"
    ```

## CSS

```css
/* Align child widgets to the center. */
align: center middle;
/* Align child widget to the top right */
align: right top;

/* Change the horizontal alignment of the children of a widget */
align-horizontal: right;
/* Change the vertical alignment of the children of a widget */
align-vertical: middle;
```

## Python
```python
# Align child widgets to the center
widget.styles.align = ("center", "middle")
# Align child widgets to the top right
widget.styles.align = ("right", "top")

# Change the horizontal alignment of the children of a widget
widget.styles.align_horizontal = "right"
# Change the vertical alignment of the children of a widget
widget.styles.align_vertical = "middle"
```

## See also

 - [`content-align`](./content_align.md) to set the alignment of content inside a widget.
 - [`text-align`](./text_align.md) to set the alignment of text in a widget.
