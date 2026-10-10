from textual.app import App, ComposeResult
from textual.widgets import ComboBox, Button
from textual.widgets._combo_box import ComboBoxInput, ComboBoxOverlay


async def test_combobox_filtering():
    """Test that filtering items works correctly based on input."""

    class ComboBoxApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ComboBox([("Apple", 1), ("Banana", 2), ("Cherry", 3), ("Date", 4)])

    app = ComboBoxApp()
    async with app.run_test() as pilot:
        combo_box = app.query_one(ComboBox)
        overlay = app.query_one(ComboBoxOverlay)

        # Initially there should be 4 options
        assert overlay.option_count == 4

        # Focus and type "a" -> Apple, Banana, Date (3 matches)
        await pilot.click(ComboBoxInput)
        await pilot.press("a")
        assert combo_box.expanded is True
        assert overlay.option_count == 3

        # Type "p" -> "ap" matches Apple only
        await pilot.press("p")
        assert overlay.option_count == 1

        # Clear input and type "xyz" -> no options, overlay hides
        await pilot.press("home", "shift+end", "delete")
        await pilot.press("x", "y", "z")
        assert overlay.option_count == 0
        assert combo_box.expanded is False


async def test_combobox_selection_flow():
    """Test the flow of selecting an item and emitting the Selected event."""

    events_received = []

    class ComboBoxApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ComboBox([("Apple", 1), ("Banana", 2)], value=1)

        def on_combo_box_selected(self, event: ComboBox.Selected) -> None:
            events_received.append(event)

    app = ComboBoxApp()
    async with app.run_test() as pilot:
        combo_box = app.query_one(ComboBox)
        input_widget = app.query_one(ComboBoxInput)

        # Initial value should be Apple (1)
        assert combo_box.value == 1
        assert input_widget.value == "Apple"

        # Focus the input, select-all, delete to clear deterministically
        await pilot.click(ComboBoxInput)
        await pilot.press("home", "shift+end", "delete")
        assert input_widget.value == ""

        # Both options should now be visible
        overlay = app.query_one(ComboBoxOverlay)
        assert combo_box.expanded is True
        assert overlay.option_count == 2

        # Arrow down to Banana (highlighted starts at 0=Apple, down goes to 1=Banana)
        await pilot.press("down")
        assert overlay.highlighted == 1

        # Press enter to select Banana
        await pilot.press("enter")

        assert combo_box.expanded is False
        assert combo_box.value == 2
        assert input_widget.value == "Banana"
        assert len(events_received) == 1
        assert events_received[0].value == 2

        # Now search for Apple again
        await pilot.press("home", "shift+end", "delete")
        await pilot.press("a", "p")
        assert combo_box.expanded is True
        await pilot.press("enter")

        assert combo_box.expanded is False
        assert combo_box.value == 1
        assert input_widget.value == "Apple"
        assert len(events_received) == 2
        assert events_received[1].value == 1


async def test_combobox_blur_closes_overlay():
    """Test that the overlay closes when focus leaves the ComboBox."""

    class ComboBoxApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ComboBox([("Apple", 1), ("Banana", 2)])
            yield Button("Other")

    app = ComboBoxApp()
    async with app.run_test() as pilot:
        combo_box = app.query_one(ComboBox)

        # Focus input and type to open overlay
        await pilot.click(ComboBoxInput)
        await pilot.press("a")
        assert combo_box.expanded is True

        # Click the button to move focus away
        await pilot.click(Button)
        assert combo_box.expanded is False


async def test_combobox_enter_no_match_reverts():
    """Test that pressing Enter with no matching option reverts to current selection."""

    class ComboBoxApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ComboBox([("Apple", 1), ("Banana", 2)], value=1)

    app = ComboBoxApp()
    async with app.run_test() as pilot:
        combo_box = app.query_one(ComboBox)
        input_widget = app.query_one(ComboBoxInput)

        assert combo_box.value == 1
        assert input_widget.value == "Apple"

        # Type something that matches nothing
        await pilot.click(ComboBoxInput)
        await pilot.press("home", "shift+end", "delete")
        await pilot.press("x", "y", "z")
        assert combo_box.expanded is False
        assert input_widget.value == "xyz"

        # Press Enter — should revert to "Apple" since no match
        await pilot.press("enter")
        assert combo_box.value == 1
        assert input_widget.value == "Apple"
        assert combo_box.expanded is False


async def test_combobox_enter_no_match_clears_when_no_selection():
    """Test that Enter with no match and no prior selection clears the input."""

    class ComboBoxApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ComboBox([("Apple", 1), ("Banana", 2)])

    app = ComboBoxApp()
    async with app.run_test() as pilot:
        combo_box = app.query_one(ComboBox)
        input_widget = app.query_one(ComboBoxInput)

        assert combo_box.value is None

        # Type something that matches nothing
        await pilot.click(ComboBoxInput)
        await pilot.press("x", "y", "z")
        assert input_widget.value == "xyz"

        # Press Enter — should clear input since there's no prior selection
        await pilot.press("enter")
        assert combo_box.value is None
        assert input_widget.value == ""
        assert combo_box.expanded is False
