# &lt;color&gt;

The `<color>` CSS type represents a color.

!!! warning

    Not to be confused with the [`color`](../styles/color.md) CSS rule to set text color.

## Syntax

The legal values for a [`<color>`](/css_types/color) depend on the [class `Color`][textual.color.Color] and include:

 - a recognised [named color](../../api/color#textual.color--named-colors) (e.g., `red`);
 - a hexadecimal number representing the RGB values of the color (e.g., `#F35573`);
 - a color description in the RGB system (e.g., `rgb(23,78,200)`);
 - a color description in the HSL system (e.g., `hsl(290,70%,80%)`); and

For more details about the exact formats accepted, see [the class method `Color.parse`][textual.color.Color.parse].
[Textual's default themes](../../guide/design#theme-reference) also provide many CSS variables with colors.

## Examples

### CSS

```sass
Header {
    background: red;           /* Color name */
}

.accent {
    color: $accent;            /* Textual variable */
}

#footer {
    tint: hsl(300, 20%, 70%);  /* HSL description */
}
```

### Python

In Python, rules that expect a `<color>` can also accept an instance of the type [`Color`][textual.color.Color].

```py
# Mimicking the CSS syntax
widget.styles.background = "red"           # Color name
widget.styles.color = "$accent"            # Textual variable
widget.styles.tint = "hsl(300, 20%, 70%)"  # HSL description

from textual.color import Color
# Using a Color object directly...
color = Color(16, 200, 45)
# ... which can also parse the CSS syntax
color = Color.parse("#A8F")
```
