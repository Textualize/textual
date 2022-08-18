# Scrollbar gutter

The `scrollbar-gutter` rule allows authors to reserve space for the vertical scrollbar.

Setting the value to `stable` prevents unwanted layout changes when the scrollbar becomes visible.

## Example

In the example below, notice the gap reserved for the scrollbar on the right side of the
terminal window.

=== "scrollbar_gutter.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_gutter.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_gutter.py"}
    ```

## CSS

```sass
/* Reserve space for vertical scrollbar */
scrollbar-gutter: stable;
```

## Python

```python
self.styles.scrollbar_gutter = "stable"
```
