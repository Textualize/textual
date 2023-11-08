from __future__ import annotations

from asyncio import Event, Queue
from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
)

from ..await_complete import AwaitComplete

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

from rich.style import Style
from rich.text import Text, TextType

from .. import work
from ..message import Message
from ..reactive import var
from ..worker import Worker, WorkerCancelled, WorkerFailed, get_current_worker
from ._tree import TOGGLE_STYLE, Tree, TreeNode

TreeState: TypeAlias = Tuple[Path, List["TreeState"]]


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
        self._load_queue: Queue[
            tuple[
                TreeNode[DirEntry],
                Optional[TreeState],
                Optional[tuple[list[Path], list[Path]]],
            ],
        ] = Queue()
        super().__init__(
            str(path),
            data=DirEntry(self.PATH(path)),
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.path = path
        self._to_restore_count = 0
        self._to_restore_event = Event()
        self._to_restore_event.set()

    def _add_to_load_queue(
        self,
        node: TreeNode[DirEntry],
        state: TreeState | None,
        to_highlight: tuple[list[Path], list[Path]] | None,
    ) -> AwaitComplete:
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
            self._load_queue.put_nowait((node, state, to_highlight))

        return AwaitComplete(self._load_queue.join(), self._to_restore_event.wait())

    def reload(self, keep_state: bool = True) -> AwaitComplete:
        """Reload the `DirectoryTree` contents."""
        # Orphan the old queue...
        self._load_queue = Queue()
        # ... reset the root node...
        processed = self.reload_node(self.root, keep_state)
        # ... and replace the old load with a new one.
        self._loader()
        return processed

    def clear_node(self, node: TreeNode[DirEntry]) -> Self:
        """Clear all nodes under the given node.

        Returns:
            The `Tree` instance.
        """
        self._clear_line_cache()
        node_label = node._label
        node_data = node.data
        node_parent = node.parent
        node = TreeNode(
            self,
            node_parent,
            self._new_id(),
            node_label,
            node_data,
            expanded=True,
        )
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

    def _compute_state(self, node: TreeNode[DirEntry]) -> TreeState:
        """Compute the state of the subtree rooted at the given node.

        Args:
            node: The root of the subtree for which we want the state computed.

        Returns:
            A recursive structure indicating all nodes that were expanded.
        """
        state: TreeState = (node.data.path, [])
        node_stack: list[tuple[list[TreeState], TreeNode[DirEntry]]] = [
            (state[1], node)
        ]
        # Find children that are expanded so that we can keep them expanded after
        # reloading the node.
        while node_stack:
            stack_state_list, stack_node = node_stack.pop()
            for child in stack_node.children:
                if child.is_expanded:
                    new_state: TreeState = (child.data.path, [])
                    stack_state_list.append(new_state)
                    node_stack.append((new_state[1], child))

        return state

    def reload_node(
        self, node: TreeNode[DirEntry], keep_state: bool = True
    ) -> AwaitComplete:
        """Reload the given node's contents.

        The return value may be awaited to ensure the DirectoryTree has reached
        a stable state and is no longer performing any node reloading (of this node
        or any other nodes).

        Args:
            node: The node to reload.
        """
        state: TreeState | None
        to_highlight: tuple[list[Path], list[Path]] | None
        if keep_state and node.is_expanded:
            state = self._compute_state(node)
            self._to_restore_count = 1
            self._to_restore_event.clear()

            # WE DON'T NEED TO DO THIS IF THE CURRENTLY HIGHLIGHTED ISN'T PART
            # OF THE SUBTREE THAT IS BEING RELOADED.
            # IN THAT CASE, SKIP!
            # Create a list of paths we'd like to highlight, ordered by priority.
            # First is the same path, then all the siblings that come after, then all
            # of the siblings that came before (in reverse order), and finally all
            # the parent directories.
            siblings_to_highlight: list[Path] = []
            highlighted_node = self.get_node_at_line(self.cursor_line)
            if highlighted_node is not None:
                parent = highlighted_node.parent
                if parent is not None:
                    siblings = parent.children
                    node_at = siblings.index(highlighted_node)
                    siblings_to_highlight.extend(
                        sibling.data.path for sibling in siblings[node_at:]
                    )
                    siblings_to_highlight.extend(
                        sibling.data.path for sibling in reversed(siblings[:node_at])
                    )
                else:
                    siblings_to_highlight.append(highlighted_node.data.path)
                to_highlight = (
                    siblings_to_highlight,
                    list(highlighted_node.data.path.parents),
                )

        else:
            state = to_highlight = None

        self.reset_node(
            node, str(node.data.path.name), DirEntry(self.PATH(node.data.path))
        )

        return self._add_to_load_queue(node, state, to_highlight)

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
        await self.reload(keep_state=False)

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

    @work(thread=True)
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

    def _restore_highlighting(
        self,
        node: TreeNode[DirEntry],
        siblings_to_highlight: list[Path],
    ) -> None:
        """Try to restore cursor highlighting into the children of the given node.

        Args:
            node: The node who contained the node that was selected/had the cursor before
                reloading the tree.
            siblings_to_highlight: A list of possible siblings that could be highlighted,
                ordered in terms of highlighting priority.
        """

        children_paths = {child.data.path for child in node.children}
        for could_be_highlighted in siblings_to_highlight:
            if could_be_highlighted in children_paths:
                node_to_highlight = next(
                    child
                    for child in node.children
                    if child.data.path == could_be_highlighted
                )
                self.cursor_line = node_to_highlight.line
                break
        else:
            self.cursor_line = node.line

    @work(group="_state_restoration")
    async def _restore_state(
        self,
        node: TreeNode[DirEntry],
        state: TreeState,
        to_highlight: tuple[list[Path], list[Path]],
    ) -> None:
        """Restore the state of the tree to what is was before reloading.

        This method will try to preserve as much of the state of the tree as possible,
        expanding nodes that were already expanded and putting the cursor on top of the
        node that had it before (if still present) or the closest node possible.

        Args:
            node: The node that is having its state restored.
            state: A record of the state of the subtree whose root is the given node.
            to_highlight: Information about the tree nodes that we'll try to highlight.
        """
        to_restore = [(node, state)]
        self._to_restore_count -= 1

        siblings_to_highlight, parents = to_highlight
        to_highlight_parent = parents[0]
        if node.data.path == to_highlight_parent:
            self._restore_highlighting(node, siblings_to_highlight)
        elif node.data.path in parents:
            self.cursor_line = node.line

        while to_restore:
            node, state = to_restore.pop()
            if not node.is_expanded:
                self._to_restore_count += 1
                self._add_to_load_queue(node, state, to_highlight)

            # See if the paths that were previously represented in the tree and expanded
            # still exist. If so, flag that node (and its state) for restoring.
            paths_to_children = {
                child.data.path: child for child in node.children if child.allow_expand
            }
            for expanded in state[1]:
                expanded_path = expanded[0]
                child_node = paths_to_children.get(expanded_path, None)
                if child_node is not None:
                    to_restore.append((child_node, expanded))

        if not self._to_restore_count:
            self._to_restore_event.set()

    @work(exclusive=True)
    async def _loader(self) -> None:
        """Background loading queue processor."""
        worker = get_current_worker()
        while not worker.is_cancelled:
            # Get the next node that needs loading of the queue. Note that
            # this blocks if the queue is empty.
            node, state, to_highlight = await self._load_queue.get()
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
                    with self.prevent(Tree.NodeExpanded):
                        self._populate_node(node, content)
                # Restore the state of the node we just reloaded.
                if state is not None:
                    self._restore_state(node, state, to_highlight)
            finally:
                # Mark this iteration as done.
                self._load_queue.task_done()

    async def _on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if self._safe_is_dir(dir_entry.path):
            await self._add_to_load_queue(event.node, None, None)
        else:
            self.post_message(self.FileSelected(event.node, dir_entry.path))

    def _on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if self._safe_is_dir(dir_entry.path):
            self.post_message(self.DirectorySelected(event.node, dir_entry.path))
        else:
            self.post_message(self.FileSelected(event.node, dir_entry.path))
