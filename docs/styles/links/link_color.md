# Link-color

The `link-color` sets the color of the link text.

!!! note

    `link-color` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

```sass
link-color: <COLOR> <PERCENTAGE>;
```

--8<-- "docs/snippets/type_syntax/color.md"

--8<-- "docs/snippets/type_syntax/percentage.md"

## Example

The example below shows some links with their color changed.
It also shows that `link-color` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_color.py" lines=6}
    ```

=== "link_color.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_color.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-color` rule.
    2. This label has an "action link" that can be styled with `link-color`.
    3. This label has an "action link" that can be styled with `link-color`.
    4. This label has an "action link" that can be styled with `link-color`.

=== "link_color.css"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_color.css"
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
