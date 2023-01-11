from textual.app import App


async def test_suspend() -> None:
    async with App().run_test() as pilot:
        with pilot.app.suspend():
            print("hi")
