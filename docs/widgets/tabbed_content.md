# TabbedContent

!!! tip "Added in version 0.16.0"

Switch between mutually exclusive content panes via a row of tabs.

- [x] Focusable
- [x] Container

This widget combines the [Tabs](../widgets/tabs.md) and [ContentSwitcher](../widgets/content_switcher.md) widgets to create a convenient way of navigating content.

Only a single child of TabbedContent is visible at once.
Each child has an associated tab which will make it visible and hide the others.

## Composing

There are two ways to provide the titles for the tab.
You can pass them as positional arguments to the [TabbedContent][textual.widgets.TabbedContent] constructor:

```python
def compose(self) -> ComposeResult:
    with TabbedContent("Leto", "Jessica", "Paul"):
        yield Markdown(LETO)
        yield Markdown(JESSICA)
        yield Markdown(PAUL)
```

Alternatively you can wrap the content in a [TabPane][textual.widgets.TabPane] widget, which takes the tab title as the first parameter:

```python
def compose(self) -> ComposeResult:
    with TabbedContent():
        with TabPane("Leto"):
            yield Markdown(LETO)
        with TabPane("Jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul"):
            yield Markdown(PAUL)
```

## Switching tabs

If you need to programmatically switch tabs, you should provide an `id` attribute to the `TabPane`s.

```python
def compose(self) -> ComposeResult:
    with TabbedContent():
        with TabPane("Leto", id="leto"):
            yield Markdown(LETO)
        with TabPane("Jessica", id="jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul", id="paul"):
            yield Markdown(PAUL)
```

You can then switch tabs by setting the `active` reactive attribute:

```python
# Switch to Jessica tab
self.query_one(TabbedContent).active = "jessica"
```

!!! note

    If you don't provide `id` attributes to the tab panes, they will be assigned sequentially starting at `tab-1` (then `tab-2` etc).

## Initial tab

The first child of `TabbedContent` will be the initial active tab by default. You can pick a different initial tab by setting the `initial` argument to the `id` of the tab:

```python
def compose(self) -> ComposeResult:
    with TabbedContent(initial="jessica"):
        with TabPane("Leto", id="leto"):
            yield Markdown(LETO)
        with TabPane("Jessica", id="jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul", id="paul"):
            yield Markdown(PAUL)
```

## Example

The following example contains a `TabbedContent` with three tabs.

=== "Output"

    ```{.textual path="docs/examples/widgets/tabbed_content.py"}
    ```

=== "tabbed_content.py"

    ```python
    --8<-- "docs/examples/widgets/tabbed_content.py"
    ```

## Reactive attributes

| Name     | Type  | Default | Description                                                    |
| -------- | ----- | ------- | -------------------------------------------------------------- |
| `active` | `str` | `""`    | The `id` attribute of the active tab. Set this to switch tabs. |


## Messages

- [TabbedContent.TabActivated][textual.widgets.TabbedContent.TabActivated]

## See also


- [Tabs](tabs.md)
- [ContentSwitcher](content_switcher.md)


---


::: textual.widgets.TabbedContent
    options:
      heading_level: 2


---


::: textual.widgets.TabPane
    options:
      heading_level: 2
