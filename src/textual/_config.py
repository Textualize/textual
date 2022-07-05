"""Resolve configuration files, parse them, and merge them based
on priorities. This is a completely standalone class, unaware of Textual
concepts like “widgets” etc.
"""
from __future__ import annotations

from pathlib import PurePath
from typing import Iterable, Collection

import tomli


class Config:
    def __init__(
        self,
        namespace: str,
        default_config_path: str | PurePath,
        user_config_paths: Iterable[str | PurePath] = None,
    ):
        """Manages access to configuration for the Textual application.
        Textual applications may ship with a `textual.toml` file containing default configuration values.
        We refer to these as "packaged defaults", and they may only contain relating to the Textual app.
        Users may have a `textual.toml` file on their system which may override these default configuration values.
        Instantiating this class does not result in disk access. Disk access only occurs when the `resolve` method is
        called.

        Args:
            namespace (str): The namespace of this application. Used to filter out irrelevant config.
            default_config_path (str | PurePath): The path to the default config for this app. This type of config is
                handled separately from user configuration as it's more restrictive. For example, you cannot bundle
                a config file with your application that alters global configuration.
            user_config_paths (Iterable[str | PurePath]): The paths to the config files to load. If items appear
                multiple times in the supplied config files and have matching namespaces, the last occurrence will be
                used.
        """
        # TODO: If namespace is None, it may be contained within the packaged defaults
        self.namespace = namespace
        self.default_config_path = default_config_path
        self.user_config_paths = user_config_paths
        self._raw_merged_config = {}

    def resolve(self) -> Config:
        """Resolve configuration"""
        default_config = self._read_and_filter_default_config_file()
        user_configs = self._read_and_filter_user_config_files()
        self._raw_merged_config = self._merge_raw_config_dicts(
            default_config, user_configs
        )

        return self

    def _read_and_filter_default_config_file(self) -> dict[str, object]:
        """Read the default config file (that is, the config file that is packaged alongside this application
        and defines the default values for configuration keys). Also filters out any sections that are not considered
        relevant for a default config file. For example, sections pertaining to other applications or global sections
        should be removed."""
        try:
            with open(self.default_config_path, "rb") as default_config_file:
                default_config = tomli.load(default_config_file)
        except OSError:
            return {}

        default_config = _filter_keys(
            default_config, keys_to_keep=self._default_config_headers
        )
        return default_config

    def _read_and_filter_user_config_files(self) -> list[dict[str, object]]:
        """Read the config files on the users machine. Keys found in here inside matching namespaces will ultimately
        override corresponding keys inside the default config files."""
        user_configs = []
        for path in self.user_config_paths:
            with open(path, "rb") as user_config_file:
                user_config = tomli.load(user_config_file)
            user_config = _filter_keys(
                user_config, keys_to_keep=self._user_config_headers
            )
            user_configs.append(user_config)
        return user_configs

    @property
    def _default_config_headers(self) -> frozenset[str]:
        """Get a frozenset of strings containing the names of the section headers relevant to the default config that
        is bundled with this application (*not* for user config)."""
        namespace = self.namespace
        return frozenset((f"{namespace}",))

    @property
    def _user_config_headers(self) -> frozenset[str]:
        return frozenset(
            (
                "meta",
                "textual",
                *self._default_config_headers,
            )
        )

    def _merge_raw_config_dicts(
        self,
        default_configs: dict[str, object],
        user_configs: Iterable[dict[str, object]],
    ) -> dict[str, object]:
        """Merge user config dictionaries into the default config dictionary"""
        merged = default_configs.copy()

        for user_config in user_configs:
            # Update the individual sections that should be merged
            merged_namespace = merged.get(self.namespace, {})
            user_config_namespace = user_config.get(self.namespace, {})

            # By "sandbox" we refer to `APP_NAME.config` section
            merged_config_sandbox = merged_namespace.get("config", {})
            user_config_sandbox = user_config_namespace.get("config", {})
            merged[self.namespace] = {
                **merged_namespace,
                **user_config_namespace,
                "config": {**merged_config_sandbox, **user_config_sandbox},
            }

            # Merge the `meta` section
            merged_meta = merged.get("meta", {})
            merged_meta.update(user_config.get("meta", {}))
            merged["meta"] = merged_meta

            # Merge the `textual` section
            merged_textual = merged.get("textual", {})
            merged_textual.update(user_config.get("textual", {}))
            merged["textual"] = merged_textual

            # Merge the `textual.devtools` section
            merged_devtools = merged.get("textual", {}).get("devtools", {})
            merged_devtools.update(user_config.get("textual", {}).get("devtools", {}))
            merged["textual"]["devtools"] = merged_devtools

        return merged


def _filter_keys(
    dictionary: dict[str, object], keys_to_keep: Collection[str]
) -> dict[str, object]:
    """Removes sections that aren't relevant, for example
    sections defining configuration for other Textual apps.'"""
    return {key: value for key, value in dictionary.items() if key in keys_to_keep}
