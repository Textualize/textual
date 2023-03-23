# Scrollbar-size

The `scrollbar-size` style defines the width of the scrollbars.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
scrollbar-size: <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
              # horizontal vertical

scrollbar-size-horizontal: <a href="../../css_types/integer">&lt;integer&gt;</a>;
scrollbar-size-vertical: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `scrollbar-size` style takes two [`<integer>`](../css_types/integer.md) to set the horizontal and vertical scrollbar sizes, respectively.
This customisable size is the width of the scrollbar, given that its length will always be 100% of the container.

The scrollbar widths may also be set individually with `scrollbar-size-horizontal` and `scrollbar-size-vertical`.

## Examples

### Basic usage

In this example we modify the size of the widget's scrollbar to be _much_ larger than usual.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_size.py"}
    ```

=== "scrollbar_size.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_size.py"
    ```

=== "scrollbar_size.css"

    ```sass hl_lines="13"
    --8<-- "docs/examples/styles/scrollbar_size.css"
    ```

### Scrollbar sizes comparison

In the next example we show three containers with differently sized scrollbars.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_size2.py"}
    ```

=== "scrollbar_size2.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_size2.py"
    ```

=== "scrollbar_size2.css"

    ```sass hl_lines="6 11 16"
    --8<-- "docs/examples/styles/scrollbar_size2.css"
    ```

## CSS

```sass
/* Set horizontal scrollbar to 10, and vertical scrollbar to 4 */
scrollbar-size: 10 4;

/* Set horizontal scrollbar to 10 */
scrollbar-size-horizontal: 10;

/* Set vertical scrollbar to 4 */
scrollbar-size-vertical: 4;
```

## Python

The style `scrollbar-size` has no Python equivalent.
The scrollbar sizes must be set independently:

```py
# Set horizontal scrollbar to 10:
widget.styles.scrollbar_size_horizontal = 10
# Set vertical scrollbar to 4:
widget.styles.scrollbar_size_vertical = 4
```
