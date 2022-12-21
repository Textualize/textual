# Links

Textual supports the concept of inline "links" embedded in text which trigger an action when pressed.

!!! note

    These CSS rules only target Textual action links. Internet hyperlinks are not affected by these CSS rules.

There are a number of styles which influence the appearance of these links within a widget.

| Property                                              | Description                                                       |
|-------------------------------------------------------|-------------------------------------------------------------------|
| [`link-color`](./link_color.md)                       | The color of the link text.                                       |
| [`link-background`](./link_background.md)             | The background color of the link text.                            |
| [`link-style`](./link_style.md)                       | The style of the link text (e.g. underline).                      |
| [`link-hover-color`](./link_hover_color.md)           | The color of the link text when the cursor is over it.            |
| [`link-hover-background`](./link_hover_background.md) | The background color of the link text when the cursor is over it. |
| [`link-hover-style`](./link_hover_style.md)           | The style of the link text when the cursor is over it.            |

## Syntax

```scss
link-color: <COLOR> [<PERCENTAGE>];
link-background: <COLOR> [<PERCENTAGE>];
link-style: <TEXT STYLE>;
link-hover-color: <COLOR> [<PERCENTAGE>];
link-hover-background: <COLOR> [<PERCENTAGE>];
link-hover-style: <TEXT STYLE>;
```

--8<-- "docs/snippets/color_css_syntax.md"

--8<-- "docs/snippets/text_style_syntax.md"

## Example

In the example below, the first label illustrates default link styling.
The second label uses CSS to customize the link color, background, and style.

=== "Output"

    ```{.textual path="docs/examples/styles/links.py"}
    ```

=== "links.py"

    ```python
    --8<-- "docs/examples/styles/links.py"
    ```

=== "links.css"

    ```sass
    --8<-- "docs/examples/styles/links.css"
    ```

## Additional Notes

* Inline links are not widgets, and thus cannot be focused.

## See Also

* An [introduction to links](../../guide/actions.md#links) in the Actions guide.

[//]: # (TODO: Links are documented twice in the guide, and one will likely be removed. Check the link above still works after that.)
