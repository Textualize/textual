# Scrollbar-visibility

The `scrollbar-visibility` is used to show or hide scrollbars.

If scrollbars are hidden, the user may still scroll the container using the mouse wheel / keys / and gestures, but
there will be no scrollbars shown.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
scrollbar-visibility: hidden | visible;
--8<-- "docs/snippets/syntax_block_end.md"


### Values

| Value               | Description                                          |
| ------------------- | ---------------------------------------------------- |
| `hidden`            | The widget's scrollbars will be hidden.              |
| `visible` (default) | The widget's scrollbars will be displayed as normal. |


## Examples

The following example contains two containers with the same text.
The container on the right has its scrollbar hidden.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_visibility.py"}
    ```

=== "scrollbar_visibility.py"

    ```py
    --8<-- "docs/examples/styles/scrollbar_visibility.py"
    ```

=== "scrollbar_visibility.tcss"

    ```css
    --8<-- "docs/examples/styles/scrollbar_visibility.tcss"
    ```


## CSS

```css
scrollbar-visibility: visible;
scrollbar-visibility: hidden;
```



## Python

```py
widget.styles.scrollbar_visibility = "visible";
widget.styles.scrollbar_visibility = "hidden";
```
