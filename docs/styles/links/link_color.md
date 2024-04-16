# Link-color

The `link-color` style sets the color of the link text.

!!! note

    `link-color` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-color: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-color` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of text enclosed in Textual action links.

## Example

The example below shows some links with their color changed.
It also shows that `link-color` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_color.py" lines=6}
    ```

=== "link_color.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_color.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-color` rule.
    2. This label has an "action link" that can be styled with `link-color`.
    3. This label has an "action link" that can be styled with `link-color`.
    4. This label has an "action link" that can be styled with `link-color`.

=== "link_color.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_color.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-color: red 70%;
link-color: $accent;
```

## Python

```py
widget.styles.link_color = "red 70%"
widget.styles.link_color = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_color = Color(100, 30, 173)
```

## See also

 - [`link-background`](./link_background.md) to set the background color of link text.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
