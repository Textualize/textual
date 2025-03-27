from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, TextArea


class TextAreaDialog(ModalScreen):
    BINDINGS = [("escape", "dismiss")]

    def compose(self) -> ComposeResult:
        yield TextArea(
            tab_behavior="focus",  # the default
        )
        yield Button("Submit")


class TextAreaDialogApp(App):
    def on_mount(self) -> None:
        self.push_screen(TextAreaDialog())


async def test_escape_key_when_tab_behavior_is_focus():
    """Regression test for https://github.com/Textualize/textual/issues/4110

    When the `tab_behavior` of TextArea is the default to shift focus,
    pressing <Escape> should not shift focus but instead skip and allow any
    parent bindings to run.
    """

    app = TextAreaDialogApp()
    async with app.run_test() as pilot:
        # Sanity check
        assert isinstance(pilot.app.screen, TextAreaDialog)
        assert isinstance(pilot.app.focused, TextArea)

        # Pressing escape should dismiss the dialog screen, not focus the button
        await pilot.press("escape")
        assert not isinstance(pilot.app.screen, TextAreaDialog)


async def test_escape_key_when_tab_behavior_is_indent():
    """When the `tab_behavior` of TextArea is indent rather than switch focus,
    pressing <Escape> should instead shift focus.
    """

    app = TextAreaDialogApp()
    async with app.run_test() as pilot:
        # Sanity check
        assert isinstance(pilot.app.screen, TextAreaDialog)
        assert isinstance(pilot.app.focused, TextArea)

        pilot.app.screen.query_one(TextArea).tab_behavior = "indent"
        # Pressing escape should focus the button, not dismiss the dialog screen
        await pilot.press("escape")
        assert isinstance(pilot.app.screen, TextAreaDialog)
        assert isinstance(pilot.app.focused, Button)
