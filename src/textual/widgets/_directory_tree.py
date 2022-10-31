from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import scandir
import os.path

from rich.console import RenderableType
import rich.repr

from rich.text import Text

from ..message import Message
from .._types import MessageTarget
from ._tree_control import TreeControl, TreeNode


@dataclass
class DirEntry:
    path: str
    is_dir: bool


class DirectoryTree(TreeControl[DirEntry]):
    @rich.repr.auto
    class FileClick(Message, bubble=True):
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
        self.path = os.path.expanduser(path.rstrip("/"))
        label = os.path.basename(self.path)
        data = DirEntry(self.path, True)
        super().__init__(label, data, name=name, id=id, classes=classes)
        self.root.tree.guide_style = "black"

    def render_node(self, node: TreeNode[DirEntry]) -> RenderableType:
        return self.render_tree_label(
            node,
            node.data.is_dir,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
        )

    @lru_cache(maxsize=1024 * 32)
    def render_tree_label(
        self,
        node: TreeNode[DirEntry],
        is_dir: bool,
        expanded: bool,
        is_cursor: bool,
        is_hover: bool,
        has_focus: bool,
    ) -> RenderableType:
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }
        label = Text(node.label) if isinstance(node.label, str) else node.label
        if is_hover:
            label.stylize("underline")
        if is_dir:
            label.stylize("bold")
            icon = "📂" if expanded else "📁"
        else:
            icon = "📄"
            label.highlight_regex(r"\..*$", "italic")

        if label.plain.startswith("."):
            label.stylize("dim")

        if is_cursor and has_focus:
            cursor_style = self.get_component_styles("tree--cursor").rich_style
            label.stylize(cursor_style)

        icon_label = Text(f"{icon} ", no_wrap=True, overflow="ellipsis") + label
        icon_label.apply_meta(meta)
        return icon_label

    def on_styles_updated(self) -> None:
        self.render_tree_label.cache_clear()

    def on_mount(self) -> None:
        self.call_later(self.load_directory, self.root)

    async def load_directory(self, node: TreeNode[DirEntry]):
        path = node.data.path
        directory = sorted(
            list(scandir(path)), key=lambda entry: (not entry.is_dir(), entry.name)
        )
        for entry in directory:
            node.add(entry.name, DirEntry(entry.path, entry.is_dir()))
        node.loaded = True
        node.expand()
        self.refresh(layout=True)

    async def on_tree_control_node_selected(
        self, message: TreeControl.NodeSelected[DirEntry]
    ) -> None:
        dir_entry = message.node.data
        if not dir_entry.is_dir:
            await self.emit(self.FileClick(self, dir_entry.path))
        else:
            if not message.node.loaded:
                await self.load_directory(message.node)
                message.node.expand()
            else:
                message.node.toggle()
