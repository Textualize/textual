# Links

Textual supports the concept of inline "links" embedded in text which trigger an action when pressed.

There are a number of styles which influence the appearance of these links within a widget.

| Property                | Description                                                 |
|-------------------------|-------------------------------------------------------------|
| `link-color`            | The color of link text.                                     |
| `link-background`       | The background color of link text.                          |
| `link-style`            | The style of link text (e.g. underline).                    |
| `link-hover-color`      | The color of link text with the cursor above it.            |
| `link-hover-background` | The background color of link text with the cursor above it. |
| `link-hover-style`      | The style of link text with the cursor above it.            |

## Syntax

```scss
link-color: <COLOR>;
link-background: <COLOR>;
link-style: <TEXT STYLE> ...;
link-hover-color: <COLOR>;
link-hover-background: <COLOR>;
link-hover-style: <TEXT STYLE> ...;
```

## Example

In the example below, the first `Static` illustrates default link styling.
The second `Static` uses CSS to customize the link color, background, and style.

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

* An [introduction to links](../guide/actions.md#links) in the Actions guide.

[//]: # (TODO: Links are documented twice in the guide, and one will likely be removed. Check the link above still works after that.)
