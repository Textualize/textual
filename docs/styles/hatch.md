# Hatch

The `hatch` style fills a widget's background with a repeating character for a pleasing textured effect.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
hatch: (<a href="../../css_types/hatch">&lt;hatch&gt;</a> | CHARACTER) <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]
--8<-- "docs/snippets/syntax_block_end.md"

The hatch type can be specified with a constant, or a string. For example, `cross` for cross hatch, or `"T"` for a custom character.

The color can be any Textual color value.

An optional percentage can be used to set the opacity.

## Examples


An app to show a few hatch effects.

=== "Output"

    ```{.textual path="docs/examples/styles/hatch.py"}
    ```

=== "hatch.py"

    ```py
    --8<-- "docs/examples/styles/hatch.py"
    ```

=== "hatch.tcss"

    ```css
    --8<-- "docs/examples/styles/hatch.tcss"
    ```


## CSS

```css
/* Red cross hatch */
hatch: cross red;
/* Right diagonals, 50% transparent green. */
hatch: right green 50%;
/* T custom character in 80% blue. **/
hatch: "T" blue 80%;
```


## Python

```py
widget.styles.hatch = ("cross", "red")
widget.styles.hatch = ("right", "rgba(0,255,0,128)")
widget.styles.hatch = ("T", "blue")
```
