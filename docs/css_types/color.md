# &lt;color&gt;

The `<color>` CSS type represents a color.

!!! warning

    Not to be confused with the [`color`](../styles/color.md) CSS rule to set text color.

## Syntax

--8<-- "docs/snippets/type_syntax/color.md"

## Examples

### CSS

```sass
* {
    rule: red;               /* color name                     */
    rule: #A8F;              /* 3-digit hex RGB                */
    rule: #FF00FFDD;         /* 6-digit hex RGB + transparency */
    rule: rgb(15,200,73);    /* RGB description                */
    rule: hsl(300,20%,70%);  /* HSL description                */
    rule: $accent;           /* Textual variable               */
}
```

### Python

```py
# Mimicking the CSS syntax
color = "red"
color = "#A8F"
color = "#FF00FFDD"
color = "rgb(15,200,73)"
color = "hsl(300,20%,70%)"
color = "$accent"

# Using a Color object directly...
color = Color(16, 200, 45)
# ... which can also parse the CSS syntax
color = Color.parse("#A8F")
```
