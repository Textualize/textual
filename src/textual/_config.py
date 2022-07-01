"""Resolve configuration files, parse them, and merge them based
on priorities. This is a completely standalone class, unaware of Textual
concepts like “widgets” etc.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import tomli

_CONFIG_FILE_NAME = "textual.toml"


class Config:
    def __init__(self):
        self._config = {}

    def resolve(self) -> None:
        """Resolve configuration"""
        paths = self._find_config_file_paths()
        tomls = []
        for path in paths:
            with open(path, "rb") as config_file:
                toml = tomli.load(config_file)
                toml = self._remove_irrelevant_sections(toml)
                tomls.append(toml)

    def _get_relevant_section_headers(self) -> list[str]:
        """Get a list of strings containing the names of the section headers relevant to this application"""

    def _remove_irrelevant_sections(self, toml: dict[str, object]) -> dict[str, object]:
        """Removes sections from the TOML that are not relevant to this app, for example
        sections defining configuration for other Textual apps."""

    def _merge_config_dicts(self, dicts: Iterable[dict]) -> dict[str, object]:
        """Merge an Iterable of dicts into one. In the event that keys appear in multiple dicts,
        the last occurrence of that key will be used. There's special handling for "keybinds", since
        if a user defines some of their own keybinds, we don't wish to remove all of the keybinds that
        were defined as defaults.
        """

        # TODO: Handle "keybinds" merging correctly

    def _read_config_file(self, path: Path) -> dict[str, object]:
        """Parse the configuration file at the given Path into a dict

        Args:
            path (Path): The Path of the config file.

        Returns:
            dict[str, object]: The configuration file as a dictionary.
        """

    def _find_config_file_paths(self) -> Iterable[Path]:
        """Find the paths of config files on the system that will be used to resolve
        the final config set.

        Returns:
            Iterable[Path]: Yields the Paths of config files that have been discovered
                in reverse order of precedence. User config which takes priority over
                config distributed alongside an application will be the final yielded
                value.
        """
