from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from typing import ClassVar, Iterable, Iterator

from rich.style import Style
from rich.text import Text, TextType
from typing_extensions import Final

from .. import work
from ..events import Mount
from ..message import Message
from ..reactive import var
from ..worker import get_current_worker
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

    path: var[str | Path] = var["str | Path"](Path("."), init=False)
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
        super().__init__(
            str(path),
            data=DirEntry(Path(path)),
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._waiting_load_jobs: Queue[TreeNode[DirEntry]] = Queue()
        self._running_load_jobs: set[int] = set()
        self.path = path

    def reload(self) -> None:
        """Reload the `DirectoryTree` contents."""
        self.reset(str(self.path), DirEntry(Path(self.path)))
        self._add_load_job(self.root)

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

    def _directory_content(self, directory: Path) -> Iterator[Path]:
        """Get the entries within a given directory.

        Args:
            directory: The directory to get the content of.

        Returns:
            An iterator of `Path` objects.
        """
        # TODO: Not like this. Oh so very not like this. This is here to
        # slow things down on purpose, to emulate loading directory
        # information from a slow source.
        #
        # REMOVE BEFORE FLIGHT!
        import time

        worker = get_current_worker()
        for entry in directory.iterdir():
            if worker.is_cancelled:
                return
            yield entry
            time.sleep(0.05)

    def _populate_node(
        self, node: TreeNode[DirEntry], directory: Iterable[Path]
    ) -> None:
        """Populate the given node with the contents of a directory.

        Args:
            node: The node to populate.
            directory: The directory contents to populate it with.
        """
        for path in directory:
            node.add(
                path.name,
                data=DirEntry(path),
                allow_expand=path.is_dir(),
            )
        node.expand()

    @dataclass
    class _LoadFinished(Message):
        """Internal message to mark when a load of a node is finished."""

        node: TreeNode[DirEntry]
        """The node that has finished loading."""

    @work
    def _load_directory(self, node: TreeNode[DirEntry]) -> None:
        """Load the directory contents for a given node.

        Args:
            node: The node to load the directory contents for.
        """
        assert node.data is not None
        node.data.loaded = True
        # TODO: Perhaps move this out of here and...
        self.app.call_from_thread(
            self._populate_node,
            node,
            sorted(
                self.filter_paths(self._directory_content(node.data.path)),
                key=lambda path: (not path.is_dir(), path.name.lower()),
            ),
        )
        # TODO: ...attach it to this and have the receiver update the tree?
        self.post_message(self._LoadFinished(node))

    _MAX_CONCURRENT_JOBS: Final[int] = 5
    """The maximum number of load jobs to run at the same time."""

    def _process_load_jobs(self) -> None:
        """Process the incoming load request queue."""
        # While we still have spare capacity...
        while len(self._running_load_jobs) <= self._MAX_CONCURRENT_JOBS:
            try:
                # ...pull a load job off the queue.
                new_job = self._waiting_load_jobs.get(block=False)
            except Empty:
                # Queue is empty; our work here is done.
                return
            # At this point we've got a new directory load job; add it to
            # the collection of running jobs and kick off the load, but only
            # if there isn't already a job for it.
            if not new_job.id in self._running_load_jobs:
                self._running_load_jobs.add(new_job.id)
                self._load_directory(new_job)

    def _on_directory_tree__load_finished(
        self, event: DirectoryTree._LoadFinished
    ) -> None:
        """Act on a signal that a node has finished loading.

        Args:
            event: The event to process.
        """
        event.stop()
        self._running_load_jobs.remove(event.node.id)
        self._process_load_jobs()

    def _add_load_job(self, node: TreeNode[DirEntry]) -> None:
        """Add a directory loading job to the queue.

        Args:
            node: The node that needs loading.
        """
        self._waiting_load_jobs.put(node)
        self._process_load_jobs()

    def _on_mount(self, _: Mount) -> None:
        self._add_load_job(self.root)

    def _on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if dir_entry.path.is_dir():
            if not dir_entry.loaded:
                self._add_load_job(event.node)
        else:
            self.post_message(self.FileSelected(self, event.node, dir_entry.path))

    def _on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if not dir_entry.path.is_dir():
            self.post_message(self.FileSelected(self, event.node, dir_entry.path))
