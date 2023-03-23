# Layer

The `layer` style defines the layer a widget belongs to.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layer: <a href="../../css_types/name">&lt;name&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `layer` style accepts a [`<name>`](../../css_types/name) that defines the layer this widget belongs to.
This [`<name>`](../../css_types/name) must correspond to a [`<name>`](../../css_types/name) that has been defined in a [`layers`](./layers) style by an ancestor of this widget.

More information on layers can be found in the [guide](../guide/layout.md#layers).

!!! warning

    Using a `<name>` that hasn't been defined in a [`layers`](./layers.md) declaration of an ancestor of this widget has no effect.

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

    ```sass hl_lines="3 14 19"
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
widget.styles.layer = "below"
```

## See also

 - The [layout guide](../guide/layout.md#layers) section on layers.
 - [`layers`](./layers.md) to define an ordered set of layers.
