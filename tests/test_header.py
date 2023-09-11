from textual.app import App
from textual.screen import Screen
from textual.widgets import Header


async def test_screen_title_none_is_ignored():
    class MyScreen(Screen):
        def compose(self):
            yield Header()

    class MyApp(App):
        TITLE = "app title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test():
        assert app.query_one("HeaderTitle").text == "app title"


async def test_screen_title_overrides_app_title():
    class MyScreen(Screen):
        TITLE = "screen title"

        def compose(self):
            yield Header()

    class MyApp(App):
        TITLE = "app title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test():
        assert app.query_one("HeaderTitle").text == "screen title"


async def test_screen_title_reactive_updates_title():
    class MyScreen(Screen):
        TITLE = "screen title"

        def compose(self):
            yield Header()

    class MyApp(App):
        TITLE = "app title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test() as pilot:
        app.screen.title = "new screen title"
        await pilot.pause()
        assert app.query_one("HeaderTitle").text == "new screen title"


async def test_app_title_reactive_does_not_update_title_when_screen_title_is_set():
    class MyScreen(Screen):
        TITLE = "screen title"

        def compose(self):
            yield Header()

    class MyApp(App):
        TITLE = "app title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test() as pilot:
        app.title = "new app title"
        await pilot.pause()
        assert app.query_one("HeaderTitle").text == "screen title"


async def test_screen_sub_title_none_is_ignored():
    class MyScreen(Screen):
        def compose(self):
            yield Header()

    class MyApp(App):
        SUB_TITLE = "app sub-title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test():
        assert app.query_one("HeaderTitle").sub_text == "app sub-title"


async def test_screen_sub_title_overrides_app_sub_title():
    class MyScreen(Screen):
        SUB_TITLE = "screen sub-title"

        def compose(self):
            yield Header()

    class MyApp(App):
        SUB_TITLE = "app sub-title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test():
        assert app.query_one("HeaderTitle").sub_text == "screen sub-title"


async def test_screen_sub_title_reactive_updates_sub_title():
    class MyScreen(Screen):
        SUB_TITLE = "screen sub-title"

        def compose(self):
            yield Header()

    class MyApp(App):
        SUB_TITLE = "app sub-title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test() as pilot:
        app.screen.sub_title = "new screen sub-title"
        await pilot.pause()
        assert app.query_one("HeaderTitle").sub_text == "new screen sub-title"


async def test_app_sub_title_reactive_does_not_update_sub_title_when_screen_sub_title_is_set():
    class MyScreen(Screen):
        SUB_TITLE = "screen sub-title"

        def compose(self):
            yield Header()

    class MyApp(App):
        SUB_TITLE = "app sub-title"

        def on_mount(self):
            self.push_screen(MyScreen())

    app = MyApp()
    async with app.run_test() as pilot:
        app.sub_title = "new app sub-title"
        await pilot.pause()
        assert app.query_one("HeaderTitle").sub_text == "screen sub-title"
