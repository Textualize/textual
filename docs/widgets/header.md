# Header

A simple header widget which docks itself to the top of the parent container.

!!! note

    The application title which is shown in the header is taken from the [`title`][textual.app.App.title] and [`sub_title`][textual.app.App.sub_title] of the application.

- [ ] Focusable
- [ ] Container

## Example

The example below shows an app with a `Header`.

=== "Output"

    ```{.textual path="docs/examples/widgets/header.py"}
    ```

=== "header.py"

    ```python
    --8<-- "docs/examples/widgets/header.py"
    ```

This example shows how to set the text in the `Header` using `App.title` and `App.sub_title`:

=== "Output"

    ```{.textual path="docs/examples/widgets/header_app_title.py"}
    ```

=== "header_app_title.py"

    ```python
    --8<-- "docs/examples/widgets/header_app_title.py"
    ```

## Reactive Attributes

| Name   | Type   | Default | Description                                                                                                                                                                                      |
| ------ | ------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tall` | `bool` | `True`  | Whether the `Header` widget is displayed as tall or not. The tall variant is 3 cells tall by default. The non-tall variant is a single cell tall. This can be toggled by clicking on the header. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Header
    options:
      heading_level: 2
