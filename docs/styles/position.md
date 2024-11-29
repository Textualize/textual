
# Position

The `position` style modifies what [`offset`](./offset.md) is applied to.
The default for `position` is `"relative"`, which means the offset is applied to the normal position of the widget.
In other words, if `offset` is (1, 1), then the widget will be moved 1 cell and 1 line down from its usual position.

The alternative value of `position` is `"absolute"`.
With absolute positioning, the offset is relative to the origin (i.e. the top left of the container).
So a widget with offset (1, 1) and absolute positioning will be 1 cell and 1 line down from the top left corner.

!!! note

    Absolute positioning takes precedence over the parent's alignment rule.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
position: <a href="../../css_types/position">&lt;position&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


## Examples


Two labels, the first is absolute positioned and is displayed relative to the top left of the screen.
The second label is relative and is displayed offset from the center.

=== "Output"

    ```{.textual path="docs/examples/styles/position.py"}
    ```

=== "position.py"

    ```py
    --8<-- "docs/examples/styles/position.py"
    ```

=== "position.tcss"

    ```css
    --8<-- "docs/examples/styles/position.tcss"
    ```




## CSS

```css
position: relative;
position: absolute;
```

## Python

```py
widget.styles.position = "relative"
widget.styles.position = "absolute"
```
