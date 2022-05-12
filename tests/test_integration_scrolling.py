from __future__ import annotations

import sys
from typing import Sequence, cast

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover


import pytest

from sandbox.vertical_container import VerticalContainer
from tests.utilities.test_app import AppTest
from textual.app import ComposeResult
from textual.geometry import Size
from textual.widget import Widget
from textual.widgets import Placeholder

SCREEN_SIZE = Size(100, 30)


@pytest.mark.asyncio
@pytest.mark.integration_test  # this is a slow test, we may want to skip them in some contexts
@pytest.mark.parametrize(
    (
        "screen_size",
        "placeholders_count",
        "scroll_to_placeholder_id",
        "scroll_to_animate",
        "waiting_duration",
        "last_screen_expected_placeholder_ids",
        "last_screen_expected_out_of_viewport_placeholder_ids",
    ),
    (
        [SCREEN_SIZE, 10, None, None, 0.01, (0, 1, 2, 3, 4), "others"],
        [SCREEN_SIZE, 10, "placeholder_3", False, 0.01, (0, 1, 2, 3, 4), "others"],
        [SCREEN_SIZE, 10, "placeholder_5", False, 0.01, (1, 2, 3, 4, 5), "others"],
        [SCREEN_SIZE, 10, "placeholder_7", False, 0.01, (3, 4, 5, 6, 7), "others"],
        [SCREEN_SIZE, 10, "placeholder_9", False, 0.01, (5, 6, 7, 8, 9), "others"],
        # N.B. Scroll duration is hard-coded to 0.2 in the `scroll_to_widget` method atm
        # Waiting for this duration should allow us to see the scroll finished:
        [SCREEN_SIZE, 10, "placeholder_9", True, 0.21, (5, 6, 7, 8, 9), "others"],
        # After having waited for approximately half of the scrolling duration, we should
        # see the middle Placeholders as we're scrolling towards the last of them.
        # The state of the screen at this "halfway there" timing looks to not be deterministic though,
        # depending on the environment - so let's only assert stuff for the middle placeholders
        # and the first and last ones, but without being too specific about the others:
        [SCREEN_SIZE, 10, "placeholder_9", True, 0.1, (6, 7, 8), (1, 2, 5, 9)],
    ),
)
async def test_scroll_to_widget(
    screen_size: Size,
    placeholders_count: int,
    scroll_to_animate: bool | None,
    scroll_to_placeholder_id: str | None,
    waiting_duration: float | None,
    last_screen_expected_placeholder_ids: Sequence[int],
    last_screen_expected_out_of_viewport_placeholder_ids: Sequence[int]
    | Literal["others"],
):
    class MyTestApp(AppTest):
        CSS = """
        Placeholder {
            height: 5; /* minimal height to see the name of a Placeholder */
        }
        """

        def compose(self) -> ComposeResult:
            placeholders = [
                Placeholder(id=f"placeholder_{i}", name=f"Placeholder #{i}")
                for i in range(placeholders_count)
            ]

            yield VerticalContainer(*placeholders, id="root")

    app = MyTestApp(size=screen_size, test_name="scroll_to_widget")

    async with app.in_running_state(waiting_duration_post_yield=waiting_duration or 0):
        if scroll_to_placeholder_id:
            target_widget_container = cast(Widget, app.query("#root").first())
            target_widget = cast(
                Widget, app.query(f"#{scroll_to_placeholder_id}").first()
            )
            target_widget_container.scroll_to_widget(
                target_widget, animate=scroll_to_animate
            )

    last_display_capture = app.last_display_capture

    placeholders_visibility_by_id = {
        id_: f"placeholder_{id_}" in last_display_capture
        for id_ in range(placeholders_count)
    }
    print(f"placeholders_visibility_by_id={placeholders_visibility_by_id}")
    # Let's start by checking placeholders that should be visible:
    for placeholder_id in last_screen_expected_placeholder_ids:
        assert (
            placeholders_visibility_by_id[placeholder_id] is True
        ), f"Placeholder '{placeholder_id}' should be visible but isn't"

    # Ok, now for placeholders that should *not* be visible:
    if last_screen_expected_out_of_viewport_placeholder_ids == "others":
        # We're simply going to check that all the placeholders that are not in
        # `last_screen_expected_placeholder_ids` are not on the screen:
        last_screen_expected_out_of_viewport_placeholder_ids = sorted(
            tuple(
                set(range(placeholders_count))
                - set(last_screen_expected_placeholder_ids)
            )
        )
    for placeholder_id in last_screen_expected_out_of_viewport_placeholder_ids:
        assert (
            placeholders_visibility_by_id[placeholder_id] is False
        ), f"Placeholder '{placeholder_id}' should not be visible but is"
