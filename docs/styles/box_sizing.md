# Box-sizing

The `box-sizing` rule impacts how `width` and `height` rules are translated in to screen dimensions, when combined with `padding` and `border`.

The default value is `border-box` which means that padding and border are included in the width and height. This setting means that if you add padding and/or border the widget will not change in size, but you will have less space for content.

You can set `box-sizing` to `content-box` which tells Textual that padding and border should increase the size of the widget, leaving the content area unaffected.

## Example

Both widgets in this example have the same height (5). The top widget has `box-sizing: border-box` which means that padding and border reduces the space for content. The bottom widget has `box-sizing: content-box` which increases the size of the widget to compensate for padding and border.

=== "box_sizing.py"

    ```python
    --8<-- "docs/examples/styles/box_sizing.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/box_sizing.py"}
    ```

## CSS

```sass
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
