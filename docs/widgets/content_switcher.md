# ContentSwitcher

!!! tip "Added in version 0.14.0"

A widget for containing and switching display between multiple child
widgets.

- [ ] Focusable
- [X] Container

## Example

The example below uses a `ContentSwitcher` in combination with two `Button`s
to create a simple tabbed view. Note how each `Button` has an ID set, and
how each child of the `ContentSwitcher` has a corresponding ID; then a
`Button.Clicked` handler is used to set `ContentSwitcher.current` to switch
between the different views.

=== "Output"

    ```{.textual path="docs/examples/widgets/content_switcher.py"}
    ```

=== "content_switcher.py"

    ~~~python
    --8<-- "docs/examples/widgets/content_switcher.py"
    ~~~

    1. A `Horizontal` to hold the buttons, each with a unique ID.
    2. This button will select the `DataTable` in the `ContentSwitcher`.
    3. This button will select the `Markdown` in the `ContentSwitcher`.
    4. Note that the initial visible content is set by its ID, see below.
    5. When a button is pressed, its ID is used to switch to a different widget in the `ContentSwitcher`. Remember that IDs are unique within parent, so the buttons and the widgets in the `ContentSwitcher` can share IDs.

=== "content_switcher.tcss"

    ~~~sass
    --8<-- "docs/examples/widgets/content_switcher.tcss"
    ~~~

When the user presses the "Markdown" button the view is switched:

```{.textual path="docs/examples/widgets/content_switcher.py" lines="40" press="tab,enter"}
```

## Reactive Attributes

| Name      | Type            | Default | Description                                                             |
| --------- | --------------- | ------- | ----------------------------------------------------------------------- |
| `current` | `str` \| `None` | `None`  | The ID of the currently-visible child. `None` means nothing is visible. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


---


::: textual.widgets.ContentSwitcher
    options:
      heading_level: 2
