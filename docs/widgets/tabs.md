# Tabs

!!! tip "Added in version 0.15.0"

Displays a number of tab headers which may be activated with a click or navigated with cursor keys.

- [x] Focusable
- [ ] Container

Construct a `Tabs` widget with strings or [Text][rich.text.Text] objects as positional arguments, which will set the labels in the tabs. Here's an example with three tabs:

```python
def compose(self) -> ComposeResult:
    yield Tabs("First tab", "Second tab", Text.from_markup("[u]Third[/u] tab"))
```

This will create [Tab][textual.widgets.Tab] widgets internally, with auto-incrementing `id` attributes (`"tab-1"`, `"tab-2"` etc).
You can also supply `Tab` objects directly in the constructor, which will allow you to explicitly set an `id`. Here's an example:

```python
def compose(self) -> ComposeResult:
    yield Tabs(
        Tab("First tab", id="one"),
        Tab("Second tab", id="two"),
    )
```

When the user switches to a tab by clicking or pressing keys, then `Tabs` will send a [Tabs.TabActivated][textual.widgets.Tabs.TabActivated] message which contains the `tab` that was activated.
You can then use `event.tab.id` attribute to perform any related actions.

## Clearing tabs

Clear tabs by calling the [clear][textual.widgets.Tabs.clear] method. Clearing the tabs will send a [Tabs.TabActivated][textual.widgets.Tabs.TabActivated] message with the `tab` attribute set to `None`.

## Adding tabs

Tabs may be added dynamically with the [add_tab][textual.widgets.Tabs.add_tab] method, which accepts strings, [Text][rich.text.Text], or [Tab][textual.widgets.Tab] objects.

## Example

The following example adds a `Tabs` widget above a text label. Press ++a++ to add a tab, ++c++ to clear the tabs.

=== "Output"

    ```{.textual path="docs/examples/widgets/tabs.py" press="a,a,a,a,right,right"}
    ```

=== "tabs.py"

    ```python
    --8<-- "docs/examples/widgets/tabs.py"
    ```


## Reactive Attributes

| Name     | Type  | Default | Description                                                                        |
| -------- | ----- | ------- | ---------------------------------------------------------------------------------- |
| `active` | `str` | `""`    | The ID of the active tab. Set this attribute to a tab ID to change the active tab. |


## Messages

- [Tabs.TabActivated][textual.widgets.Tabs.TabActivated]
- [Tabs.Cleared][textual.widgets.Tabs.Cleared]

## Bindings

The Tabs widget defines the following bindings:

::: textual.widgets.Tabs.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


---


::: textual.widgets.Tabs
    options:
      heading_level: 2


---

::: textual.widgets.Tab
    options:
      heading_level: 2
