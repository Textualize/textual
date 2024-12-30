"""
Tools for lazy loading widgets.
"""

from __future__ import annotations

from textual.widget import Widget


class Lazy(Widget):
    """Wraps a widget so that it is mounted *lazily*.

    Lazy widgets are mounted after the first refresh. This can be used to display some parts of
    the UI very quickly, followed by the lazy widgets. Technically, this won't make anything
    faster, but it reduces the time the user sees a blank screen and will make apps feel
    more responsive.

    Making a widget lazy is beneficial for widgets which start out invisible, such as tab panes.

    Note that since lazy widgets aren't mounted immediately (by definition), they will not appear
    in queries for a brief interval until they are mounted. Your code should take this into account.

    Example:
        ```python
        def compose(self) -> ComposeResult:
            yield Footer()
            with ColorTabs("Theme Colors", "Named Colors"):
                yield Content(ThemeColorButtons(), ThemeColorsView(), id="theme")
                yield Lazy(NamedColorsView())
        ```

    """

    DEFAULT_CSS = """
    Lazy {
        display: none;        
    } 
    """

    def __init__(self, widget: Widget) -> None:
        """Create a lazy widget.

        Args:
            widget: A widget that should be mounted after a refresh.
        """
        self._replace_widget = widget
        super().__init__()

    def compose_add_child(self, widget: Widget) -> None:
        self._replace_widget.compose_add_child(widget)

    async def mount_composed_widgets(self, widgets: list[Widget]) -> None:
        parent = self.parent
        if parent is None:
            return
        assert isinstance(parent, Widget)

        async def mount() -> None:
            """Perform the mount and discard the lazy widget."""
            await parent.mount(self._replace_widget, after=self)
            await self.remove()

        self.call_after_refresh(mount)


class Reveal(Widget):
    """Similar to [Lazy][textual.lazy.Lazy], but mounts children sequentially.

    This is useful when you have so many child widgets that there is a noticeable delay before
    you see anything. By mounting the children over several frames, the user will feel that
    something is happening.

    Example:
        ```python
        def compose(self) -> ComposeResult:
            with lazy.Reveal(containers.VerticalScroll(can_focus=False)):
                yield Markdown(WIDGETS_MD, classes="column")
                yield Buttons()
                yield Checkboxes()
                yield Datatables()
                yield Inputs()
                yield ListViews()
                yield Logs()
                yield Sparklines()
            yield Footer()
        ```
    """

    DEFAULT_CSS = """
    Reveal {
        display: none;
    }
    """

    def __init__(self, widget: Widget) -> None:
        """
        Args:
            widget: A widget to mount.
        """
        self._replace_widget = widget
        self._widgets: list[Widget] = []
        super().__init__()

    @classmethod
    def _reveal(cls, parent: Widget, widgets: list[Widget]) -> None:
        """Reveal children lazily.

        Args:
            parent: The parent widget.
            widgets: Child widgets.
        """

        async def check_children() -> None:
            """Check for pending children"""
            if not widgets:
                return
            widget = widgets.pop(0)
            try:
                await parent.mount(widget)
            except Exception:
                # I think this can occur if the parent is removed before all children are added
                # Only noticed this on shutdown
                return

            if widgets:
                parent.set_timer(0.02, check_children)

        parent.call_next(check_children)

    def compose_add_child(self, widget: Widget) -> None:
        self._widgets.append(widget)

    async def mount_composed_widgets(self, widgets: list[Widget]) -> None:
        parent = self.parent
        if parent is None:
            return
        assert isinstance(parent, Widget)
        await parent.mount(self._replace_widget, after=self)
        await self.remove()
        self._reveal(self._replace_widget, self._widgets.copy())
        self._widgets.clear()
