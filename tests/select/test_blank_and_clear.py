import pytest

from textual.app import App
from textual.widgets import Select
from textual.widgets.select import InvalidSelectValueError

SELECT_OPTIONS = [(str(n), n) for n in range(3)]


async def test_value_is_blank_by_default():
    class SelectApp(App[None]):
        def compose(self):
            yield Select(SELECT_OPTIONS)

    app = SelectApp()
    async with app.run_test():
        select = app.query_one(Select)
        assert select.value == Select.BLANK
        assert select.is_blank()


async def test_setting_and_checking_blank():
    class SelectApp(App[None]):
        def compose(self):
            yield Select(SELECT_OPTIONS)

    app = SelectApp()
    async with app.run_test():
        select = app.query_one(Select)
        assert select.value == Select.BLANK
        assert select.is_blank()

        select.value = 0
        assert select.value != Select.BLANK
        assert not select.is_blank()

        select.value = Select.BLANK
        assert select.value == Select.BLANK
        assert select.is_blank()


async def test_clear_with_allow_blanks():
    class SelectApp(App[None]):
        def compose(self):
            yield Select(SELECT_OPTIONS, value=1)

    app = SelectApp()
    async with app.run_test():
        select = app.query_one(Select)
        assert select.value == 1  # Sanity check.
        select.clear()
        assert select.is_blank()


async def test_clear_fails_if_allow_blank_is_false():
    class SelectApp(App[None]):
        def compose(self):
            yield Select(SELECT_OPTIONS, allow_blank=False)

    app = SelectApp()
    async with app.run_test():
        select = app.query_one(Select)
        assert not select.is_blank()
        with pytest.raises(InvalidSelectValueError):
            select.clear()

async def test_selection_is_none_with_blank():
    class SelectApp(App[None]):
        def compose(self):
            yield Select(SELECT_OPTIONS)

    app = SelectApp()
    async with app.run_test():
        select = app.query_one(Select)
        assert select.selection is None
