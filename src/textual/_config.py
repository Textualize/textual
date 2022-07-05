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
        self.namespace = namespace
        self._default_config_path = default_config_path
        self._user_config_paths = user_config_paths
        self._raw_merged_config = {}

        # Textual default config values which can be overridden by resolved config.

        # TODO: Apply environment variables first before resolving configuration files
        self.dark = False
        self.debug = False

    def __getitem__(self, key: str) -> object:
        """Retrieve a config value for this application for a given key."""
        return self._raw_merged_config.get(self.namespace)[key]

    @property
    def raw(self) -> dict[str, object]:
        return self._raw_merged_config.get(self.namespace)

    @property
    def meta(self) -> dict[str, object]:
        return self._raw_merged_config.get("meta")

    def resolve(self) -> Config:
        """Resolve configuration"""
        default_config = self._read_and_filter_default_config_file()
        user_configs = self._read_and_filter_user_config_files()

        raw_merged_config = self._merge_raw_config_dicts(default_config, user_configs)
        self._raw_merged_config = self._prioritise_user_config(raw_merged_config)
        self._fill_attributes(self._raw_merged_config)

        return self

    def _prioritise_user_config(
        self, raw_merged_config: dict[str, object]
    ) -> dict[str, object]:
        """Given a merged/combined settings file which may have 'global' config and app level config, ensure
        the config for the curren Textual app takes precedence. After this operation, the [textual] section
        will be merged into the [APP_NAME] section."""
        config = raw_merged_config.copy()

        global_config = config.pop("textual", {})
        namespaced_config = config.get(self.namespace, {})

        global_devtools_config = global_config.pop("devtools")
        namespaced_devtools_config = namespaced_config.get("devtools")

        config = {
            "meta": config.get("meta", {}),
            self.namespace: {
                **global_config,
                **namespaced_config,
                "devtools": {**global_devtools_config, **namespaced_devtools_config},
            },
        }

        return config

    def _read_and_filter_default_config_file(self) -> dict[str, object]:
        """Read the default config file (that is, the config file that is packaged alongside this application
        and defines the default values for configuration keys). Also filters out any sections that are not considered
        relevant for a default config file. For example, sections pertaining to other applications or global sections
        should be removed."""
        try:
            with open(self._default_config_path, "rb") as default_config_file:
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
        for path in self._user_config_paths:
            try:
                with open(path, "rb") as user_config_file:
                    user_config = tomli.load(user_config_file)
            except OSError:
                continue

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
        """Get a frozenset of strings containing the names of the section headers relevant to the user config that
        is bundled with this application."""
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

            # Merge the `meta` section
            merged_meta = merged.get("meta", {})
            merged_meta.update(user_config.get("meta", {}))

            # Merge the `textual` section
            merged_textual = merged.get("textual", {})
            merged_textual.update(user_config.get("textual", {}))

            # Merge the `textual.devtools` section
            merged_devtools = merged.get("textual", {}).get("devtools", {})
            merged_devtools.update(user_config.get("textual", {}).get("devtools", {}))

            # Merge the `APP_NAME.devtools` sections
            merged_app_devtools = merged_namespace.get("devtools", {})
            merged_app_devtools.update(user_config_namespace.get("devtools", {}))

            # Merge the new settings with the previous iteration
            merged = {
                "meta": merged_meta,
                "textual": {
                    **merged_textual,
                    "devtools": merged_devtools,
                },
                self.namespace: {
                    **merged_namespace,
                    **user_config_namespace,
                    "config": {**merged_config_sandbox, **user_config_sandbox},
                    "devtools": merged_app_devtools,
                },
            }

        return merged

    def _fill_attributes(self, raw_merged_config: dict[str, object]) -> None:
        """Override the Textual default configuration values with the values from a dictionary"""
        # TODO: At this point we may consider validation. There's none here for now though.
        #  .. May also consider having a separate object which we can convert this dict into easily,
        #  that allows for validation via pydantic, with this class providing "transparent" read-only
        #  access to it.


def _filter_keys(
    dictionary: dict[str, object], keys_to_keep: Collection[str]
) -> dict[str, object]:
    """Removes items from a dictionary where the key isn't contained in `keys_to_keep`"""
    return {key: value for key, value in dictionary.items() if key in keys_to_keep}
