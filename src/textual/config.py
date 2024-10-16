from __future__ import annotations

import tomllib
from os import PathLike


class Config:
    def __init__(self, *paths: PathLike) -> None:
        self.paths = paths
        self._data: dict | None = None
        self._attempted_read = False

    def _read(self) -> dict:
        configs: list[dict] = []
        for path in self.paths:
            try:
                with open(path, "rb") as config_file:
                    configs.append(tomllib.load(config_file))
            except IOError:
                pass
        config = configs[0]
        for overlay_config in configs[1:]:
            if isinstance(overlay_config, dict):
                for key, value in overlay_config.items():
                    config[key] = value
        return config

    @property
    def data(self) -> dict:
        if not self._attempted_read:
            self._attempted_read = True
            self._data = self._read()
        if self._data is None:
            return {}
        return self._data

    def get(self, *keys: str, default: object = None) -> object:
        data = self.data
        for key in keys:
            if key not in data:
                return default
            data = data[key]
        return data


if __name__ == "__main__":
    config = Config("config.toml")
    from rich import print

    print(config.data)
