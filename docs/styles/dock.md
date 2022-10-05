# Dock

The `dock` property is used to fix a widget to the edge of a container (which may be the entire terminal window).

## Syntax

```
dock: top|right|bottom|left;
```

## Example

The example below shows a `left` docked sidebar.
Notice that even though the content is scrolled, the sidebar remains fixed.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout1_sidebar.py" press="pagedown,down,down,_,_,_,_,_"}
    ```

=== "dock_layout1_sidebar.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.py"
    ```

=== "dock_layout1_sidebar.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.css"
    ```

## CSS

```sass
/* Dock the widget on the left edge of its parent container */
dock: left;
```

## Python

```python
# Dock the widget on the left edge of its parent container
widget.styles.dock = "left"
```
