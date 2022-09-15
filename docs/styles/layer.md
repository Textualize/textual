# Layer

The `layer` property is used to assign widgets to a layer.
The value of the `layer` property must be the name of a layer defined using a `layers` declaration.
Layers control the order in which widgets are painted on screen.
More information on layers can be found in the [guide](../guide/layout.md#layers).

## Syntax

```
layer: <STRING>;
```

## Example

In the example below, `#box1` is yielded before `#box2`.
However, since `#box1` is on the higher layer, it is drawn on top of `#box2`.

[//]: # (NOTE: the example below also appears in the guide and 'layers.md'.)

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
/* Draw the widget on the layer called 'below' */
layer: below;
```

## Python

```python
# Draw the widget on the layer called 'below'
widget.layer = "below"
```
