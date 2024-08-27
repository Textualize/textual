# Link-style-hover

The `link-style-hover` style sets the text style for the link text when the mouse cursor is over the link.

!!! note

    `link-style-hover` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-style-hover: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`link-style-hover` applies its [`<text-style>`](../../css_types/text_style.md) to the text of Textual action links when the mouse pointer is over them.

### Defaults

If not provided, a Textual action link will have `link-style-hover` set to `bold`.

## Example

The example below shows some links that have their color changed when the mouse moves over it.
It also shows that `link-style-hover` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_style_hover_demo.gif)

    !!! note

        The background color also changes when the mouse moves over the links because that is the default behavior.
        That can be customised by setting [`link-background-hover`](./link_background_hover.md) but we haven't done so in this example.

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_style_hover.py`.

=== "link_style_hover.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_style_hover.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-style-hover` rule.
    2. This label has an "action link" that can be styled with `link-style-hover`.
    3. This label has an "action link" that can be styled with `link-style-hover`.
    4. This label has an "action link" that can be styled with `link-style-hover`.

=== "link_style_hover.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_style_hover.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different text style, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```css
link-style-hover: bold;
link-style-hover: bold italic reverse;
```

## Python

```py
widget.styles.link_style_hover = "bold"
widget.styles.link_style_hover = "bold italic reverse"
```

## See also

 - [`link-background-hover`](./link_background_hover.md) to set the background color of link text when the mouse pointer is over it.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
 - [`link-style`](./link_style.md) to set the style of link text.
 - [`text-style`](../text_style.md) to set the style of text in a widget.
