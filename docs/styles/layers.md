# Layers

The `layers` style allows you to define an ordered set of layers.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layers: <a href="../../css_types/name">&lt;name&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `layers` style accepts one or more [`<name>`](../css_types/name.md) that define the layers that the widget is aware of, and the order in which they will be painted on the screen.

The values used here can later be referenced using the [`layer`](./layer.md) property.
The layers defined first in the list are drawn under the layers that are defined later in the list.

More information on layers can be found in the [guide](../guide/layout.md#layers).

## Example

In the example below, `#box1` is yielded before `#box2`.
However, since `#box1` is on the higher layer, it is drawn on top of `#box2`.

[//]: # (NOTE: the example below also appears in the guide and 'layer.md'.)

=== "Output"

    ```{.textual path="docs/examples/guide/layout/layers.py"}
    ```

=== "layers.py"

    ```python
    --8<-- "docs/examples/guide/layout/layers.py"
    ```

=== "layers.tcss"

    ```css hl_lines="3 14 19"
    --8<-- "docs/examples/guide/layout/layers.tcss"
    ```

## CSS

```css
/* Bottom layer is called 'below', layer above it is called 'above' */
layers: below above;
```

## Python

```python
# Bottom layer is called 'below', layer above it is called 'above'
widget.style.layers = ("below", "above")
```

## See also

 - The [layout guide](../guide/layout.md#layers) section on layers.
 - [`layer`](./layer.md) to set the layer a widget belongs to.
