# Visibility

The `visibility` style determines whether a widget is visible or not.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
visibility: hidden | visible;
--8<-- "docs/snippets/syntax_block_end.md"

`visibility` takes one of two values to set the visibility of a widget.

### Values

| Value               | Description                             |
|---------------------|-----------------------------------------|
| `hidden`            | The widget will be invisible.           |
| `visible` (default) | The widget will be displayed as normal. |

### Visibility inheritance

!!! note

    Children of an invisible container _can_ be visible.

By default, children inherit the visibility of their parents.
So, if a container is set to be invisible, its children widgets will also be invisible by default.
However, those widgets can be made visible if their visibility is explicitly set to `visibility: visible`.
This is shown in the second example below.

## Examples

### Basic usage

Note that the second widget is hidden while leaving a space where it would have been rendered.

=== "Output"

    ```{.textual path="docs/examples/styles/visibility.py"}
    ```

=== "visibility.py"

    ```python
    --8<-- "docs/examples/styles/visibility.py"
    ```

=== "visibility.css"

    ```sass hl_lines="14"
    --8<-- "docs/examples/styles/visibility.css"
    ```

### Overriding container visibility

The next example shows the interaction of the `visibility` style with invisible containers that have visible children.
The app below has three rows with a `Horizontal` container per row and three placeholders per row.
The containers all have a white background, and then:

 - the top container is visible by default (we can see the white background around the placeholders);
 - the middle container is invisible and the children placeholders inherited that setting;
 - the bottom container is invisible _but_ the children placeholders are visible because they were set to be visible.

=== "Output"

    ```{.textual path="docs/examples/styles/visibility_containers.py"}
    ```

=== "visibility_containers.py"

    ```python
    --8<-- "docs/examples/styles/visibility_containers.py"
    ```

=== "visibility_containers.css"

    ```sass hl_lines="2-3 6 8-10 12-14 16-18"
    --8<-- "docs/examples/styles/visibility_containers.css"
    ```

    1. The padding and the white background let us know when the `Horizontal` is visible.
    2. The top `Horizontal` is visible by default, and so are its children.
    3. The middle `Horizontal` is made invisible and its children will inherit that setting.
    4. The bottom `Horizontal` is made invisible...
    5. ... but its children override that setting and become visible.

## CSS

```sass
/* Widget is invisible */
visibility: hidden;

/* Widget is visible */
visibility: visible;
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

## See also

 - [`display`](./display.md) to specify whether a widget is displayed or not.
