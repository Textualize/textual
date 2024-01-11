"""Provides a dialog widget."""

from __future__ import annotations

from typing_extensions import Final

from ..app import ComposeResult
from ..containers import VerticalScroll
from ..css.query import NoMatches
from ..geometry import Size
from ..reactive import var
from ..widget import Widget

_MAX_DIALOG_DIMENSION: Final[float] = 0.9
"""The idea maximum dimension for the dialog in respect to the sceen."""


class Body(VerticalScroll, can_focus=False):
    """Internal dialog container class for the main body of the dialog."""

    DEFAULT_CSS = """
    Body {
        width: auto;
        height: auto;
    }
    """

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Get the ideal height for the body of the dialog.

        Args:
            container: The container size.
            viewport: The viewport.
            width: The content width.

        Returns:
            The height of the body portion of the dialog (in lines).

        Ideally we'd want this widget to be `height: auto` and `max-height:
        1fr`, with the constraint on the ultimate height being a
        `max-height` on the container. As of the time of writing, there's no
        (obvious?) way to do this in CSS (that particular CSS setup doesn't
        do what you'd probably expect).

        So in this widget we simply set the `height` to `auto` and then
        constrain the maximum height with this method; the idea being that
        the content height will be capped at the maximum height that will
        push the container to what we want its `max-height` to be, and no
        further.
        """
        height = super().get_content_height(container, viewport, width)
        if isinstance(self.parent, Widget):
            try:
                # See if the dialog has an ActionArea.
                action_area = self.parent.query_one(Dialog.ActionArea)
            except NoMatches:
                # It's fine if it doesn't; that just means we don't need to
                # take it into account for this calculation to take place.
                pass
            else:
                return min(
                    # Use the minimum of either the actual content height...
                    height,
                    # ...or maximum fraction of the screen...
                    int(self.screen.size.height * _MAX_DIALOG_DIMENSION)
                    # ...minus the full height of the ActionArea...
                    - action_area.outer_size.height
                    # ...and minus the size of the "non-content" parts of
                    # the container.
                    - (self.parent.outer_size.height - self.parent.size.height),
                )
        return height


class Dialog(Widget):
    """A dialog widget."""

    DEFAULT_CSS = """
    $--dialog-border-color: $primary;

    Dialog {

        layout: vertical;

        width: auto;
        height: auto;
        max-width: 90%;
        /*max-height: 90%; Using the get_content_height hack above instead. */

        border: panel $--dialog-border-color;
        border-title-color: $accent;
        background: $surface;

        padding: 1 1 0 1;

        ActionArea {

            layout: horizontal;
            align: right middle;

            height: auto;
            width: auto;

            border-top: $--dialog-border-color;

            padding: 1 1 0 1;

            /* The developer may place widgets directly into the action
            area; they will likely do this half expecting that there will be
            a bit of space between each of the widgets. Let's help them with
            that. */
            &> * {
                margin-left: 1;
            }

            &> GroupLeft {

                layout: horizontal;
                align: left middle;

                height: auto;
                width: 1fr;

                /* The rule above for all items in the ActionArea will give
                this grouping container a left margin too; but we don't want
                that. */
                margin-left: 0;
            }

            /* Devs will likely compose labels into the ActionArea,
            expecting that they'll vertically line up with most other things
            (most of those other) things going in often being 3 cells high.
            So let's be super helpful here and have a default styling that
            just does the right thing out of the box. */
            Label {
                height: 100%;
                content-align: center middle;
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
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._dialog_children: list[Widget] = list(children)
        """Holds the widgets that will go to making up the dialog."""
        self.title = title

    def _watch_title(self) -> None:
        """React to the title being changed."""
        self.border_title = self.title

    class ActionArea(Widget):
        """A container that holds widgets that specify actions to perform on a dialog.

        This is the area in which buttons and other widgets should go that
        dictate what actions should be performed on the contents of the
        dialog.

        Widgets composed into this area will be grouped to the right, with a
        1-cell margin between them. If you wish to group some widgets to the
        left of the area group them inside a `Dialog.ActionArea.GroupLeft`.
        """

        class GroupLeft(Widget):
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

    def on_mount(self) -> None:
        # DEBUG
        for widget in [self, *self.query("*")]:
            widget.tooltip = "\n".join(
                f"{node!r}" for node in widget.ancestors_with_self
            )
