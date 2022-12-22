# Content-align

The `content-align` style aligns content _inside_ a widget.
Not to be confused with [`align`](../align).


## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
content-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

content-align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
content-align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `content-align` takes a [`<horizontal>`](../../css_types/horizontal) followed by a [`<vertical>`](../../css_types/vertical).

You can specify the alignment of content on both the horizontal and vertical axes at the same time,
or on each of the axis separately.
To specify content alignment on a single axis, use the respective style and type:

 - `content-align-horizontal` takes a [`<horizontal>`](../../css_types/horizontal) and does alignment along the horizontal axis; and
 - `content-align-vertical` takes a [`<vertical>`](../../css_types/vertical) and does alignment along the vertical axis.

### Values

#### &lt;horizontal&gt;

--8<-- "docs/snippets/type_syntax/horizontal.md"

#### &lt;vertical&gt;

--8<-- "docs/snippets/type_syntax/vertical.md"

## Examples

This first example shows three labels stacked vertically, each with different content alignments.

=== "content_align.py"

    ```python
    --8<-- "docs/examples/styles/content_align.py"
    ```

=== "content_align.css"

    ```scss hl_lines="2 7-8 13"
    --8<-- "docs/examples/styles/content_align.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/content_align.py"}
    ```

The next example shows a 3 by 3 grid of labels.
Each label has its text aligned differently.

=== "content_align_all.py"

    ```py
    --8<-- "docs/examples/styles/content_align_all.py"
    ```

=== "content_align_all.css"

    ```css
    --8<-- "docs/examples/styles/content_align_all.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/content_align_all.py"}
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
