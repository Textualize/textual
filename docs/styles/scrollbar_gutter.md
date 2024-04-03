# Scrollbar-gutter

The `scrollbar-gutter` style allows reserving space for a vertical scrollbar.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
scrollbar-gutter: auto | stable;
--8<-- "docs/snippets/syntax_block_end.md"

### Values

| Value            | Description                                    |
|------------------|------------------------------------------------|
| `auto` (default) | No space is reserved for a vertical scrollbar. |
| `stable`         | Space is reserved for a vertical scrollbar.    |

Setting the value to `stable` prevents unwanted layout changes when the scrollbar becomes visible, whereas the default value of `auto` means that the layout of your application is recomputed when a vertical scrollbar becomes needed.

## Example

In the example below, notice the gap reserved for the scrollbar on the right side of the
terminal window.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_gutter.py"}
    ```

=== "scrollbar_gutter.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_gutter.py"
    ```

=== "scrollbar_gutter.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/scrollbar_gutter.tcss"
    ```

## CSS

```css
scrollbar-gutter: auto;    /* Don't reserve space for a vertical scrollbar. */
scrollbar-gutter: stable;  /* Reserve space for a vertical scrollbar. */
```

## Python

```python
self.styles.scrollbar_gutter = "auto"    # Don't reserve space for a vertical scrollbar.
self.styles.scrollbar_gutter = "stable"  # Reserve space for a vertical scrollbar.
```
