from textual._easing import EASING
from textual.app import App
from textual.reactive import Reactive

from textual.views import DockView
from textual.widgets import Placeholder, TreeControl, ScrollView, TreeClick


class EasingApp(App):
    """An app do demonstrate easing."""

    side = Reactive(False)
    easing = Reactive("linear")

    def watch_side(self, side: bool) -> None:
        """Animate when the side changes (False for left, True for right)."""
        width = self.easing_view.size.width
        animate_x = (width - self.placeholder.size.width) if side else 0
        self.placeholder.animate(
            "layout_offset_x", animate_x, easing=self.easing, duration=1
        )

    async def on_mount(self) -> None:
        """Called when application mode is ready."""

        self.placeholder = Placeholder()
        self.easing_view = DockView()
        self.placeholder.style = "white on dark_blue"

        tree = TreeControl("Easing", {})
        for easing_key in sorted(EASING.keys()):
            await tree.add(tree.root.id, easing_key, {"easing": easing_key})
        await tree.root.expand()

        await self.screen.dock(ScrollView(tree), edge="left", size=32)
        await self.screen.dock(self.easing_view)
        await self.easing_view.dock(self.placeholder, edge="left", size=32)

    async def handle_tree_click(self, message: TreeClick[dict]) -> None:
        """Called in response to a tree click."""
        self.easing = message.node.data.get("easing", "linear")
        self.side = not self.side


EasingApp().run(log_path="textual.log")
