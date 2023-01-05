# &lt;text-style&gt;

The `<text-style>` CSS type represents styles that can be applied to text.

!!! warning

    Not to be confused with the [`text-style`](../styles/text_style.md) CSS rule that sets the style of text in a widget.

## Syntax

--8<-- "docs/snippets/type_syntax/text_style.md"

## Examples

### CSS

```sass
* {
    /* You can specify any value by itself. */
    rule: bold;
    rule: italic;
    rule: none;
    rule: reverse;
    rule: strike;
    rule: underline;

    /* You can also combine multiple values. */
    rule: strike bold italic reverse;
    rule: bold underline italic;
}
```

### Python

```py
# You can specify any value by itself
text_style = "bold"
text_style = "italic"
text_style = "none"
text_style = "reverse"
text_style = "strike"
text_style = "underline"

# You can also combine multiple values
text_style = "strike bold italic reverse"
text_style = "bold underline italic"
```
