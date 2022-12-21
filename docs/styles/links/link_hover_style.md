# Link-hover-style

The `link-hover-style` sets the text style for the link text when the mouse cursor is over the link.

!!! note

    `link-hover-style` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

```sass
link-hover-style: <COLOR> <PERCENTAGE>;
```

--8<-- "docs/styles/snippets/color_css_syntax.md"

--8<-- "docs/styles/snippets/percentage_syntax.md"

## Example

The example below shows some links that have their colour changed when the mouse moves over it.
It also shows that `link-hover-style` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_hover_style_demo.gif)

    !!! note

        The background color also changes when the mouse moves over the links because that is the default behavior.
        That can be customised by setting [`link-hover-background`](./link_hover_background.md) but we haven't done so in this example.

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_hover_style.py`.

=== "link_hover_style.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_hover_style.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-hover-style` rule.
    2. This label has an "action link" that can be styled with `link-hover-style`.
    3. This label has an "action link" that can be styled with `link-hover-style`.
    4. This label has an "action link" that can be styled with `link-hover-style`.

=== "link_hover_style.css"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_hover_style.css"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different text style, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```css
link-hover-style: bold;
link-hover-style: bold italic reverse;
```

## Python

```py
widget.styles.link_hover_style = "bold"
widget.styles.link_hover_style = "bold italic reverse"
```
