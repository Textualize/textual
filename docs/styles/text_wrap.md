<!-- This is the template file for a CSS style reference page. -->

# Text-wrap

The `text-wrap` style set how Textual should wrap text.
The default value is `wrap` which will word-wrap text.
You can also set this style to `nowrap` which will disable wrapping entirely.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"

Formal syntax description of the style
style-name: <a href="../../css_types/text_wrap">&lt;text_wrap&gt;</a>;

--8<-- "docs/snippets/syntax_block_end.md"


## Examples

In the following example we have to pieces of text.
The first (top) text has the default `text-wrap` setting which will word wrap.
The second has `text-wrap` set to `nowrap`, which disables text wrapping, and results in a single line.

=== "Output"

    ```{.textual path="docs/examples/styles/text_wrap.py"}
    ```

=== "text_wrap.py"

    ```py
    --8<-- "docs/examples/styles/text_wrap.py"
    ```

=== "text_wrap.tcss"

    ```css
    --8<-- "docs/examples/styles/text_wrap.tcss"
    ```
-->



## CSS


```css
text-wrap: wrap;
text-wrap: nowrap;
```


## Python


```py
widget.styles.text_wrap = "wrap"
widget.styles.text_wrap = "nowrap"

```
