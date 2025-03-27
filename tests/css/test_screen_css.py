from textual.app import App
from textual.color import Color
from textual.screen import Screen
from textual.widgets import Label

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)


class BaseScreen(Screen):
    def compose(self):
        yield Label("Hello, world!", id="app-css")
        yield Label("Hello, world!", id="screen-css-path")
        yield Label("Hello, world!", id="screen-css")


class ScreenWithCSS(Screen):
    SCOPED_CSS = False
    CSS = """
    #screen-css {
        background: #ff0000;
    }
    """

    CSS_PATH = "test_screen_css.tcss"

    def compose(self):
        yield Label("Hello, world!", id="app-css")
        yield Label("Hello, world!", id="screen-css-path")
        yield Label("Hello, world!", id="screen-css")


class BaseApp(App):
    """Base app for testing screen CSS when pushing screens."""

    CSS = """
    #app-css {
        background: #00ff00;
    }
    #screen-css-path {
        background: #00ff00;
    }
    #screen-css {
        background: #00ff00;
    }
    """

    def on_mount(self):
        self.push_screen(BaseScreen())


class SwitchBaseApp(BaseApp):
    """Base app for testing screen CSS when switching a screen."""

    def on_mount(self):
        self.push_screen(BaseScreen())


def check_colors_before_screen_css(app: BaseApp):
    assert app.screen.query_one("#app-css").styles.background == GREEN
    assert app.screen.query_one("#screen-css-path").styles.background == GREEN
    assert app.screen.query_one("#screen-css").styles.background == GREEN


def check_colors_after_screen_css(app: BaseApp):
    assert app.screen.query_one("#app-css").styles.background == GREEN
    assert app.screen.query_one("#screen-css-path").styles.background == BLUE
    assert app.screen.query_one("#screen-css").styles.background == RED


async def test_screen_pushing_and_popping_does_not_reparse_css():
    """Check that pushing and popping the same screen doesn't trigger CSS reparses."""

    class MyApp(BaseApp):
        def key_p(self):
            self.push_screen(ScreenWithCSS())

        def key_o(self):
            self.pop_screen()

    counter = 0

    def reparse_wrapper(reparse):
        def _reparse(*args, **kwargs):
            nonlocal counter
            counter += 1
            return reparse(*args, **kwargs)

        return _reparse

    app = MyApp()
    app.stylesheet.reparse = reparse_wrapper(app.stylesheet.reparse)
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("o")
        await pilot.press("p")
        await pilot.press("o")
        await pilot.press("p")
        await pilot.press("o")
        await pilot.press("p")
        await pilot.press("o")
        assert counter == 1


async def test_screen_css_push_screen_instance():
    """Check that screen CSS is loaded and applied when pushing a screen instance."""

    class MyApp(BaseApp):
        def key_p(self):
            self.push_screen(ScreenWithCSS())

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_push_screen_instance_by_name():
    """Check that screen CSS is loaded and applied when pushing a screen name that points to a screen instance."""

    class MyApp(BaseApp):
        SCREENS = {"screenwithcss": ScreenWithCSS}

        def key_p(self):
            self.push_screen("screenwithcss")

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_push_screen_type_by_name():
    """Check that screen CSS is loaded and applied when pushing a screen name that points to a screen class."""

    class MyApp(BaseApp):
        SCREENS = {"screenwithcss": ScreenWithCSS}

        def key_p(self):
            self.push_screen("screenwithcss")

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_screen_instance():
    """Check that screen CSS is loaded and applied when switching to a screen instance."""

    class MyApp(SwitchBaseApp):
        def key_p(self):
            self.switch_screen(ScreenWithCSS())

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_screen_instance_by_name():
    """Check that screen CSS is loaded and applied when switching a screen name that points to a screen instance."""

    class MyApp(SwitchBaseApp):
        SCREENS = {"screenwithcss": ScreenWithCSS}

        def key_p(self):
            self.switch_screen("screenwithcss")

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_screen_type_by_name():
    """Check that screen CSS is loaded and applied when switching a screen name that points to a screen class."""

    class MyApp(SwitchBaseApp):
        SCREENS = {"screenwithcss": ScreenWithCSS}

        async def key_p(self):
            self.switch_screen("screenwithcss")

        def key_o(self):
            self.pop_screen()

    app = MyApp()
    async with app.run_test() as pilot:
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_mode_screen_instance():
    """Check that screen CSS is loaded and applied when switching to a mode with a screen instance."""

    class MyApp(BaseApp):
        MODES = {
            "base": BaseScreen,
            "mode": ScreenWithCSS,
        }

        def key_p(self):
            self.switch_mode("mode")

        def key_o(self):
            self.switch_mode("base")

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_mode_screen_instance_by_name():
    """Check that screen CSS is loaded and applied when switching to a mode with a screen instance name."""

    class MyApp(BaseApp):
        SCREENS = {
            "screenwithcss": ScreenWithCSS,
        }

        MODES = {
            "base": BaseScreen,
            "mode": "screenwithcss",
        }

        def key_p(self):
            self.switch_mode("mode")

        def key_o(self):
            self.switch_mode("base")

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)


async def test_screen_css_switch_mode_screen_type_by_name():
    """Check that screen CSS is loaded and applied when switching to a mode with a screen type name."""

    class MyApp(BaseApp):
        SCREENS = {
            "screenwithcss": ScreenWithCSS,
        }

        MODES = {
            "base": BaseScreen,
            "mode": "screenwithcss",
        }

        def key_p(self):
            self.switch_mode("mode")

        def key_o(self):
            self.switch_mode("base")

    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("o")
        check_colors_before_screen_css(app)
        await pilot.press("p")
        check_colors_after_screen_css(app)
        await pilot.press("o")
        check_colors_after_screen_css(app)
