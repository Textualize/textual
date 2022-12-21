# Link-hover-color

The `link-hover-color` sets the color of the link text when the mouse cursor is over the link.

!!! note

    `link-hover-color` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

```sass
link-hover-color: <COLOR> <PERCENTAGE>;
```

--8<-- "docs/styles/snippets/color_css_syntax.md"

--8<-- "docs/styles/snippets/percentage_syntax.md"

## Example

The example below shows some links that have their colour changed when the mouse moves over it.
It also shows that `link-hover-color` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_hover_color_demo.gif)

    !!! note

        The background color also changes when the mouse moves over the links because that is the default behavior.
        That can be customised by setting [`link-hover-background`](./link_hover_background.md) but we haven't done so in this example.

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_hover_color.py`.

=== "link_hover_color.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_hover_color.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-hover-color` rule.
    2. This label has an "action link" that can be styled with `link-hover-color`.
    3. This label has an "action link" that can be styled with `link-hover-color`.
    4. This label has an "action link" that can be styled with `link-hover-color`.

=== "link_hover_color.css"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_hover_color.css"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-hover-color: red 70%;
link-hover-color: black;
```

## Python

```py
widget.styles.link_hover_color = "red 70%"
widget.styles.link_hover_color = "black"

# You can also use a `Color` object directly:
widget.styles.link_hover_color = Color(100, 30, 173)
```
