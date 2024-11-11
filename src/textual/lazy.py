"""
Tools for lazy loading widgets.
"""

from __future__ import annotations

from functools import partial

from textual.widget import Widget


class Lazy(Widget):
    """Wraps a widget so that it is mounted *lazily*.

    Lazy widgets are mounted after the first refresh. This can be used to display some parts of
    the UI very quickly, followed by the lazy widgets. Technically, this won't make anything
    faster, but it reduces the time the user sees a blank screen and will make apps feel
    more responsive.

    Making a widget lazy is beneficial for widgets which start out invisible, such as tab panes.

    Note that since lazy widgets aren't mounted immediately (by definition), they will not appear
    in queries for a brief interval until they are mounted. Your code should take this in to account.

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
    DEFAULT_CSS = """
    Reveal {
        display: none;
    }
    """

    def __init__(self, widget: Widget, delay: float = 1 / 60) -> None:
        """Similar to [Lazy][textual.lazy.Lazy], but also displays *children* sequentially.

        The first frame will display the first child with all other children hidden.
        The remaining children will be displayed 1-by-1, over as may frames are required.

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

        Args:
            widget: A widget that should be mounted after a refresh.
            delay: A (short) delay between mounting widgets.
        """
        self._replace_widget = widget
        self._delay = delay
        super().__init__()

    @classmethod
    def _reveal(cls, parent: Widget, delay: float = 1 / 60) -> None:
        """Reveal children lazily.

        Args:
            parent: The parent widget.
            delay: A delay between reveals.
        """

        def check_children() -> None:
            """Check for un-displayed children."""
            iter_children = iter(parent.children)
            for child in iter_children:
                if not child.display:
                    child.display = True
                    break
            for child in iter_children:
                if not child.display:
                    parent.set_timer(
                        delay, partial(parent.call_after_refresh, check_children)
                    )
                    break

        check_children()

    def compose_add_child(self, widget: Widget) -> None:
        widget.display = False
        self._replace_widget.compose_add_child(widget)

    async def mount_composed_widgets(self, widgets: list[Widget]) -> None:
        parent = self.parent
        if parent is None:
            return
        assert isinstance(parent, Widget)

        if self._replace_widget.children:
            self._replace_widget.children[0].display = True
        await parent.mount(self._replace_widget, after=self)
        await self.remove()
        self._reveal(self._replace_widget, self._delay)
