# Link-style

The `link-style` sets the text style for the link text.

!!! note

    `link-style` only applies to "action links" as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

```sass
link-style: <TEXT STYLE>;
```

--8<-- "docs/styles/snippets/text_style_syntax.md"

## Example

The example below shows some links with different styles applied to their text.
It also shows that `link-style` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_style.py" lines=6}
    ```

=== "link_style.py"

    ```py hl_lines="8-9 12-13 16-17 20-21"
    --8<-- "docs/examples/styles/link_style.py"
    ```

    1. This label has an hyperlink so it won't be affected by the `link-style` rule.
    2. This label has an "action link" that can be styled with `link-style`.
    3. This label has an "action link" that can be styled with `link-style`.
    4. This label has an "action link" that can be styled with `link-style`.

=== "link_style.css"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_style.css"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-style: bold;
link-style: bold italic reverse;
```

## Python

```py
widget.styles.link_style = "bold"
widget.styles.link_style = "bold italic reverse"
```
