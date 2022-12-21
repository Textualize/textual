# Text style

The text style unit is a combination of any of the legal text style values in a space-separated list.

!!! warning

    Not to be confused with the [`text-style`](../text_style.md) CSS rule that sets the style of text in a widget.

## Syntax

--8<-- "docs/styles/snippets/text_style_syntax.md"

## Examples

!!! note

    The `text-style` CSS rule and the text style unit are closely related but they are not the same thing.
    Here, we show examples of the text style unit, which are relevant for [all CSS rules](#used-by) that use the text style unit.

```css
Widget {
    text-style: bold;
    text-style: italic;
    text-style: reverse;
    text-style: underline;
    text-style: strike;

    /* When the unit expected is a style, you can specify multiple values */
    text-style: strike bold italic reverse;
    text-style: bold underline italic;
}
```

```py
widget.styles.text_style = "bold"
widget.styles.text_style = "italic"
widget.styles.text_style = "reverse"
widget.styles.text_style = "underline"
widget.styles.text_style = "strike"

# Multiple values can be specified
widget.styles.text_style = "strike bold italic reverse"
widget.styles.text_style = "bold underline italic"
```

## Used by

 - Links:
    - [`link-style`](../links/link_style.md)
    - [`link-hover-style`](../links/link_hover_style.md)
 - [`text-style`](../text_style.md)
