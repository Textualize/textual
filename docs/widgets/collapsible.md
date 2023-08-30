# Collapsible

!!! tip "Added in version 0.36"

Widget that wraps its contents in a collapsible container.

- [ ] Focusable
- [x] Container


## Composing

There are two ways to wrap other widgets.
You can pass them as positional arguments to the [Collapsible][textual.widgets.Collapsible] constructor:

```python
def compose(self) -> ComposeResult:
    yield Collapsible(Label("Hello, world."))
```

Alternatively, you can compose other widgets under the context manager:

```python
def compose(self) -> ComposeResult:
    with Collapsible():
        yield Label("Hello, world.")
```

## Title

The default title "Toggle" of the `Collapsible` widget can be customized by specifying the parameter `title` of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="An interesting story."):
        yield Label("Interesting but verbose story.")
```

## Initial State

The initial state of the `Collapsible` widget can be customized via the parameter `collapsed` of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="Contents 1", collapsed=False):
        yield Label("Hello, world.")

    with Collapsible(title="Contents 2", collapsed=True):  # Default.
        yield Label("Hello, world.")
```

## Collapse/Expand Symbols

The symbols `►` and `▼` of the `Collapsible` widget can be customized by specifying the parameters `collapsed_symbol` and `expanded_symbol`, respectively, of the `Collapsible` constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(collapsed_symbol=">>>", expanded_symbol="v"):
        yield Label("Hello, world.")
```

=== "Output"

    ```{.textual path="tests/snapshot_tests/snapshot_apps/collapsible_custom_symbol.py"}
    ```

=== "collapsible_custom_symbol.py"

    ```python
    --8<-- "tests/snapshot_tests/snapshot_apps/collapsible_custom_symbol.py"
    ```

## Examples

### Basic example

The following example contains three `Collapsible`s in different states.

=== "All expanded"

    ```{.textual path="docs/examples/widgets/collapsible.py press="e"}
    ```

=== "All collapsed"

    ```{.textual path="docs/examples/widgets/collapsible.py press="c"}
    ```

=== "Mixed"

    ```{.textual path="docs/examples/widgets/collapsible.py"}
    ```

=== "collapsible.py"

    ```python
    --8<-- "docs/examples/widgets/collapsible.py"
    ```

### Setting Initial State

The example below shows nested `Collapsible` widgets and how to set their initial state.


=== "Output"

    ```{.textual path="tests/snapshot_tests/snapshot_apps/collapsible_nested.py"}
    ```

=== "collapsible_nested.py"

    ```python hl_lines="7"
    --8<-- "tests/snapshot_tests/snapshot_apps/collapsible_nested.py"
    ```

### Custom Symbols

The app below shows `Collapsible` widgets with custom expand/collapse symbols.


=== "Output"

    ```{.textual path="tests/snapshot_tests/snapshot_apps/collapsible_custom_symbol.py"}
    ```

=== "collapsible_custom_symbol.py"

    ```python
    --8<-- "tests/snapshot_tests/snapshot_apps/collapsible_custom_symbol.py"
    ```

## Reactive attributes

| Name        | Type   | Default | Description                                                    |
| ----------- | ------ | ------- | -------------------------------------------------------------- |
| `collapsed` | `bool` | `True`  | Controls the collapsed/expanded state of the widget. |

## Messages

- [Collapsible.Title.Toggle][textual.widgets.Collapsible.Title.Toggle]

<!--
## See also

TODO: Add Accordion widgets later
-->

---


::: textual.widgets.Collapsible
    options:
      heading_level: 2
