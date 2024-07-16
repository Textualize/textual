# Border-title-align

The `border-title-align` style sets the horizontal alignment for the border title.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-title-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `border-title-align` style takes a [`<horizontal>`](../css_types/horizontal.md) that determines where the border title is aligned along the top edge of the border.
This means that the border corners are always visible.

### Default

The default alignment is `left`.


## Examples

### Basic usage

This example shows three labels, each with a different border title alignment:

=== "Output"

    ```{.textual path="docs/examples/styles/border_title_align.py"}
    ```

=== "border_title_align.py"

    ```py
    --8<-- "docs/examples/styles/border_title_align.py"
    ```

=== "border_title_align.tcss"

    ```css
    --8<-- "docs/examples/styles/border_title_align.tcss"
    ```


### Complete usage reference

--8<-- "docs/snippets/border_sub_title_align_all_example.md"


## CSS

```css
border-title-align: left;
border-title-align: center;
border-title-align: right;
```

## Python

```py
widget.styles.border_title_align = "left"
widget.styles.border_title_align = "center"
widget.styles.border_title_align = "right"
```

## See also

--8<-- "docs/snippets/see_also_border.md"
