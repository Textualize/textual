# Link-background-hover

The `link-background-hover` style sets the background color of the link when the mouse cursor is over the link.

!!! note

    `link-background-hover` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-background-hover: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-background-hover` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of text enclosed in Textual action links when the mouse pointer is over it.

### Defaults

If not provided, a Textual action link will have `link-background-hover` set to `$accent`.

## Example

The example below shows some links that have their background color changed when the mouse moves over it and it shows that there is a default color for `link-background-hover`.

It also shows that `link-background-hover` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_background_hover_demo.gif)

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_background_hover.py`.

=== "link_background_hover.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_background_hover.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-background-hover` rule.
    2. This label has an "action link" that can be styled with `link-background-hover`.
    3. This label has an "action link" that can be styled with `link-background-hover`.
    4. This label has an "action link" that can be styled with `link-background-hover`.

=== "link_background_hover.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_background_hover.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different background color, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```css
link-background-hover: red 70%;
link-background-hover: $accent;
```

## Python

```py
widget.styles.link_background_hover = "red 70%"
widget.styles.link_background_hover = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_background_hover = Color(100, 30, 173)
```

## See also

 - [`link-background`](./link_background.md) to set the background color of link text.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
 - [`link-style-hover`](./link_style_hover.md) to set the style of link text when the mouse pointer is over it.
