# Text-wrap

The `text-wrap` style set how Textual should wrap text.
The default value is "wrap" which will word-wrap text.
You can also set this style to "nowrap" which will disable wrapping entirely.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-wrap: <a href="../../css_types/text_wrap">&lt;text-wrap&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


## Example

In the following example we have two pieces of text.

The first (top) text has the default value for `text-wrap` ("wrap") which will cause text to be word wrapped as normal.
The second has `text-wrap` set to "nowrap" which disables text wrapping and results in a single line.

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



## See also

 - [`text-overflow`](./text_overflow.md) to set what happens to text that overflows the available width.
 
