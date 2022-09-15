# Layers

The `layers` property allows you to define an ordered set of layers.
These `layers` can later be referenced using the `layer` property.
Layers control the order in which widgets are painted on screen.
More information on layers can be found in the [guide](../guide/layout.md#layers).

## Syntax

```
layers: <STRING> ...;
```

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

=== "layers.css"

    ```sass hl_lines="3 15 19"
    --8<-- "docs/examples/guide/layout/layers.css"
    ```

## CSS

```sass
/* Bottom layer is called 'below', layer above it is called 'above' */
layers: below above;
```

## Python

```python
# Bottom layer is called 'below', layer above it is called 'above'
widget.layers = ("below", "above")
```
