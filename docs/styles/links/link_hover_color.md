# Link-hover-color

The `link-hover-color` style sets the color of the link text when the mouse cursor is over the link.

!!! note

    `link-hover-color` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-hover-color: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-hover-color` accepts a [`<color>`](../../../css_types/color) (with an optional opacity level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the color of text enclosed in Textual action links when the mouse pointer is over it.

### Defaults

If not provided, a Textual action link will have `link-hover-color` set to `white`.

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

    ```sass hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_hover_color.css"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```sass
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

## See also

 - [`link-color`](./link_color.md) to set the color of link text.
 - [`link-hover-background](./link_hover_background.md) to set the background color of link text when the mouse pointer is over it.
 - [`link-hover-style](./link_hover_style.md) to set the style of link text when the mouse pointer is over it.
