from textual.demo.demo_app import DemoApp


async def test_demo():
    """Test the demo runs."""
    # Test he demo can at least run.
    # This exists mainly to catch screw-ups that might effect only certain Python versions.
    app = DemoApp()
    async with app.run_test() as pilot:
        await pilot.pause(0.1)
