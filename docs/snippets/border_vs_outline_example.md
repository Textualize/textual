The next example makes the difference between [`border`](../styles/border.md) and [`outline`](../styles/outline.md) clearer by having three labels side-by-side.
They contain the same text, have the same width and height, and are styled exactly the same up to their [`border`](../styles/border.md) and [`outline`](../styles/outline.md) styles.

This example also shows that a widget cannot contain both a `border` and an `outline`:

=== "Output"

    ```{.textual path="docs/examples/styles/outline_vs_border.py"}
    ```

=== "outline_vs_border.py"

    ```python
    --8<-- "docs/examples/styles/outline_vs_border.py"
    ```

=== "outline_vs_border.tcss"

    ```css hl_lines="5-7 9-11"
    --8<-- "docs/examples/styles/outline_vs_border.tcss"
    ```
