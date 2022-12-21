# Color unit

Color units are used with rules that need to set the color of a part of a widget.
For example, the `background` rule sets the color of the background of a widget.

!!! warning

    Not to be confused with the [`color`](../color.md) CSS rule to set text color.

## Syntax

--8<-- "docs/styles/snippets/color_css_syntax.md"

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

## Used by

 - [`background`](../background.md)
 - [`border`](../border.md)
 - [`color`](../color.md)
 - Links:
    - [`link-color`](../links/link_color.md)
    - [`link-background`](../links/link_background.md)
    - [`link-hover-color`](../links/link_hover_color.md)
    - [`link-hover-background`](../links/link_hover_background.md)
 - [`outline`](../outline.md)
 - Scrollbars:
    - [`scrollbar-color`](../scrollbar_colors/scrollbar_color.md)
    - [`scrollbar-color-hover`](../scrollbar_colors/scrollbar_color_hover.md)
    - [`scrollbar-color-active`](../scrollbar_colors/scrollbar_color_active.md)
    - [`scrollbar-background`](../scrollbar_colors/scrollbar_background.md)
    - [`scrollbar-background-hover`](../scrollbar_colors/scrollbar_background_hover.md)
    - [`scrollbar-background-active`](../scrollbar_colors/scrollbar_background_active.md)
    - [`scrollbar-corner-color`](../scrollbar_colors/scrollbar_corner_color.md)
 - [`tint`](../tint.md)
