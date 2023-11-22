from textual.app import App, ComposeResult
from textual.color import Color
from textual.widget import Widget


class Base(Widget):
    DEFAULT_CSS = """
    Base {
        color: magenta;
    }
    """


class CustomWidget1(Base):
    DEFAULT_CSS = """
    CustomWidget1 {
        background: red
    }
    """


class CustomWidget2(CustomWidget1):
    DEFAULT_CSS = """
    CustomWidget2 {
        background: initial;
    }
    """


class CustomWidget3(CustomWidget2):
    pass


async def test_initial_default():
    class InitialApp(App):
        def compose(self) -> ComposeResult:
            yield Base(id="base")
            yield CustomWidget1(id="custom1")
            yield CustomWidget2(id="custom2")

    app = InitialApp()
    async with app.run_test():
        base = app.query_one("#base", Base)
        custom1 = app.query_one("#custom1", CustomWidget1)
        custom2 = app.query_one("#custom2", CustomWidget2)

        # No background set on base
        default_background = base.styles.background
        assert default_background == Color.parse("rgba(0,0,0,0)")
        # Customized background value, should be red
        assert custom1.styles.background == Color.parse("red")
        # Background has default value
        assert custom2.styles.background == default_background


async def test_initial():
    class InitialApp(App):
        CSS = """
        CustomWidget1 {
            color: red;
        }

        CustomWidget2 {
           color: initial;
        }

        CustomWidget3 {
            color: blue;
        }
        """

        def compose(self) -> ComposeResult:
            yield Base(id="base")
            yield CustomWidget1(id="custom1")
            yield CustomWidget2(id="custom2")
            yield CustomWidget3(id="custom3")

    app = InitialApp()
    async with app.run_test():
        base = app.query_one("#base")
        custom1 = app.query_one("#custom1")
        custom2 = app.query_one("#custom2")
        custom3 = app.query_one("#custom3")

        # Default color
        assert base.styles.color == Color.parse("magenta")

        # Explicitly set to red
        assert custom1.styles.color == Color.parse("red")

        # Set to initial, should be same as base
        assert custom2.styles.color == Color.parse("magenta")

        # Set to blue
        assert custom3.styles.color == Color.parse("blue")
