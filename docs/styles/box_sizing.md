# Box-sizing

The `box-sizing` style determines how the width and height of a widget are calculated.

## Syntax

```
box-sizing: border-box | content-box;
```

### Values

| Value                  | Description                                                                                                                                                             |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `border-box` (default) | Padding and border are included in the width and height. If you add padding and/or border the widget will not change in size, but you will have less space for content. |
| `content-box`          | Padding and border will increase the size of the widget, leaving the content area unaffected.                                                                           |

## Example

Both widgets in this example have the same height (5).
The top widget has `box-sizing: border-box` which means that padding and border reduce the space for content.
The bottom widget has `box-sizing: content-box` which increases the size of the widget to compensate for padding and border.

=== "Output"

    ```{.textual path="docs/examples/styles/box_sizing.py"}
    ```

=== "box_sizing.py"

    ```python
    --8<-- "docs/examples/styles/box_sizing.py"
    ```

=== "box_sizing.tcss"

    ```css hl_lines="2 6"
    --8<-- "docs/examples/styles/box_sizing.tcss"
    ```

## CSS

```css
/* Set box sizing to border-box (default) */
box-sizing: border-box;

/* Set box sizing to content-box */
box-sizing: content-box;
```

## Python

```python
# Set box sizing to border-box (default)
widget.box_sizing = "border-box"

# Set box sizing to content-box
widget.box_sizing = "content-box"
```

## See also

 - [`border`](./border.md) to add a border around a widget.
 - [`padding`](./padding.md) to add spacing around the content of a widget.
