from __future__ import annotations

from asyncio import Queue
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Iterable, Iterator

from rich.style import Style
from rich.text import Text, TextType

from .. import work
from ..message import Message
from ..reactive import var
from ..worker import Worker, WorkerCancelled, WorkerFailed, get_current_worker
from ._tree import TOGGLE_STYLE, Tree, TreeNode


@dataclass
class DirEntry:
    """Attaches directory information to a node."""

    path: Path
    """The path of the directory entry."""
    loaded: bool = False
    """Has this been loaded?"""


class DirectoryTree(Tree[DirEntry]):
    """A Tree widget that presents files and directories."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "directory-tree--extension",
        "directory-tree--file",
        "directory-tree--folder",
        "directory-tree--hidden",
    }
    """
    | Class | Description |
    | :- | :- |
    | `directory-tree--extension` | Target the extension of a file name. |
    | `directory-tree--file` | Target files in the directory structure. |
    | `directory-tree--folder` | Target folders in the directory structure. |
    | `directory-tree--hidden` | Target hidden items in the directory structure. |

    See also the [component classes for `Tree`][textual.widgets.Tree.COMPONENT_CLASSES].
    """

    DEFAULT_CSS = """
    DirectoryTree > .directory-tree--folder {
        text-style: bold;
    }

    DirectoryTree > .directory-tree--extension {
        text-style: italic;
    }

    DirectoryTree > .directory-tree--hidden {
        color: $text 50%;
    }
    """

    class FileSelected(Message, bubble=True):
        """Posted when a file is selected.

        Can be handled using `on_directory_tree_file_selected` in a subclass of
        `DirectoryTree` or in a parent widget in the DOM.
        """

        def __init__(
            self, tree: DirectoryTree, node: TreeNode[DirEntry], path: Path
        ) -> None:
            """Initialise the FileSelected object.

            Args:
                node: The tree node for the file that was selected.
                path: The path of the file that was selected.
            """
            super().__init__()
            self.tree: DirectoryTree = tree
            """The `DirectoryTree` that had a file selected."""
            self.node: TreeNode[DirEntry] = node
            """The tree node of the file that was selected."""
            self.path: Path = path
            """The path of the file that was selected."""

        @property
        def control(self) -> DirectoryTree:
            """The `DirectoryTree` that had a file selected.

            This is an alias for [`FileSelected.tree`][textual.widgets.DirectoryTree.FileSelected.tree]
            which is used by the [`on`][textual.on] decorator.
            """
            return self.tree

    path: var[str | Path] = var["str | Path"](Path("."), init=False, always_update=True)
    """The path that is the root of the directory tree.

    Note:
        This can be set to either a `str` or a `pathlib.Path` object, but
        the value will always be a `pathlib.Path` object.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the directory tree.

        Args:
            path: Path to directory.
            name: The name of the widget, or None for no name.
            id: The ID of the widget in the DOM, or None for no ID.
            classes: A space-separated list of classes, or None for no classes.
            disabled: Whether the directory tree is disabled or not.
        """
        self._load_queue: Queue[TreeNode[DirEntry]] = Queue()
        super().__init__(
            str(path),
            data=DirEntry(Path(path)),
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.path = path

    def _add_to_load_queue(self, node: TreeNode[DirEntry]) -> None:
        """Add the given node to the load queue.

        Args:
            node: The node to add to the load queue.
        """
        assert node.data is not None
        node.data.loaded = True
        self._load_queue.put_nowait(node)

    def reload(self) -> None:
        """Reload the `DirectoryTree` contents."""
        self.reset(str(self.path), DirEntry(Path(self.path)))
        # Orphan the old queue...
        self._load_queue = Queue()
        # ...and replace the old load with a new one.
        self._loader()
        # We have a fresh queue, we have a fresh loader, get the fresh root
        # loading up.
        self._add_to_load_queue(self.root)

    def validate_path(self, path: str | Path) -> Path:
        """Ensure that the path is of the `Path` type.

        Args:
            path: The path to validate.

        Returns:
            The validated Path value.

        Note:
            The result will always be a Python `Path` object, regardless of
            the value given.
        """
        return Path(path)

    def watch_path(self) -> None:
        """Watch for changes to the `path` of the directory tree.

        If the path is changed the directory tree will be repopulated using
        the new value as the root.
        """
        self.reload()

    def process_label(self, label: TextType) -> Text:
        """Process a str or Text into a label. Maybe overridden in a subclass to modify how labels are rendered.

        Args:
            label: Label.

        Returns:
            A Rich Text object.
        """
        if isinstance(label, str):
            text_label = Text(label)
        else:
            text_label = label
        first_line = text_label.split()[0]
        return first_line

    def render_label(
        self, node: TreeNode[DirEntry], base_style: Style, style: Style
    ) -> Text:
        """Render a label for the given node.

        Args:
            node: A tree node.
            base_style: The base style of the widget.
            style: The additional style for the label.

        Returns:
            A Rich Text object containing the label.
        """
        node_label = node._label.copy()
        node_label.stylize(style)

        if node._allow_expand:
            prefix = ("📂 " if node.is_expanded else "📁 ", base_style + TOGGLE_STYLE)
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--folder", partial=True)
            )
        else:
            prefix = (
                "📄 ",
                base_style,
            )
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--file", partial=True),
            )
            node_label.highlight_regex(
                r"\..+$",
                self.get_component_rich_style(
                    "directory-tree--extension", partial=True
                ),
            )

        if node_label.plain.startswith("."):
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--hidden")
            )

        text = Text.assemble(prefix, node_label)
        return text

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter the paths before adding them to the tree.

        Args:
            paths: The paths to be filtered.

        Returns:
            The filtered paths.

        By default this method returns all of the paths provided. To create
        a filtered `DirectoryTree` inherit from it and implement your own
        version of this method.
        """
        return paths

    @staticmethod
    def _safe_is_dir(path: Path) -> bool:
        """Safely check if a path is a directory.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is for a directory, `False` if not.
        """
        try:
            return path.is_dir()
        except PermissionError:
            # We may or may not have been looking at a directory, but we
            # don't have the rights or permissions to even know that. Best
            # we can do, short of letting the error blow up, is assume it's
            # not a directory. A possible improvement in here could be to
            # have a third state which is "unknown", and reflect that in the
            # tree.
            return False

    def _populate_node(self, node: TreeNode[DirEntry], content: Iterable[Path]) -> None:
        """Populate the given tree node with the given directory content.

        Args:
            node: The Tree node to populate.
            content: The collection of `Path` objects to populate the node with.
        """
        for path in content:
            node.add(
                path.name,
                data=DirEntry(path),
                allow_expand=self._safe_is_dir(path),
            )
        node.expand()

    def _directory_content(self, location: Path, worker: Worker) -> Iterator[Path]:
        """Load the content of a given directory.

        Args:
            location: The location to load from.
            worker: The worker that the loading is taking place in.

        Yields:
            Path: An entry within the location.
        """
        try:
            for entry in location.iterdir():
                if worker.is_cancelled:
                    break
                yield entry
        except PermissionError:
            pass

    @work
    def _load_directory(self, node: TreeNode[DirEntry]) -> list[Path]:
        """Load the directory contents for a given node.

        Args:
            node: The node to load the directory contents for.

        Returns:
            The list of entries within the directory associated with the node.
        """
        assert node.data is not None
        return sorted(
            self.filter_paths(
                self._directory_content(node.data.path, get_current_worker())
            ),
            key=lambda path: (not self._safe_is_dir(path), path.name.lower()),
        )

    @work(exclusive=True)
    async def _loader(self) -> None:
        """Background loading queue processor."""
        worker = get_current_worker()
        while not worker.is_cancelled:
            # Get the next node that needs loading off the queue. Note that
            # this blocks if the queue is empty.
            node = await self._load_queue.get()
            content: list[Path] = []
            try:
                # Spin up a short-lived thread that will load the content of
                # the directory associated with that node.
                content = await self._load_directory(node).wait()
            except WorkerCancelled:
                # The worker was cancelled, that would suggest we're all
                # done here and we should get out of the loader in general.
                break
            except WorkerFailed:
                # This particular worker failed to start. We don't know the
                # reason so let's no-op that (for now anyway).
                pass
            else:
                # We're still here and we have directory content, get it into
                # the tree.
                if content:
                    self._populate_node(node, content)
            # Mark this iteration as done.
            self._load_queue.task_done()

    def _on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if self._safe_is_dir(dir_entry.path):
            if not dir_entry.loaded:
                self._add_to_load_queue(event.node)
        else:
            self.post_message(self.FileSelected(self, event.node, dir_entry.path))

    def _on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if not self._safe_is_dir(dir_entry.path):
            self.post_message(self.FileSelected(self, event.node, dir_entry.path))
