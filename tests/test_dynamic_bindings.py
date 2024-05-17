from __future__ import annotations

from textual.app import App


async def test_dynamic_disabled():
    """Check we can dynamically disable bindings."""
    actions = []

    class DynamicApp(App):
        BINDINGS = [
            ("a", "register('a')", "A"),
            ("b", "register('b')", "B"),
            ("c", "register('c')", "B"),
        ]

        def action_register(self, key: str) -> None:
            actions.append(key)

        def check_action(
            self, action: str, parameters: tuple[object, ...]
        ) -> bool | None:
            if action == "register":
                if parameters == ("b",):
                    return False
                if parameters == ("c",):
                    return None
            return True

    app = DynamicApp()
    async with app.run_test() as pilot:
        await pilot.press("a", "b", "c")
        assert actions == ["a"]
