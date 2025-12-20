from textual.app import App, ComposeResult
from textual.widgets import RadioSet, RadioButton


class RadioSetTestApp(App):
    def compose(self) -> ComposeResult:
        yield RadioSet(
            RadioButton("One"),
            RadioButton("Two"),
            RadioButton("Three"),
        )


async def test_radioset_clear():
    """clear() should remove all selections"""
    app = RadioSetTestApp()
    
    async with app.run_test() as pilot:
        rs = app.query_one(RadioSet)
        buttons = list(rs.query(RadioButton))
        rb1, rb2, rb3 = buttons
        
        await pilot.pause()
        
        # press second button
        rb2.value = True
        await pilot.pause()
        
        assert rs.pressed_button is rb2
        assert rs.pressed_index == 1
        assert rb2.value is True
        
        # now clear it
        rs.clear()
        await pilot.pause()
        
        assert rs.pressed_button is None
        assert rs.pressed_index == -1
        
        for rb in buttons:
            assert rb.value is False


async def test_clear_empty_radioset():
    """calling clear on empty radioset shouldn't crash"""
    
    class EmptyApp(App):
        def compose(self) -> ComposeResult:
            yield RadioSet()
    
    app = EmptyApp()
    
    async with app.run_test() as pilot:
        rs = app.query_one(RadioSet)
        await pilot.pause()
        
        rs.clear()  # shouldn't error
        await pilot.pause()
        
        assert rs.pressed_button is None
        assert rs.pressed_index == -1


async def test_clear_twice():
    """clearing multiple times should work fine"""
    
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield RadioSet(
                RadioButton("One"),
                RadioButton("Two"),
            )
    
    app = TestApp()
    
    async with app.run_test() as pilot:
        rs = app.query_one(RadioSet)
        btns = list(rs.query(RadioButton))
        await pilot.pause()
        
        btns[0].value = True
        await pilot.pause()
        assert rs.pressed_button is btns[0]
        
        rs.clear()
        await pilot.pause()
        assert rs.pressed_button is None
        
        # clear again - should still work
        rs.clear()
        await pilot.pause()
        assert rs.pressed_button is None
        assert rs.pressed_index == -1


async def test_can_select_after_clear():
    """after clearing, we should be able to select buttons again"""
    
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield RadioSet(
                RadioButton("Option A"),
                RadioButton("Option B"),
            )
    
    app = TestApp()
    
    async with app.run_test() as pilot:
        rs = app.query_one(RadioSet)
        btns = list(rs.query(RadioButton))
        await pilot.pause()
        
        rs.clear()
        await pilot.pause()
        assert rs.pressed_button is None
        
        # should be able to select again
        btns[1].value = True
        await pilot.pause()
        
        assert rs.pressed_button is btns[1]
        assert rs.pressed_index == 1