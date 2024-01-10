"""Provides a dialog widget."""

from __future__ import annotations

from textual.app import ComposeResult

from ..containers import Horizontal, Vertical, VerticalScroll
from ..reactive import var
from ..widget import Widget


class Body(VerticalScroll, can_focus=False):
    """Internal dialog container class for the main body of the dialog."""


class Dialog(Vertical):
    """A dialog widget."""

    DEFAULT_CSS = """
    Dialog {
        border: panel $panel;
        width: auto;
        height: auto;
        max-width: 90%;
        max-height: 90%;

        ActionArea {
            align: right middle;
            height: auto;
            width: 1fr;

            /* The developer may place widgets directly into the action
            area; they will likely do this half expecting that there will be
            a bit of space between each of the widgets. Let's help them with
            that. */
            &> * {
                margin-left: 1;
            }

            &> GroupLeft {
                height: auto;
                width: 1fr;
                align: left middle;

                /* The rule above for all items in the ActionArea will give
                this grouping container a left margin too; but we don't want
                that. */
                margin-left: 0;
            }
        }
    }
    """

    title: var[str] = var("")
    """The title of the dialog."""

    def __init__(
        self,
        *children: Widget,
        title: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the dialog widget.

        Args:
            children: The child widgets for the dialog.
            title: The title for the dialog.
            name: The name of the dialog.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes of the dialog.
            disabled: Whether the dialog is disabled or not.
        """
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._dialog_children: list[Widget] = list(children)
        """Holds the widgets that will go to making up the dialog."""
        self.title = title

    def _watch_title(self) -> None:
        """React to the title being changed."""
        self.border_title = self.title

    class ActionArea(Horizontal):
        """A container that holds widgets that specify actions to perform on a dialog.

        This is the area in which buttons and other widgets should go that
        dictate what actions should be performed on the contents of the
        dialog.

        Widgets composed into this area will be grouped to the right, with a
        1-cell margin between them. If you wish to group some widgets to the
        left of the area group them inside a `Dialog.ActionArea.GroupLeft`.
        """

        class GroupLeft(Horizontal):
            """A container for grouping widgets to the left side of a `Dialog.ActionArea`."""

    def compose_add_child(self, widget: Widget) -> None:
        """Capture the widgets being added to the dialog for later processing.

        Args:
            widget: The widget being added.
        """
        self._dialog_children.append(widget)

    class TooManyActionAreas(Exception):
        """Raised if there is an attempt to add more than one `ActionArea` to a dialog."""

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog.

        Raises:
            TooManyActionAreas: If more than one `ActionArea` is added to a dialog.
        """
        # Loop over all of the children intended for the dialog, and extract
        # any instance of an `ActionArea`; meanwhile place everything else
        # inside a 'body' container that will scroll the content if
        # necessary.
        action_area: Dialog.ActionArea | None = None
        with Body():
            for widget in self._dialog_children:
                if isinstance(widget, Dialog.ActionArea):
                    if action_area is not None:
                        raise self.TooManyActionAreas(
                            "Only one ActionArea can be defined for a Dialog."
                        )
                    action_area = widget
                else:
                    yield widget
        if action_area is not None:
            yield action_area
