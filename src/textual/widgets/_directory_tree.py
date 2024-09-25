from __future__ import annotations

from asyncio import Queue
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Iterator

from rich.style import Style
from rich.text import Text, TextType

from textual import work
from textual.await_complete import AwaitComplete
from textual.message import Message
from textual.reactive import var
from textual.widgets._tree import TOGGLE_STYLE, Tree, TreeNode
from textual.worker import Worker, WorkerCancelled, WorkerFailed, get_current_worker

if TYPE_CHECKING:
    from typing_extensions import Self


@dataclass
class DirEntry:
    """Attaches directory information to a [`DirectoryTree`][textual.widgets.DirectoryTree] node."""

    path: Path
    """The path of the directory entry."""
    loaded: bool = False
    """Has this been loaded?"""


class DirectoryTree(Tree[DirEntry]):
    """A Tree widget that presents files and directories."""

    ICON_NODE_EXPANDED = "📂 "
    ICON_NODE = "📁 "
    ICON_FILE = "📄 "
    """Unicode 'icon' to represent a file."""

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
    DirectoryTree {
        
        & > .directory-tree--folder {
            text-style: bold;
        }

        & > .directory-tree--extension {
            text-style: italic;
        }

        & > .directory-tree--hidden {
            color: $text 50%;
        }

        &:ansi {
        
            & > .tree--guides {
               color: transparent;              
            }
        
            & > .directory-tree--folder {
                text-style: bold;
            }

            & > .directory-tree--extension {
                text-style: italic;
            }

            & > .directory-tree--hidden {
                color: ansi_default;
                text-style: dim;
            }
        }

    }

    """

    PATH: Callable[[str | Path], Path] = Path
    """Callable that returns a fresh path object."""

    class FileSelected(Message):
        """Posted when a file is selected.

        Can be handled using `on_directory_tree_file_selected` in a subclass of
        `DirectoryTree` or in a parent widget in the DOM.
        """

        def __init__(self, node: TreeNode[DirEntry], path: Path) -> None:
            """Initialise the FileSelected object.

            Args:
                node: The tree node for the file that was selected.
                path: The path of the file that was selected.
            """
            super().__init__()
            self.node: TreeNode[DirEntry] = node
            """The tree node of the file that was selected."""
            self.path: Path = path
            """The path of the file that was selected."""

        @property
        def control(self) -> Tree[DirEntry]:
            """The `Tree` that had a file selected."""
            return self.node.tree

    class DirectorySelected(Message):
        """Posted when a directory is selected.

        Can be handled using `on_directory_tree_directory_selected` in a
        subclass of `DirectoryTree` or in a parent widget in the DOM.
        """

        def __init__(self, node: TreeNode[DirEntry], path: Path) -> None:
            """Initialise the DirectorySelected object.

            Args:
                node: The tree node for the directory that was selected.
                path: The path of the directory that was selected.
            """
            super().__init__()
            self.node: TreeNode[DirEntry] = node
            """The tree node of the directory that was selected."""
            self.path: Path = path
            """The path of the directory that was selected."""

        @property
        def control(self) -> Tree[DirEntry]:
            """The `Tree` that had a directory selected."""
            return self.node.tree

    path: var[str | Path] = var["str | Path"](PATH("."), init=False, always_update=True)
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
            data=DirEntry(self.PATH(path)),
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.path = path

    def _add_to_load_queue(self, node: TreeNode[DirEntry]) -> AwaitComplete:
        """Add the given node to the load queue.

        The return value can optionally be awaited until the queue is empty.

        Args:
            node: The node to add to the load queue.

        Returns:
            An optionally awaitable object that can be awaited until the
                load queue has finished processing.
        """
        assert node.data is not None
        if not node.data.loaded:
            node.data.loaded = True
            self._load_queue.put_nowait(node)

        return AwaitComplete(self._load_queue.join())

    def reload(self) -> AwaitComplete:
        """Reload the `DirectoryTree` contents.

        Returns:
            An optionally awaitable that ensures the tree has finished reloading.
        """
        # Orphan the old queue...
        self._load_queue = Queue()
        # ... reset the root node ...
        processed = self.reload_node(self.root)
        # ...and replace the old load with a new one.
        self._loader()
        return processed

    def clear_node(self, node: TreeNode[DirEntry]) -> Self:
        """Clear all nodes under the given node.

        Returns:
            The `Tree` instance.
        """
        self._clear_line_cache()
        node.remove_children()
        self._updates += 1
        self.refresh()
        return self

    def reset_node(
        self, node: TreeNode[DirEntry], label: TextType, data: DirEntry | None = None
    ) -> Self:
        """Clear the subtree and reset the given node.

        Args:
            node: The node to reset.
            label: The label for the node.
            data: Optional data for the node.

        Returns:
            The `Tree` instance.
        """
        self.clear_node(node)
        node.label = label
        node.data = data
        return self

    async def _reload(self, node: TreeNode[DirEntry]) -> None:
        """Reloads the subtree rooted at the given node while preserving state.

        After reloading the subtree, nodes that were expanded and still exist
        will remain expanded and the highlighted node will be preserved, if it
        still exists. If it doesn't, highlighting goes up to the first parent
        directory that still exists.

        Args:
            node: The root of the subtree to reload.
        """
        async with self.lock:
            # Track nodes that were expanded before reloading.
            currently_open: set[Path] = set()
            to_check: list[TreeNode[DirEntry]] = [node]
            while to_check:
                checking = to_check.pop()
                if checking.allow_expand and checking.is_expanded:
                    if checking.data:
                        currently_open.add(checking.data.path)
                    to_check.extend(checking.children)

            # Track node that was highlighted before reloading.
            highlighted_path: None | Path = None
            if self.cursor_line > -1:
                highlighted_node = self.get_node_at_line(self.cursor_line)
                if highlighted_node is not None and highlighted_node.data is not None:
                    highlighted_path = highlighted_node.data.path

            if node.data is not None:
                self.reset_node(
                    node, str(node.data.path.name), DirEntry(self.PATH(node.data.path))
                )

            # Reopen nodes that were expanded and still exist.
            to_reopen = [node]
            while to_reopen:
                reopening = to_reopen.pop()
                if not reopening.data:
                    continue
                if reopening.allow_expand and (
                    reopening.data.path in currently_open or reopening == node
                ):
                    try:
                        content = await self._load_directory(reopening).wait()
                    except (WorkerCancelled, WorkerFailed):
                        continue
                    reopening.data.loaded = True
                    self._populate_node(reopening, content)
                    to_reopen.extend(reopening.children)
                    reopening.expand()

            if highlighted_path is None:
                return

            # Restore the highlighted path and consider the parents as fallbacks.
            looking = [node]
            highlight_candidates = set(highlighted_path.parents)
            highlight_candidates.add(highlighted_path)
            best_found: None | TreeNode[DirEntry] = None
            while looking:
                checking = looking.pop()
                checking_path = (
                    checking.data.path if checking.data is not None else None
                )
                if checking_path in highlight_candidates:
                    best_found = checking
                    if checking_path == highlighted_path:
                        break
                if (
                    checking.allow_expand
                    and checking.is_expanded
                    and checking_path in highlighted_path.parents
                ):
                    looking.extend(checking.children)
            if best_found is not None:
                # We need valid lines. Make sure the tree lines have been computed:
                _ = self._tree_lines
                self.cursor_line = best_found.line

    def reload_node(self, node: TreeNode[DirEntry]) -> AwaitComplete:
        """Reload the given node's contents.

        The return value may be awaited to ensure the DirectoryTree has reached
        a stable state and is no longer performing any node reloading (of this node
        or any other nodes).

        Args:
            node: The root of the subtree to reload.

        Returns:
            An optionally awaitable that ensures the subtree has finished reloading.
        """
        return AwaitComplete(self._reload(node))

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
        return self.PATH(path)

    async def watch_path(self) -> None:
        """Watch for changes to the `path` of the directory tree.

        If the path is changed the directory tree will be repopulated using
        the new value as the root.
        """
        has_cursor = self.cursor_node is not None
        self.reset_node(self.root, str(self.path), DirEntry(self.PATH(self.path)))
        await self.reload()
        if has_cursor:
            self.cursor_line = 0
        self.scroll_to(0, 0, animate=False)

    def process_label(self, label: TextType) -> Text:
        """Process a str or Text into a label. May be overridden in a subclass to modify how labels are rendered.

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

        # If the tree isn't mounted yet we can't use component classes to stylize
        # the label fully, so we return early.
        if not self.is_mounted:
            return node_label

        if node._allow_expand:
            prefix = (
                self.ICON_NODE_EXPANDED if node.is_expanded else self.ICON_NODE,
                base_style + TOGGLE_STYLE,
            )
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--folder", partial=True)
            )
        else:
            prefix = (
                self.ICON_FILE,
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
        node.remove_children()
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

    @work(thread=True, exit_on_error=False)
    def _load_directory(self, node: TreeNode[DirEntry]) -> list[Path]:
        """Load the directory contents for a given node.

        Args:
            node: The node to load the directory contents for.

        Returns:
            The list of entries within the directory associated with the node.
        """
        assert node.data is not None
        path = node.data.path
        path = path.expanduser().resolve()
        return sorted(
            self.filter_paths(self._directory_content(path, get_current_worker())),
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
            async with self.lock:
                cursor_node = self.cursor_node
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
                        if cursor_node is not None:
                            self.move_cursor(cursor_node, animate=False)
                finally:
                    # Mark this iteration as done.
                    self._load_queue.task_done()

    async def _on_tree_node_expanded(self, event: Tree.NodeExpanded[DirEntry]) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if self._safe_is_dir(dir_entry.path):
            await self._add_to_load_queue(event.node)
        else:
            self.post_message(self.FileSelected(event.node, dir_entry.path))

    def _on_tree_node_selected(self, event: Tree.NodeSelected[DirEntry]) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if self._safe_is_dir(dir_entry.path):
            self.post_message(self.DirectorySelected(event.node, dir_entry.path))
        else:
            self.post_message(self.FileSelected(event.node, dir_entry.path))
