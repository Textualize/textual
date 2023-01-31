"""
Helper script to help document all widgets.

This goes through the widgets listed in textual.widgets and prints the scaffolding
for the tables that are used to document the classvars BINDINGS and COMPONENT_CLASSES.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import textual.widgets

if TYPE_CHECKING:
    from textual.binding import Binding


def print_bindings(widget: str, bindings: list[Binding]) -> None:
    """Print a table summarising the bindings.

    The table contains columns for the key(s) that trigger the binding,
    the method that it calls (and tries to link it to the widget itself),
    and the description of the binding.
    """
    if bindings:
        print("BINDINGS")
        print('"""')
        print("| Key(s) | Description |")
        print("| :- | :- |")

    for binding in bindings:
        print(f"| {binding.key} | {binding.description} |")

    if bindings:
        print('"""')


def print_component_classes(classes: set[str]) -> None:
    """Print a table to document these component classes.

    The table contains two columns, one with the component class name and another
    for the description of what the component class is for.
    The second column is always empty.
    """
    if classes:
        print("COMPONENT_CLASSES")
        print('"""')
        print("| Class | Description |")
        print("| :- | :- |")

    for cls in sorted(classes):
        print(f"| `{cls}` | XXX |")

    if classes:
        print('"""')


def main() -> None:
    """Main entrypoint.

    Iterates over all widgets and prints docs tables.
    """

    widgets: list[str] = textual.widgets.__all__

    for widget in widgets:
        w = getattr(textual.widgets, widget)
        bindings: list[Binding] = w.__dict__.get("BINDINGS", [])
        component_classes: set[str] = getattr(w, "COMPONENT_CLASSES", set())

        if bindings or component_classes:
            print(widget)
            print()
            print_bindings(widget, bindings)
            print_component_classes(component_classes)
            print()


if __name__ == "__main__":
    main()
