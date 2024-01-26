# Keyline

The `keyline` style is applied to a container and will draw lines around child widgets.

A keyline is superficially like the [border](./border.md) rule, but rather than draw inside the widget, a keyline is drawn outside of the widget's border. Additionally, unlike `border`, keylines can overlap and cross to create dividing lines between widgets.

Because keylines are drawn in the widget's margin, you will need to apply the [margin](./margin.md) or [grid-gutter](./grid/grid_gutter.md) rule to see the effect.


## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
keyline: [<a href="../../css_types/keyline">&lt;keyline&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"


## Examples

### Horizontal Keyline

The following examples shows a simple horizontal layout with a thin keyline.

=== "Output"

    ```{.textual path="docs/examples/styles/keyline_horizontal.py"}
    ```

=== "keyline.py"

    ```python
    --8<-- "docs/examples/styles/keyline_horizontal.py"
    ```

=== "keyline.tcss"

    ```css
    --8<-- "docs/examples/styles/keyline_horizontal.tcss"
    ```



### Grid keyline

The following examples shows a grid layout with a *heavy* keyline.

=== "Output"

    ```{.textual path="docs/examples/styles/keyline.py"}
    ```

=== "keyline.py"

    ```python
    --8<-- "docs/examples/styles/keyline.py"
    ```

=== "keyline.tcss"

    ```css 
    --8<-- "docs/examples/styles/keyline.tcss"
    ```


## CSS

```css
/* Set a thin green keyline */
/* Note: Must be set on a container or a widget with a layout. */
keyline: thin green;
```

## Python

You can set a keyline in Python with a tuple of type and color:

```python
widget.styles.keyline = ("thin", "green")
```


## See also

 - [`border`](./border.md) to add a border around a widget.
