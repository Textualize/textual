"""Resolve configuration files, parse them, and merge them based
on priorities. This is a completely standalone class, unaware of Textual
concepts like “widgets” etc.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

_CONFIG_FILE_NAME = "textual.toml"


class Config:
    def _read_config_file(self, path: Path) -> dict[str, object]:
        """Parse the configuration file into a"""

    def _find_config_file_paths(self) -> Iterable[Path]:
        """Find the paths of config files on the system that will be used to resolve
        the final config set.

        Returns:
            Iterable[Path]: Yields the Paths of config files that have been discovered
                in reverse order of precedence. User config which takes priority over
                config distributed alongside an application will be the final yielded
                value.
        """
