from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree


class DirectoryTreeReloadApp(App[None]):
    BINDINGS = [
        ("r", "reload"),
        ("e", "expand"),
        ("d", "delete"),
    ]

    async def setup(self, path_root: Path) -> None:
        self.path_root = path_root

        structure = [
            "f1.txt",
            "f2.txt",
            "b1/f1.txt",
            "b1/f2.txt",
            "b2/f1.txt",
            "b2/f2.txt",
            "b1/c1/f1.txt",
            "b1/c1/f2.txt",
            "b1/c2/f1.txt",
            "b1/c2/f2.txt",
            "b1/c1/d1/f1.txt",
            "b1/c1/d1/f2.txt",
            "b1/c1/d2/f1.txt",
            "b1/c1/d2/f2.txt",
        ]
        for file in structure:
            path = path_root / Path(file)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)

        await self.mount(DirectoryTree(self.path_root))

    async def action_reload(self) -> None:
        dt = self.query_one(DirectoryTree)
        await dt.reload()

    def action_expand(self) -> None:
        self.query_one(DirectoryTree).root.expand_all()

    def action_delete(self) -> None:
        self.rmdir(self.path_root / Path("b1/c1/d2"))
        self.rmdir(self.path_root / Path("b1/c2"))
        self.rmdir(self.path_root / Path("b2"))

    def rmdir(self, path: Path) -> None:
        for file in path.iterdir():
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                self.rmdir(file)
        path.rmdir()


if __name__ == "__main__":
    DirectoryTreeReloadApp(Path("playground")).run()
