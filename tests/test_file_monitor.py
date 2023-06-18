from pathlib import Path

from textual.file_monitor import FileMonitor


def test_repr() -> None:
    file_monitor = FileMonitor([Path(".")], lambda: None)
    assert "FileMonitor" in repr(file_monitor)
