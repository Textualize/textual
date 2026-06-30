import pytest
import asyncio

from textual.app import App
from textual.widgets import Select

SELECT_OPTIONS = [(str(n), n) for n in range(3)]

from textual.widgets._select import SelectCurrent

async def test_select_current_update_before_mount():
    """Test that updating SelectCurrent before mount does not crash."""
    app = App()
    async with app.run_test():
        select_current = SelectCurrent("placeholder")
        # Update before it is mounted / composed
        select_current.update("new label")
        
        # After mounting, the label should reflect the updated value
        app.mount(select_current)
        await app.workers.wait_for_complete()
        
        # Wait for the next tick to ensure label is updated
        # (Though we might need to check if label text is correct)
