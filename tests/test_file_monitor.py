import os
from pathlib import Path

from textual.file_monitor import FileMonitor


def test_repr() -> None:
    file_monitor = FileMonitor([Path(".")], lambda: None)
    assert "FileMonitor" in repr(file_monitor)


def test_file_never_found():
    path = "doesnt_exist.tcss"
    file_monitor = FileMonitor([Path(path)], lambda: None)
    file_monitor.check()  # Ensuring no exceptions are raised.


async def test_file_deletion(tmp_path):
    """In some environments, a file can become temporarily unavailable during saving.

    This test ensures the FileMonitor is robust enough to handle a file temporarily being
    unavailable, and that it recovers when the file becomes available again.

    Regression test for: https://github.com/Textualize/textual/issues/3996
    """

    def make_file():
        path = tmp_path / "will_be_deleted.tcss"
        path.write_text("#foo { color: dodgerblue; }")
        return path

    callback_counter = 0

    def callback():
        nonlocal callback_counter
        callback_counter += 1

    path = make_file()
    file_monitor = FileMonitor([path], callback)

    # Ensure the file monitor survives after the file is gone
    await file_monitor()
    os.remove(path)

    # The file is now unavailable, but we don't crash here
    await file_monitor()
    await file_monitor()

    # Despite multiple checks, the file was only available for the first check,
    # and we only fire the callback while the file is available.
    assert callback_counter == 1

    # The file is made available again.
    make_file()

    # Since the file is available, the callback should fire when the FileMonitor is called
    await file_monitor()
    assert callback_counter == 2
