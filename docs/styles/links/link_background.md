# Link-background

The `link-background` style sets the background color of the link.

!!! note

    `link-background` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-background: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-background` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of text enclosed in Textual action links.

## Example

The example below shows some links with their background color changed.
It also shows that `link-background` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_background.py" lines=6}
    ```

=== "link_background.py"

    ```py hl_lines="10-11 14-15 18-20 22-23"
    --8<-- "docs/examples/styles/link_background.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-background` rule.
    2. This label has an "action link" that can be styled with `link-background`.
    3. This label has an "action link" that can be styled with `link-background`.
    4. This label has an "action link" that can be styled with `link-background`.

=== "link_background.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_background.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-background: red 70%;
link-background: $accent;
```

## Python

```py
widget.styles.link_background = "red 70%"
widget.styles.link_background = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_background = Color(100, 30, 173)
```

## See also

 - [`link-color`](./link_color.md) to set the color of link text.
 - [`link-background-hover`](./link_background_hover.md) to set the background color of link text when the mouse pointer is over it.
