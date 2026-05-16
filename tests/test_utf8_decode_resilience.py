"""Regression test for https://github.com/Textualize/textual/issues/6456

Verify that the UTF-8 incremental decoders used in drivers are configured
with ``errors="replace"`` so that invalid byte sequences produce U+FFFD
instead of raising ``UnicodeDecodeError`` and crashing the input thread.

This test inspects the driver source code to ensure the fix is in place.
Without errors="replace", invalid UTF-8 input would crash the input thread.
"""

import re
from pathlib import Path


def _get_driver_files() -> dict[str, Path]:
    """Get the paths to the three drivers that were modified."""
    drivers_dir = Path(__file__).parent.parent / "src" / "textual" / "drivers"
    return {
        "linux_driver": drivers_dir / "linux_driver.py",
        "linux_inline_driver": drivers_dir / "linux_inline_driver.py",
        "web_driver": drivers_dir / "web_driver.py",
    }


def _check_driver_decoder_config(driver_path: Path) -> bool:
    """Check if driver uses getincrementaldecoder with errors='replace'."""
    if not driver_path.exists():
        raise FileNotFoundError(f"Driver file not found: {driver_path}")
    
    source = driver_path.read_text(encoding="utf-8")
    
    # Look for the pattern: getincrementaldecoder("utf-8")(errors="replace")
    # This regex matches the decoder instantiation with the replace error handler
    pattern = r'getincrementaldecoder\s*\(\s*["\']utf-8["\']\s*\)\s*\(\s*errors\s*=\s*["\']replace["\']\s*\)'
    
    return bool(re.search(pattern, source))


def test_linux_driver_uses_replace_errors() -> None:
    """Linux driver must use errors='replace' for UTF-8 decoder."""
    drivers = _get_driver_files()
    assert _check_driver_decoder_config(drivers["linux_driver"]), (
        "linux_driver.py must use getincrementaldecoder('utf-8')(errors='replace'). "
        "Without this, invalid UTF-8 bytes will crash the input thread."
    )


def test_linux_inline_driver_uses_replace_errors() -> None:
    """Linux inline driver must use errors='replace' for UTF-8 decoder."""
    drivers = _get_driver_files()
    assert _check_driver_decoder_config(drivers["linux_inline_driver"]), (
        "linux_inline_driver.py must use getincrementaldecoder('utf-8')(errors='replace'). "
        "Without this, invalid UTF-8 bytes will crash the input thread."
    )


def test_web_driver_uses_replace_errors() -> None:
    """Web driver must use errors='replace' for UTF-8 decoder."""
    drivers = _get_driver_files()
    assert _check_driver_decoder_config(drivers["web_driver"]), (
        "web_driver.py must use getincrementaldecoder('utf-8')(errors='replace'). "
        "Without this, invalid UTF-8 bytes will crash the input thread."
    )
