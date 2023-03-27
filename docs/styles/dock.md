# Dock

The `dock` style is used to fix a widget to the edge of a container (which may be the entire terminal window).

## Syntax

```
dock: bottom | left | right | top;
```

The option chosen determines the edge to which the widget is docked.

## Examples

### Basic usage

The example below shows a `left` docked sidebar.
Notice that even though the content is scrolled, the sidebar remains fixed.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout1_sidebar.py" press="pagedown,down,down"}
    ```

=== "dock_layout1_sidebar.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.py"
    ```

=== "dock_layout1_sidebar.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.css"
    ```

### Advanced usage

The second example shows how one can use full-width or full-height containers to dock labels to the edges of a larger container.
The labels will remain in that position (docked) even if the container they are in scrolls horizontally and/or vertically.

=== "Output"

    ```{.textual path="docs/examples/styles/dock_all.py"}
    ```

=== "dock_all.py"

    ```py
    --8<-- "docs/examples/styles/dock_all.py"
    ```

=== "dock_all.css"

    ```sass hl_lines="2-5 8-11 14-17 20-23"
    --8<-- "docs/examples/styles/dock_all.css"
    ```

## CSS

```sass
dock: bottom;  /* Docks on the bottom edge of the parent container. */
dock: left;    /* Docks on the   left edge of the parent container. */
dock: right;   /* Docks on the  right edge of the parent container. */
dock: top;     /* Docks on the    top edge of the parent container. */
```

## Python

```python
widget.styles.dock = "bottom"  # Dock bottom.
widget.styles.dock = "left"    # Dock   left.
widget.styles.dock = "right"   # Dock  right.
widget.styles.dock = "top"     # Dock    top.
```

## See also

 - The [layout guide](../guide/layout.md#docking) section on docking.
