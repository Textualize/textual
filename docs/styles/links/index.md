# Links

Textual supports the concept of inline "links" embedded in text which trigger an action when pressed.
There are a number of styles which influence the appearance of these links within a widget.

!!! note

    These CSS rules only target Textual action links. Internet hyperlinks are not affected by these styles.

| Property                                              | Description                                                       |
|-------------------------------------------------------|-------------------------------------------------------------------|
| [`link-background`](./link_background.md)             | The background color of the link text.                            |
| [`link-background-hover`](./link_background_hover.md) | The background color of the link text when the cursor is over it. |
| [`link-color`](./link_color.md)                       | The color of the link text.                                       |
| [`link-color-hover`](./link_color_hover.md)           | The color of the link text when the cursor is over it.            |
| [`link-style`](./link_style.md)                       | The style of the link text (e.g. underline).                      |
| [`link-style-hover`](./link_style_hover.md)           | The style of the link text when the cursor is over it.            |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./link_background">link-background</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_color">link-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_style">link-style</a>: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;

<a href="./link_background_hover">link-background-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_color_hover">link-color-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_style_hover">link-style-hover</a>: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

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

=== "links.tcss"

    ```css
    --8<-- "docs/examples/styles/links.tcss"
    ```

## Additional Notes

* Inline links are not widgets, and thus cannot be focused.

## See Also

* An [introduction to links](../../guide/actions.md#links) in the Actions guide.

[//]: # (TODO: Links are documented twice in the guide, and one will likely be removed. Check the link above still works after that.)
