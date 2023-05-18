"""
Textual's Implementation of Pathlib, Powered by fsspec
"""

from os import getenv

try:
    import upath as _upath
    from upath import UPath as Path

    _upath.registry._registry.known_implementations[
        "github"
    ] = "textual._pathlib.GitHubPath"
except ImportError:
    from pathlib import Path

PathlibImplementation = Path


class GitHubPath(Path):
    """
    GitHubPath

    UPath implementation for GitHub to be compatible with
    the Directory Tree
    """

    def __new__(cls, *args, **kwargs) -> "GitHubPath":  # type: ignore[no-untyped-def]
        """
        Attempt to set the username and token from the environment
        """
        token = getenv("GITHUB_TOKEN")
        if token is not None:
            kwargs.update({"username": "Bearer", "token": token})
        github_path = super().__new__(cls, *args, **kwargs)
        return github_path

    @property
    def path(self) -> str:
        """
        Paths get their leading slash stripped
        """
        return super().path.strip("/")

    @property
    def name(self) -> str:
        """
        Override the name for top level repo
        """
        if self.path == "":
            org = self._accessor._fs.org
            repo = self._accessor._fs.repo
            sha = self._accessor._fs.storage_options["sha"]
            github_name = f"{org}:{repo}@{sha}"
            return github_name
        else:
            return super().name
