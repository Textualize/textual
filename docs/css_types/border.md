# &lt;border&gt;

The `<border>` CSS type represents a border style.

## Syntax

The [`<border>`](/css_types/border) type can take any of the following values:

| Border type | Description                                              |
|-------------|----------------------------------------------------------|
| `ascii`     | A border with plus, hyphen, and vertical bar characters. |
| `blank`     | A blank border (reserves space for a border).            |
| `dashed`    | Dashed line border.                                      |
| `double`    | Double lined border.                                     |
| `heavy`     | Heavy border.                                            |
| `hidden`    | Alias for "none".                                        |
| `hkey`      | Horizontal key-line border.                              |
| `inner`     | Thick solid border.                                      |
| `none`      | Disabled border.                                         |
| `outer`     | Solid border with additional space around content.       |
| `round`     | Rounded corners.                                         |
| `solid`     | Solid border.                                            |
| `tall`      | Solid border with additional space top and bottom.       |
| `thick`     | Border style that is consistently thick across edges.    |
| `vkey`      | Vertical key-line border.                                |
| `wide`      | Solid border with additional space left and right.       |

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively, when applied to the CSS rule [`border`](../styles/border.md):

```
textual borders
```

## Examples

### CSS

```sass
#container {
    border: heavy red;
}

#heading {
    border-bottom: solid blue;
}
```

### Python

```py
widget.styles.border = ("heavy", "red")
widget.styles.border_bottom = ("solid", "blue")
```
