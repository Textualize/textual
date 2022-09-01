import inspect
import sys
from pathlib import Path


def _make_path_object_relative(path: str, obj: object) -> Path:
    """Given a path as a string convert it, if possible, to a Path that is relative to a given Python object.
    If the path string is already absolute, it will simply be converted to a Path object.
    Used, for example, to return the path of a CSS file relative to a Textual App instance.

    Args:
        path (str): A path, as a string.
        obj (object): A Python object.

    Returns:
        Path: A resolved Path object, relative to obj
    """
    path = Path(path)

    # If the path supplied by the user is absolute, we can use it directly
    if path.is_absolute():
        return path

    # Otherwise (relative path), resolve it relative to obj...
    subclass_module = sys.modules[obj.__module__]
    subclass_path = Path(inspect.getfile(subclass_module))
    resolved_path = (subclass_path.parent / path).resolve()
    return resolved_path
