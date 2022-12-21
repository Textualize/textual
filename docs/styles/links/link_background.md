# Link-background

The `link-background` sets the background color of the link.

!!! note

    `link-background` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

```sass
link-background: <COLOR> <PERCENTAGE>;
```

--8<-- "docs/snippets/color_css_syntax.md"

--8<-- "docs/snippets/percentage_syntax.md"

## Example

The example below shows some links with their background color changed.
It also shows that `link-background` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_background.py" lines=6}
    ```

=== "link_background.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_background.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-background` rule.
    2. This label has an "action link" that can be styled with `link-background`.
    3. This label has an "action link" that can be styled with `link-background`.
    4. This label has an "action link" that can be styled with `link-background`.

=== "link_background.css"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_background.css"
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
