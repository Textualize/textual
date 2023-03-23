# Content-align

The `content-align` style aligns content _inside_ a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
content-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

content-align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
content-align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `content-align` style takes a [`<horizontal>`](../../css_types/horizontal) followed by a [`<vertical>`](../../css_types/vertical).

You can specify the alignment of content on both the horizontal and vertical axes at the same time,
or on each of the axis separately.
To specify content alignment on a single axis, use the respective style and type:

 - `content-align-horizontal` takes a [`<horizontal>`](../../css_types/horizontal) and does alignment along the horizontal axis; and
 - `content-align-vertical` takes a [`<vertical>`](../../css_types/vertical) and does alignment along the vertical axis.

## Examples

### Basic usage

This first example shows three labels stacked vertically, each with different content alignments.

=== "Output"

    ```{.textual path="docs/examples/styles/content_align.py"}
    ```

=== "content_align.py"

    ```python
    --8<-- "docs/examples/styles/content_align.py"
    ```

=== "content_align.css"

    ```sass hl_lines="2 7-8 13"
    --8<-- "docs/examples/styles/content_align.css"
    ```

### All content alignments

The next example shows a 3 by 3 grid of labels.
Each label has its text aligned differently.

=== "Output"

    ```{.textual path="docs/examples/styles/content_align_all.py"}
    ```

=== "content_align_all.py"

    ```py
    --8<-- "docs/examples/styles/content_align_all.py"
    ```

=== "content_align_all.css"

    ```sass hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/content_align_all.css"
    ```

## CSS

```sass
/* Align content in the very center of a widget */
content-align: center middle;
/* Align content at the top right of a widget */
content-align: right top;

/* Change the horizontal alignment of the content of a widget */
content-align-horizontal: right;
/* Change the vertical alignment of the content of a widget */
content-align-vertical: middle;
```

## Python
```python
# Align content in the very center of a widget
widget.styles.content_align = ("center", "middle")
# Align content at the top right of a widget
widget.styles.content_align = ("right", "top")

# Change the horizontal alignment of the content of a widget
widget.styles.content_align_horizontal = "right"
# Change the vertical alignment of the content of a widget
widget.styles.content_align_vertical = "middle"
```

## See also

 - [`align`](./align.md) to set the alignment of children widgets inside a container.
 - [`text-align`](./text_align.md) to set the alignment of text in a widget.
