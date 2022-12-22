# Align

The `align` style aligns children within a container.
Not to be confused with [`content-align`](../content_align).

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `align` takes a [`<horizontal>`](../../css_types/horizontal) followed by a [`<vertical>`](../../css_types/vertical).

You can specify the alignment of children on both the horizontal and vertical axes at the same time,
or on each of the axis separately.
To specify alignment on a single axis, use the respective style and type:

 - `align-horizontal` takes a [`<horizontal>`](../../css_types/horizontal) and does alignment along the horizontal axis; and
 - `align-vertical` takes a [`<vertical>`](../../css_types/vertical) and does alignment along the vertical axis.

### Values

#### &lt;horizontal&gt;

--8<-- "docs/snippets/type_syntax/horizontal.md"

#### &lt;vertical&gt;

--8<-- "docs/snippets/type_syntax/vertical.md"


## Examples

This example contains a simple app with two labels centered on the screen with `align: center middle;`:

=== "align.py"

    ```python
    --8<-- "docs/examples/styles/align.py"
    ```

=== "align.css"

    ```scss hl_lines="2"
    --8<-- "docs/examples/styles/align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/align.py"}

    ```

The next example shows a 3 by 3 grid of containers with text labels.
Each label has been aligned differently inside its container, and its text shows its `align: ...` value.

=== "align_all.py"

    ```python
    --8<-- "docs/examples/styles/align_all.py"
    ```

=== "align_all.css"

    ```css
    --8<-- "docs/examples/styles/align_all.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/align_all.py"}
    ```

## CSS

```sass
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
