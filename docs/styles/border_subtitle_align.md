# Border-subtitle-align

The `border-subtitle-align` style sets the horizontal alignment for the border subtitle.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-subtitle-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `border-subtitle-align` style takes a [`<horizontal>`](../css_types/horizontal.md) that determines where the border subtitle is aligned along the top edge of the border.
This means that the border corners are always visible.

### Default

The default alignment is `right`.


## Examples

### Basic usage

This example shows three labels, each with a different border subtitle alignment:

=== "Output"

    ```{.textual path="docs/examples/styles/border_subtitle_align.py"}
    ```

=== "border_subtitle_align.py"

    ```py
    --8<-- "docs/examples/styles/border_subtitle_align.py"
    ```

=== "border_subtitle_align.tcss"

    ```css
    --8<-- "docs/examples/styles/border_subtitle_align.tcss"
    ```


### Complete usage reference

--8<-- "docs/snippets/border_sub_title_align_all_example.md"


## CSS

```css
border-subtitle-align: left;
border-subtitle-align: center;
border-subtitle-align: right;
```

## Python

```py
widget.styles.border_subtitle_align = "left"
widget.styles.border_subtitle_align = "center"
widget.styles.border_subtitle_align = "right"
```

## See also

--8<-- "docs/snippets/see_also_border.md"
