# Collapsible

!!! tip "Added in version 0.37"

A container with a title that can be used to show (expand) or hide (collapse) content, either by clicking or focusing and pressing ++enter++.

- [x] Focusable
- [x] Container


## Composing

You can add content to a Collapsible widget either by passing in children to the constructor, or with a context manager (`with` statement).

Here is an example of using the constructor to add content:

```python
def compose(self) -> ComposeResult:
    yield Collapsible(Label("Hello, world."))
```

Here's how the to use it with the context manager:

```python
def compose(self) -> ComposeResult:
    with Collapsible():
        yield Label("Hello, world.")
```

The second form is generally preferred, but the end result is the same.

## Title

The default title "Toggle" can be customized by setting the `title` parameter of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="An interesting story."):
        yield Label("Interesting but verbose story.")
```

## Initial State

The initial state of the `Collapsible` widget can be customized via the `collapsed` parameter of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="Contents 1", collapsed=False):
        yield Label("Hello, world.")

    with Collapsible(title="Contents 2", collapsed=True):  # Default.
        yield Label("Hello, world.")
```

## Collapse/Expand Symbols

The symbols used to show the collapsed / expanded state can be customized by setting the parameters `collapsed_symbol` and `expanded_symbol`:

```python
def compose(self) -> ComposeResult:
    with Collapsible(collapsed_symbol=">>>", expanded_symbol="v"):
        yield Label("Hello, world.")
```

## Examples


The following example contains three `Collapsible`s in different states.

=== "All expanded"

    ```{.textual path="docs/examples/widgets/collapsible.py" press="e"}
    ```

=== "All collapsed"

    ```{.textual path="docs/examples/widgets/collapsible.py" press="c"}
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

    ```{.textual path="docs/examples/widgets/collapsible_nested.py"}
    ```

=== "collapsible_nested.py"

    ```python hl_lines="7"
    --8<-- "docs/examples/widgets/collapsible_nested.py"
    ```

### Custom Symbols

The following example shows `Collapsible` widgets with custom expand/collapse symbols.


=== "Output"

    ```{.textual path="docs/examples/widgets/collapsible_custom_symbol.py"}
    ```

=== "collapsible_custom_symbol.py"

    ```python
    --8<-- "docs/examples/widgets/collapsible_custom_symbol.py"
    ```

## Reactive Attributes

| Name        | Type   | Default     | Description                                          |
| ----------- | ------ | ------------| ---------------------------------------------------- |
| `collapsed` | `bool` | `True`      | Controls the collapsed/expanded state of the widget. |
| `title`     | `str`  | `"Toggle"`  | Title of the collapsed/expanded contents.            |

## Messages

- [Collapsible.Toggled][textual.widgets.Collapsible.Toggled]

## Bindings

The collapsible widget defines the following binding on its title:

::: textual.widgets._collapsible.CollapsibleTitle.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.


::: textual.widgets.Collapsible
    options:
      heading_level: 2
