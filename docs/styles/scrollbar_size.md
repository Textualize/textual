# Scrollbar-size

The `scrollbar-size` rule changes the size of the scrollbars. It takes 2 integers for horizontal and vertical scrollbar size respectively.

The scrollbar dimensions may also be set individually with `scrollbar-size-horizontal` and `scrollbar-size-vertical`.

## Syntax

```
scrollbar-size: <INTEGER> <INTEGER>;
```

## Example

In this example we modify the size of the widget's scrollbar to be _much_ larger than usual.

=== "scrollbar_size.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_size.py"
    ```

=== "scrollbar_size.css"

    ```css
    --8<-- "docs/examples/styles/scrollbar_size.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_size.py"}
    ```

## CSS

```sass
/* Set horizontal scrollbar to 10, and vertical scrollbar to 4 */
Widget {
    scrollbar-size: 10 4;
}
```

## Python

```python
# Set horizontal scrollbar to 10, and vertical scrollbar to 4
widget.styles.horizontal_scrollbar = 10
widget.styles.vertical_scrollbar = 10
```
