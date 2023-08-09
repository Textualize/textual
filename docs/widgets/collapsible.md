# Collapsible

!!! tip "Added in version 0.33"

Collapsible contents with title.

- [ ] Focusable
- [x] Container

This widget wraps other widgets as `Contents` and control the visibility.

## Composing

There are two ways to wrap other widgets.
You can pass them as positional arguments to the [Collapsible][textual.widgets.Collapsible] constructor:

```python
def compose(self) -> ComposeResult:
    yield Collapsible(Label("Verbose sentence to show by default."))

```

Alternatively you can compose other widgets under the context manager:

```python
def compose(self) -> ComposeResult:
    with Collapsible():
        yield Label("Verbose sentence to show by default.")

```

## Title

`Collapsible` can have a custom title instead of "Toggle" by `title` argument of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="An interesting story."):
        yield Label("Interesting but verbose story.")

```

## Collapse/Expand Symbols

`Collapsible` can have different symbol(label)s for each expanded/collapsed status.

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="", collapsed_symbol="► Show more", expanded_symbol="▼ Close"):
        yield Label("Many words.")

```

## Collapse/Expand

If can set the initial status of `collapsed` by `collapsed` argument of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="Contents 1", collapsed=False):
        yield Label("Short sentence to show by default.")

    with Collapsible(title="Contents 2", collapsed=True):  # Default is True
        yield Label("Verbose unecessary sentence to show by default.")
```

## Example

The following example contains three `Collapsible`s.

=== "Output"

    ```{.textual path="docs/examples/widgets/collapsible.py"}
    ```

=== "collapsible.py"

    ```python
    --8<-- "docs/examples/widgets/collapsible.py"
    ```

## Reactive attributes

| Name        | Type   | Default | Description                                                    |
| ----------- | ------ | ------- | -------------------------------------------------------------- |
| `collapsed` | `bool` | `True`  | Invisibility of `Contents`. Set it `False` to show `Contents`. |

## Messages

- [Collapsible.Summary.Toggle][Collapsible.Summary.Toggle]

## See also

<!-- TODO: Add Accordion widgets later -->

---


::: textual.widgets.Collapsible
    options:
      heading_level: 2
