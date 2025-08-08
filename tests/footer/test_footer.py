from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Button, Footer


async def test_footer_bindings() -> None:
    app_binding_count = 0

    class TestWidget(Widget, can_focus=True):
        BINDINGS = [
            Binding("b", "widget_binding", "Overridden Binding"),
        ]

        DEFAULT_CSS = """
        TestWidget {
            border: tall $background;
            width: 50%;
            height: 50%;
            content-align: center middle;

            &:focus {
                border: tall $secondary;
            }
        }
        """

        def action_widget_binding(self) -> None:
            assert False, "should never be called since there is a priority binding"

    class PriorityBindingApp(App):
        BINDINGS = [
            Binding("b", "app_binding", "Priority Binding", priority=True),
        ]

        CSS = """
        Screen {
            align: center middle;
        }
        """

        def compose(self) -> ComposeResult:
            yield TestWidget()
            yield Button("Move Focus")
            yield Footer()

        def action_app_binding(self) -> None:
            nonlocal app_binding_count
            app_binding_count += 1

    app = PriorityBindingApp()
    async with app.run_test() as pilot:
        assert app_binding_count == 0
        # Pause to ensure the footer is fully composed to avoid flakiness in CI
        await pilot.pause(0.4)
        await app.wait_for_refresh()

        footer_key_clicked = await pilot.click("FooterKey")
        assert footer_key_clicked is True  # Sanity check
        await pilot.pause()
        assert app_binding_count == 1

        footer_key_clicked = await pilot.click("FooterKey")
        assert footer_key_clicked is True  # Sanity check
        await pilot.pause()
        assert app_binding_count == 2
