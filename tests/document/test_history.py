import pytest

from textual.document._history import EditHistory

BATCH_TIMER = 3.0
BATCH_MAX_CHARACTERS = 8


@pytest.fixture
def history():
    return EditHistory(
        checkpoint_timer=BATCH_TIMER,
        checkpoint_max_characters=BATCH_MAX_CHARACTERS,
    )


def test_append(history):
    pass  # TODO


def test_reset(history):
    pass  # TODO
