# Border

The `border` rule enables the drawing of a box around a widget. A border is set with a border value (see below) followed by a color.

Borders may also be set individually for the four edges of a widget with the `border-top`, `border-right`, `border-bottom` and `border-left` rules.

## Syntax

```
border: [<COLOR>] [<BORDER VALUE>];
border-top: [<COLOR>] [<BORDER VALUE>];
border-right: [<COLOR>] [<BORDER VALUE>];
border-bottom: [<COLOR>] [<BORDER VALUE>];
border-left: [<COLOR>] [<BORDER VALUE>];
```

### Values

| Border value | Description                                             |
|--------------|---------------------------------------------------------|
| `"ascii"`    | A border with plus, hyphen, and vertical bar            |
| `"blank"`    | A blank border (reserves space for a border)            |
| `"dashed"`   | Dashed line border                                      |
| `"double"`   | Double lined border                                     |
| `"heavy"`    | Heavy border                                            |
| `"hidden"`   | Alias for "none"                                        |
| `"hkey"`     | Horizontal key-line border                              |
| `"inner"`    | Thick solid border                                      |
| `"none"`     | Disabled border                                         |
| `"outer"`    | Think solid border with additional space around content |
| `"round"`    | Rounded corners                                         |
| `"solid"`    | Solid border                                            |
| `"tall"`     | Solid border with extras space top and bottom           |
| `"vkey"`     | Vertical key-line border                                |
| `"wide"`     | Solid border with additional space left and right       |

For example, `heavy white` would display a heavy white line around a widget.

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types:

```
textual borders
```

## Example

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
