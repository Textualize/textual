from __future__ import annotations

import inspect
from pathlib import Path, PurePath
from typing import List, Union

from typing_extensions import TypeAlias

CSSPathType: TypeAlias = Union[
    str,
    PurePath,
    List[Union[str, PurePath]],
]
"""Valid ways of specifying paths to CSS files."""


class CSSPathError(Exception):
    """Raised when supplied CSS path(s) are invalid."""


def _css_path_type_as_list(css_path: CSSPathType) -> list[PurePath]:
    """Normalize the supplied CSSPathType into a list of paths.

    Args:
        css_path: Value to be normalized.

    Raises:
        CSSPathError: If the argument has the wrong format.

    Returns:
        A list of paths.
    """

    paths: list[PurePath] = []
    if isinstance(css_path, str):
        paths = [Path(css_path)]
    elif isinstance(css_path, PurePath):
        paths = [css_path]
    elif isinstance(css_path, list):
        paths = [Path(path) for path in css_path]
    else:
        raise CSSPathError("Expected a str, Path or list[str | Path] for the CSS_PATH.")

    return paths


def _make_path_object_relative(path: str | PurePath, obj: object) -> Path:
    """Convert the supplied path to a Path object that is relative to a given Python object.
    If the supplied path is absolute, it will simply be converted to a Path object.
    Used, for example, to return the path of a CSS file relative to a Textual App instance.

    Args:
        path: A path.
        obj: A Python object to resolve the path relative to.

    Returns:
        A resolved Path object, relative to obj
    """
    path = Path(path)

    # If the path supplied by the user is absolute, we can use it directly
    if path.is_absolute():
        return path

    # Otherwise (relative path), resolve it relative to obj...
    base_path = getattr(obj, "_BASE_PATH", None)
    if base_path is not None:
        subclass_path = Path(base_path)
    else:
        subclass_path = Path(inspect.getfile(obj.__class__))
    resolved_path = (subclass_path.parent / path).resolve()
    return resolved_path
