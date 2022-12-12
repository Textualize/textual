from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from rich.style import Style
from rich.text import Text, TextType

from ..message import Message
from ._tree import Tree, TreeNode, TOGGLE_STYLE
from .._types import MessageTarget


@dataclass
class DirEntry:
    """Attaches directory information ot a node."""

    path: str
    is_dir: bool
    loaded: bool = False


class DirectoryTree(Tree[DirEntry]):
    """A Tree widget that presents files and directories.

    Args:
        path (str): Path to directory.
        name (str | None, optional): The name of the widget, or None for no name. Defaults to None.
        id (str | None, optional): The ID of the widget in the DOM, or None for no ID. Defaults to None.
        classes (str | None, optional): A space-separated list of classes, or None for no classes. Defaults to None.
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "tree--label",
        "tree--guides",
        "tree--guides-hover",
        "tree--guides-selected",
        "tree--cursor",
        "tree--highlight",
        "tree--highlight-line",
        "directory-tree--folder",
        "directory-tree--file",
        "directory-tree--extension",
        "directory-tree--hidden",
    }

    DEFAULT_CSS = """
    DirectoryTree > .directory-tree--folder {
        text-style: bold;        
    }

    DirectoryTree > .directory-tree--file {
        
    }

    DirectoryTree > .directory-tree--extension {               
        text-style: italic;   
    }

    DirectoryTree > .directory-tree--hidden {
        color: $text 50%;        
    }
    """

    class FileSelected(Message, bubble=True):
        def __init__(self, sender: MessageTarget, path: str) -> None:
            self.path = path
            super().__init__(sender)

    def __init__(
        self,
        path: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:

        self.path = path
        super().__init__(
            path,
            data=DirEntry(path, True),
            name=name,
            id=id,
            classes=classes,
        )

    def process_label(self, label: TextType):
        """Process a str or Text in to a label. Maybe overridden in a subclass to change modify how labels are rendered.

        Args:
            label (TextType): Label.

        Returns:
            Text: A Rich Text object.
        """
        if isinstance(label, str):
            text_label = Text(label)
        else:
            text_label = label
        first_line = text_label.split()[0]
        return first_line

    def render_label(self, node: TreeNode[DirEntry], base_style: Style, style: Style):
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

    def load_directory(self, node: TreeNode[DirEntry]) -> None:
        assert node.data is not None
        dir_path = Path(node.data.path)
        node.data.loaded = True
        directory = sorted(
            list(dir_path.iterdir()),
            key=lambda path: (not path.is_dir(), path.name.lower()),
        )
        for path in directory:
            node.add(
                path.name,
                data=DirEntry(str(path), path.is_dir()),
                allow_expand=path.is_dir(),
            )
        node.expand()

    def on_mount(self) -> None:
        self.load_directory(self.root)

    def on_tree_node_expanded(self, event: Tree.NodeSelected) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if dir_entry.is_dir:
            if not dir_entry.loaded:
                self.load_directory(event.node)
        else:
            self.emit_no_wait(self.FileSelected(self, dir_entry.path))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if not dir_entry.is_dir:
            self.emit_no_wait(self.FileSelected(self, dir_entry.path))
