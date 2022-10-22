# Scrollbar colors

There are a number of rules to set the colors used in Textual scrollbars.
You won't typically need to do this, as the default themes have carefully chosen colors, but you can if you want to.

| Rule                          | Color                                                   |
|-------------------------------|---------------------------------------------------------|
| `scrollbar-color`             | Scrollbar "thumb" (movable part)                        |
| `scrollbar-color-hover`       | Scrollbar thumb when the mouse is hovering over it      |
| `scrollbar-color-active`      | Scrollbar thumb when it is active (being dragged)       |
| `scrollbar-background`        | Scrollbar background                                    |
| `scrollbar-background-hover`  | Scrollbar background when the mouse is hovering over it |
| `scrollbar-background-active` | Scrollbar background when the thumb is being dragged    |
| `scrollbar-corner-color`      | The gap between the horizontal and vertical scrollbars  |

## Syntax

```
scrollbar-color: <COLOR>;
scrollbar-color-hover: <COLOR>;
scrollbar-color-active: <COLOR>;
scrollbar-background: <COLOR>;
scrollbar-background-hover: <COLOR>;
scrollbar-background-active: <COLOR>;
scrollbar-corner-color: <COLOR>;
```

## Example

In this example we have two panels with different scrollbar colors set for each.

=== "scrollbars.py"

    ```python
    --8<-- "docs/examples/styles/scrollbars.py"
    ```

=== "scrollbars.css"

    ```css
    --8<-- "docs/examples/styles/scrollbars.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbars.py"}
    ```

## CSS

```sass
/* Set widget scrollbar color to yellow */
Widget {
    scrollbar-color: yellow;
}
```

## Python

```python
# Set the scrollbar color to yellow
widget.styles.scrollbar_color = "yellow"
```
