# tests/test_binding_priority_collision.py
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Static


class FocusableWidget(Widget, can_focus=True):
    BINDINGS = [
        Binding(key="a", action="widget_a", description="Widget A"),
        Binding(key="f", action="widget_find", description="Widget Find"),
    ]
    def action_widget_a(self) -> None: ...
    def action_widget_find(self) -> None: ...


class PriorityOrderApp(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit", priority=True),
        Binding(key="j", action="jump", description="Jump", priority=True),
        Binding(key="f", action="find", description="Find", priority=True),
        Binding(key="n", action="find_next", description="Next", priority=True),
    ]
    def compose(self) -> ComposeResult:
        yield Static("test")
        yield FocusableWidget()
        yield Footer()
    def action_jump(self) -> None: ...
    def action_find(self) -> None: ...
    def action_find_next(self) -> None: ...
    def on_mount(self) -> None:
        self.query_one(FocusableWidget).focus()


async def test_priority_binding_collision_preserves_declared_order():
    """Regresión #4639: un binding de prioridad de la App que gana una
    colisión de tecla contra un widget enfocado debe aparecer en el orden
    declarado de la App, no en la posición del binding perdedor."""
    app = PriorityOrderApp()
    async with app.run_test():
        keys = list(app.screen.active_bindings.keys())
        assert keys.index("f") > keys.index("j")