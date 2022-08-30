# Visibility

The `visibility` rule may be used to make a widget invisible while still reserving spacing for it.

## Syntax

```
visibility: [visible|hidden];
```

### Values

| Value               | Description                            |
|---------------------|----------------------------------------|
| `visible` (default) | The widget will be displayed as normal |
| `hidden`            | The widget will be invisible           |

## Example

Note that the second widget is hidden, while leaving a space where it would have been rendered.

=== "visibility.py"

    ```python
    --8<-- "docs/examples/styles/visibility.py"
    ```

=== "visibility.css"

    ```css
    --8<-- "docs/examples/styles/visibility.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/visibility.py"}
    ```

## CSS

```sass
/* Widget is on screen */
visibility: visible;

/* Widget is not on the screen */
visibility: hidden;
```

## Python

```python
# Widget is invisible
self.styles.visibility = "hidden"

# Widget is visible
self.styles.visibility = "visible"
```

There is also a shortcut to set a Widget's visibility. The `visible` property on `Widget` may be set to `True` or `False`.

```python
# Make a widget invisible
widget.visible = False

# Make the widget visible again
widget.visible = True
```
