# Outline

The `outline` rule enables the drawing of a box around a widget. Similar to `border`, but unlike border, outline will draw over the content area. This rule can be useful for emphasis if you want to display a outline for a brief time to draw the user's attention to it.

An outline is set with a border value (see below) followed by a color.

| Border value | Explanation                                             |
| ------------ | ------------------------------------------------------- |
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

For example `heavy white` would display a heavy white line around a widget.

Outlines may also be set individually with the `outline-top`, `outline-right`, `outline-bottom` and `outline-left` rules.

## Example

This examples shows a widget with an outline. Note how the outline occludes the text area.

=== "outline.py"

    ```python
    --8<-- "docs/examples/styles/outline.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/outline.py"}
    ```

## CSS

```sass
/* Set a heavy white outline */
outline: heavy white;

/* set a red outline on the left */
outline-left: outer red;
```

## Python

```python
# Set a heavy white outline
widget.outline = ("heavy", "white)

# Set a red outline on the left
widget.outline_left = ("outer", "red)
```
