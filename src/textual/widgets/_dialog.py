"""Provides a dialog widget."""

from __future__ import annotations

from typing import get_args

from typing_extensions import Final, Literal

from ..app import ComposeResult
from ..containers import VerticalScroll
from ..css._error_tools import friendly_list
from ..css.query import NoMatches
from ..geometry import Size
from ..reactive import var
from ..widget import Widget

_MAX_DIALOG_DIMENSION: Final[float] = 0.9
"""The ideal maximum dimension for the dialog in respect to the screen."""

DialogVariant = Literal["default", "success", "warning", "error"]
"""The names of the valid dialog variants.

These are the variants that can be used with a [`Dialog`][textual.widgets.Dialog].
"""

##############################################################################
from rich.console import Group
from rich.rule import Rule


class DOMInfo:
    def __init__(self, widget: Widget) -> None:
        self._widget = widget

    def __rich__(self) -> Group:
        return Group(
            Rule("DOM hierarchy"),
            "\n".join(f"{node!r}" for node in self._widget.ancestors_with_self),
            Rule("Dimensions"),
            f"Container: {self._widget.container_size}",
            f"Content: {self._widget.content_size}",
            Rule("CSS"),
            self._widget.styles.css,
            Rule(),
        )

    @classmethod
    def attach_to(cls, node: Widget) -> None:
        for widget in [node, *node.query("*")]:
            widget.tooltip = cls(widget)


##############################################################################


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

        Ideally we'd want this widget to be `height: auto` until it would be
        too tall for the maximum height of the dialog, minus the height
        needed for the `ActionArea`. At the moment there's no simple method
        of doing this in with Textual's CSS.

        So in this widget we simply set the `height` to `auto` and then
        constrain the maximum height with this method; the idea being that
        the content height will be capped at the maximum height that will
        push the container to what we want its `max-height` to be, and no
        further.
        """
        height = super().get_content_height(container, viewport, width)
        if isinstance(self.parent, Dialog):
            try:
                # See if the dialog has an ActionArea.
                action_area = self.parent.query_one(Dialog.ActionArea)
            except NoMatches:
                # It's fine if it doesn't; that just means we don't need to
                # take it into account for this calculation to take place.
                pass
            else:
                height = min(
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
    Dialog {

        layout: vertical;

        width: auto;
        height: auto;
        max-width: 90%;
        /*max-height: 90%; Using the get_content_height hack above instead. */

        border: panel $primary;
        border-title-color: $accent;
        background: $surface;

        padding: 1 1 0 1;

        ActionArea {

            layout: horizontal;
            align: right middle;

            /* Action area should perfectly wrap its content. */
            height: auto;
            width: auto;

            border-top: $primary;

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

                /* The grouping container should perfectly wrap its content. */
                height: auto;
                width: auto;
                dock: left;

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

        /***
         * Styling exceptions for each of the variants.
         */

        &.-success {
            border: panel $success;
            border-title-color: initial;

            ActionArea {
                border-top: $success;
            }
        }

        &.-warning {
            border: panel $warning;
            border-title-color: initial;

            ActionArea {
                border-top: $warning;
            }
        }

        &.-error {
            border: panel $error;
            border-title-color: initial;

            ActionArea {
                border-top: $error;
            }
        }
    }
    """

    variant: var[DialogVariant] = var("default")
    """The variant of dialog."""

    title: var[str] = var("")
    """The title of the dialog."""

    def __init__(
        self,
        *children: Widget,
        title: str = "",
        variant: DialogVariant = "default",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the dialog widget.

        Args:
            children: The child widgets for the dialog.
            title: The title for the dialog.
            variant: The variant of the dialog.
            name: The name of the dialog.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes of the dialog.
            disabled: Whether the dialog is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._dialog_children: list[Widget] = list(children)
        """Holds the widgets that will go to making up the dialog."""
        self.variant = variant
        self.title = title

    def _watch_variant(
        self, old_variant: DialogVariant, new_variant: DialogVariant
    ) -> None:
        """React to the variant being changed."""
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{new_variant}")

    def _validate_variant(self, variant: DialogVariant) -> DialogVariant:
        """Ensure that the given variant is a supported value."""
        if variant not in get_args(DialogVariant):
            raise ValueError(
                f"Valid dialog variants are {friendly_list(get_args(DialogVariant))}"
            )
        return variant

    def _watch_title(self) -> None:
        """React to the title being changed."""
        self.border_title = self.title

    class MisplacedActionGroup(Exception):
        """Error raised if an action group is misplaced."""

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

            def on_mount(self) -> None:
                """Check that we're only inside an `ActionArea`."""
                if not isinstance(self.parent, Dialog.ActionArea):
                    raise Dialog.MisplacedActionGroup(
                        "A GroupLeft can only be used inside an ActionArea."
                    )

        def get_content_width(self, container: Size, viewport: Size) -> int:
            """Get the ideal width for the `ActionArea`.

            Args:
                container: The container size.
                viewport: The viewport.

            Returns:
                The width of the action area for the dialog.

            Much like with `Body.get_content_height` this seeks to work
            around a thing we need to figure out in CSS; where we want the
            width of the dialog itself to be enough for the width of the
            body or the width of the content of the action area; whichever
            is greater.

            There's no easy way to say that in CSS right at the moment, so
            this in concert with `Body.get_content_height` helps push the
            layout in the right direction.
            """
            width = super().get_content_width(container, viewport)
            if isinstance(self.parent, Dialog):
                try:
                    # See if the dialog has a body yet.
                    body = self.parent.query_one(Body)
                except NoMatches:
                    # It's fine if it doesn't; that just means we'll go
                    # ahead and use our "normal" content width.
                    pass
                else:
                    width = max(
                        # Use our own content width...
                        width,
                        # ...or the width of the body, minus our horizontal
                        # padding and margins; whichever is greater.
                        body.size.width
                        - (
                            self.styles.padding.right
                            + self.styles.padding.left
                            + self.styles.margin.right
                            + self.styles.margin.left
                        ),
                    )
            return width

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
        DOMInfo.attach_to(self)

    @staticmethod
    def success(
        *children: Widget,
        title: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Dialog:
        """Create a success variant dialog widget.

        Args:
            children: The child widgets for the dialog.
            title: The title for the dialog.
            name: The name of the dialog.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes of the dialog.
            disabled: Whether the dialog is disabled or not.
        """
        return Dialog(
            *children,
            title=title,
            variant="success",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @staticmethod
    def warning(
        *children: Widget,
        title: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Dialog:
        """Create a warning variant dialog widget.

        Args:
            children: The child widgets for the dialog.
            title: The title for the dialog.
            name: The name of the dialog.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes of the dialog.
            disabled: Whether the dialog is disabled or not.
        """
        return Dialog(
            *children,
            title=title,
            variant="warning",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @staticmethod
    def error(
        *children: Widget,
        title: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Dialog:
        """Create a warning variant dialog widget.

        Args:
            children: The child widgets for the dialog.
            title: The title for the dialog.
            name: The name of the dialog.
            id: The ID of the dialog in the DOM.
            classes: The CSS classes of the dialog.
            disabled: Whether the dialog is disabled or not.
        """
        return Dialog(
            *children,
            title=title,
            variant="error",
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
