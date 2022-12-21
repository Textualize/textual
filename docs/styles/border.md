# Border

The `border` rule enables the drawing of a box around a widget. A border is set with a border type (see below) and a color.

Borders may also be set individually for the four edges of a widget with the `border-top`, `border-right`, `border-bottom` and `border-left` rules.

## Syntax

```
border: [<BORDER TYPE>] [<COLOR>];
border-top: [<BORDER TYPE>] [<COLOR>];
border-right: [<BORDER TYPE>] [<COLOR>];
border-bottom: [<BORDER TYPE>] [<COLOR>];
border-left: [<BORDER TYPE>] [<COLOR>];
```

### Border types

| Border type | Description                                             |
|-------------|---------------------------------------------------------|
| `"ascii"`   | A border with plus, hyphen, and vertical bar characters |
| `"blank"`   | A blank border (reserves space for a border)            |
| `"dashed"`  | Dashed line border                                      |
| `"double"`  | Double lined border                                     |
| `"heavy"`   | Heavy border                                            |
| `"hidden"`  | Alias for "none"                                        |
| `"hkey"`    | Horizontal key-line border                              |
| `"inner"`   | Thick solid border                                      |
| `"none"`    | Disabled border                                         |
| `"outer"`   | Solid border with additional space around content       |
| `"round"`   | Rounded corners                                         |
| `"solid"`   | Solid border                                            |
| `"tall"`    | Solid border with extras space top and bottom           |
| `"vkey"`    | Vertical key-line border                                |
| `"wide"`    | Solid border with additional space left and right       |

For example, `heavy white` would display a heavy white line around a widget.

### Color syntax

--8<-- "docs/snippets/color_css_syntax.md"

### Multiple edge rules

If multiple border rules target the same edge, the last rule that targets a specific edge is the one that is applied to that edge.
For example, consider the CSS below:

```sass
Static {
    border-top: dashed red;
    border: solid green;  /* overrides the border-top rule above */
    /* Change the border but just for the bottom edge: */
    border-bottom: double blue;
}
```

The CSS snippet above will add a solid green border around `Static` widgets, except for the bottom edge, which will be double blue.

### Defaults

If a border color is specified but the border type is omitted, it defaults to solid.
If a border type is specified but the border color is omitted, it defaults to green (RGB color `"#00FF00"`).

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively:

```
textual borders
```

Alternatively, you can see the examples below.

## Examples

This examples shows three widgets with different border styles.

=== "border.py"

    ```python
    --8<-- "docs/examples/styles/border.py"
    ```

=== "border.css"

    ```css
    --8<-- "docs/examples/styles/border.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/border.py"}
    ```

The next example shows a grid with all the available border types.

=== "border_all.py"

    ```py
    --8<-- "docs/examples/styles/border_all.py"
    ```

=== "border_all.css"

    ```css
    --8<-- "docs/examples/styles/border_all.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/border_all.py"}
    ```

## CSS

```sass
/* Set a heavy white border */
border: heavy white;

/* set a red border on the left */
border-left: outer red;
```

## Python

```python
# Set a heavy white border
widget.border = ("heavy", "white")

# Set a red border on the left
widget.border_left = ("outer", "red")
```
