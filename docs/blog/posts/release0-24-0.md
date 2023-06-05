---
draft: false
date: 2023-05-08
categories:
  - Release
title: "Textual 0.24.0 adds a Select control"
authors:
  - willmcgugan
---

# Textual 0.24.0 adds a Select control

Coming just 5 days after the last release, we have version 0.24.0 which we are crowning the King of Textual releases.
At least until it is deposed by version 0.25.0.

<!-- more -->

The highlight of this release is the new [Select](/widget_gallery/#select) widget: a very familiar control from the web and desktop worlds.
Here's a screenshot and code:

=== "Output (expanded)"

    ```{.textual path="docs/examples/widgets/select_widget.py" press="tab,enter,down,down"}
    ```

=== "select_widget.py"

    ```python
    --8<-- "docs/examples/widgets/select_widget.py"
    ```

=== "select.css"

    ```sass
    --8<-- "docs/examples/widgets/select.css"
    ```

## New styles

This one required new functionality in Textual itself.
The "pull-down" overlay with options presented a difficulty with the previous API.
The overlay needed to appear over any content below it.
This is possible (using [layers](https://textual.textualize.io/styles/layers/)), but there was no simple way of positioning it directly under the parent widget.

We solved this with a new "overlay" concept, which can considered a special layer for user interactions like this Select, but also pop-up menus, tooltips, etc.
Widgets styled to use the overlay appear in their natural place in the "document", but on top of everything else.

A second problem we tackled was ensuring that an overlay widget was never clipped.
This was also solved with a new rule called "constrain".
Applying `constrain` to a widget will keep the widget within the bounds of the screen.
In the case of `Select`, if you expand the options while at the bottom of the screen, then the overlay will be moved up so that you can see all the options.

These new rules are currently undocumented as they are still subject to change, but you can see them in the [Select](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_select.py#L179) source if you are interested.

In a future release these will be finalized and you can confidently use them in your own projects.

## Fixes for the @on decorator

The new `@on` decorator is proving popular.
To recap, it is a more declarative and finely grained way of dispatching messages.
Here's a snippet from the [calculator](https://github.com/Textualize/textual/blob/main/examples/calculator.py) example which uses `@on`:

```python
    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def pressed_op(self, event: Button.Pressed) -> None:
        """Pressed one of the arithmetic operations."""
        self.right = Decimal(self.value or "0")
        self._do_math()
        assert event.button.id is not None
        self.operator = event.button.id
```

The decorator arranges for the method to be called when any of the four math operation buttons are pressed.

In 0.24.0 we've fixed some missing attributes which prevented the decorator from working with some messages.
We've also extended the decorator to use keywords arguments, so it will match attributes other than `control`.

## Other fixes

There is a surprising number of fixes in this release for just 5 days. See [CHANGELOG.md](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for details.


## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
