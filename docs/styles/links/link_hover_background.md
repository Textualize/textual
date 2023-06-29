# Link-hover-background

The `link-hover-background` style sets the background color of the link when the mouse cursor is over the link.

!!! note

    `link-hover-background` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-hover-background: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-hover-background` accepts a [`<color>`](../../../css_types/color) (with an optional opacity level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the background color of text enclosed in Textual action links when the mouse pointer is over it.

### Defaults

If not provided, a Textual action link will have `link-hover-background` set to `$accent`.

## Example

The example below shows some links that have their background colour changed when the mouse moves over it and it shows that there is a default color for `link-hover-background`.

It also shows that `link-hover-background` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_hover_background_demo.gif)

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_hover_background.py`.

=== "link_hover_background.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_hover_background.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-hover-background` rule.
    2. This label has an "action link" that can be styled with `link-hover-background`.
    3. This label has an "action link" that can be styled with `link-hover-background`.
    4. This label has an "action link" that can be styled with `link-hover-background`.

=== "link_hover_background.css"

    ```sass hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_hover_background.css"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different background color, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```sass
link-hover-background: red 70%;
link-hover-background: $accent;
```

## Python

```py
widget.styles.link_hover_background = "red 70%"
widget.styles.link_hover_background = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_hover_background = Color(100, 30, 173)
```

## See also

 - [`link-background`](./link_background.md) to set the background color of link text.
 - [`link-hover-color](./link_hover_color.md) to set the color of link text when the mouse pointer is over it.
 - [`link-hover-style](./link_hover_style.md) to set the style of link text when the mouse pointer is over it.
