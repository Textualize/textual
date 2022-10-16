# Display

The `display` property defines whether a widget is displayed or not.

## Syntax

```
display: [none|block];
```

### Values

| Value             | Description                                                               |
|-------------------|---------------------------------------------------------------------------|
| `block` (default) | Display the widget as normal                                              |
| `none`            | The widget not be displayed, and space will no longer be reserved for it. |

## Example

Note that the second widget is hidden by adding the `"remove"` class which sets the display style to None.

=== "display.py"

    ```python
    --8<-- "docs/examples/styles/display.py"
    ```

=== "display.css"

    ```css
    --8<-- "docs/examples/styles/display.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/display.py"}
    ```

## CSS

```sass
/* Widget is on screen */
display: block;

/* Widget is not on the screen */
display: none;
```

## Python

```python
# Hide the widget
self.styles.display = "none"

# Show the widget again
self.styles.display = "block"
```

There is also a shortcut to show / hide a widget. The `display` property on `Widget` may be set to `True` or `False` to show or hide the widget.

```python
# Hide the widget
widget.display = False

# Show the widget
widget.display = True
```
