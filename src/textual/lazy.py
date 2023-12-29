from .widget import Widget


class Lazy(Widget):
    DEFAULT_CSS = """
    Lazy {
        display: none;        
    } 
    """

    def __init__(self, widget: Widget) -> None:
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
            await parent.mount(self._replace_widget, after=self)
            await self.remove()

        self.call_after_refresh(mount)
