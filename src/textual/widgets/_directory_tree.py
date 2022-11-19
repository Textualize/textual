from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from rich.style import Style
from rich.text import Text

from ._tree import Tree, TreeNode, TOGGLE_STYLE


@dataclass
class DirEntry:
    path: str
    is_dir: bool
    loaded: bool = False


class DirectoryTree(Tree[DirEntry]):

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
        dir_entry = event.node.data
        if dir_entry is None:
            return
        if dir_entry.is_dir and not dir_entry.loaded:
            self.load_directory(event.node)
