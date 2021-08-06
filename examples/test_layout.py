from rich import print
from rich.console import Console

from textual.geometry import Offset, Region
from textual.widgets import Placeholder


from textual.views import WindowView

p = Placeholder(height=10)
view = WindowView(p)

console = Console()
view.layout.reflow(console, 30, 25, Offset(0, 3))

print(view.layout._layout_map.widgets)

console.print(view.layout.render(console))

# console.print(view.layout.render(console, Region(100, 2, 10, 10)))
