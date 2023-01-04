# Scrollbar-background

The `scrollbar-background` sets the background color of the scrollbar.
## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background">scrollbar-background</a>: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-background` accepts a [`<color>`](../../../css_types/color) (with an optional transparency level defined by a [`<percentage>`](../../../css_types/percentage)) that is used to define the background color of a scrollbar.

### Values

#### &lt;color&gt;

--8<-- "docs/snippets/type_syntax/color.md"

#### &lt;percentage&gt;

--8<-- "docs/snippets/type_syntax/percentage.md"

## Example

=== "Output"

    Awaits resolution of [issue 1479](https://github.com/textualize/textual/issues/1479).

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.css"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/scrollbars2.css"
    ```

## CSS

```css
scrollbar-backround: blue;
```

## Python

```py
widget.styles.scrollbar_background = "blue"
```
