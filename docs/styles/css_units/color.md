# Color unit

!!! warning

    Not to be confused with the [`color`](../color.md) CSS rule to set text color.

## Syntax

--8<-- "../snippets/color_css_syntax.md"

## Examples

```css
Widget {
    color: red;
    color: #A8F;
    color: #FF00FFDD;
    color: rgb(15,200,73);
    color: hsl(300,20,70);
    color: $accent;
}
```

```py
# Mimicking the CSS syntax
widget.styles.color = "red"
widget.styles.color = "#A8F"
widget.styles.color = "#FF00FFDD"
widget.styles.color = "rgb(15,200,73)"
widget.styles.color = "hsl(300,20,70)"
widget.styles.color = "$accent"

# Using a Color object directly...
widget.styles.color = Color(16, 200, 45)
# ... which can parse the CSS syntax
widget.styles.color = Color.parse("#A8F")
```

## Used by

 - [`background`](../background.md)
 - [`border`](../border.md)
 - [`color`](../color.md)
