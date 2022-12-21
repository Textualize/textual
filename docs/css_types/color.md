# Color unit

Color units are used with rules that need to set the color of a part of a widget.
For example, the `background` rule sets the color of the background of a widget.

!!! warning

    Not to be confused with the [`color`](../color.md) CSS rule to set text color.

## Syntax

--8<-- "docs/snippets/color_css_syntax.md"

## Examples

```css
Widget {
    background: red;               /* color name                     */
    background: #A8F;              /* 3-digit hex RGB                */
    background: #FF00FFDD;         /* 6-digit hex RGB + transparency */
    background: rgb(15,200,73);    /* RGB description                */
    background: hsl(300,20%,70%);  /* HSL description                */
    background: $accent;           /* Textual variable               */
}
```

```py
# Mimicking the CSS syntax
widget.styles.background = "red"
widget.styles.background = "#A8F"
widget.styles.background = "#FF00FFDD"
widget.styles.background = "rgb(15,200,73)"
widget.styles.background = "hsl(300,20%,70%)"
widget.styles.background = "$accent"

# Using a Color object directly...
widget.styles.background = Color(16, 200, 45)
# ... which can also parse the CSS syntax
widget.styles.background = Color.parse("#A8F")
```
