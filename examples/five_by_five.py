"""Simple version of 5x5, developed for/with Textual."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import DOMQuery
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Label, Markdown

if TYPE_CHECKING:
    from typing_extensions import Final


class Help(Screen):
    """The help screen for the application."""

    BINDINGS = [("escape,space,q,question_mark", "app.pop_screen", "Close")]
    """Bindings for the help screen."""

    def compose(self) -> ComposeResult:
        """Compose the game's help.

        Returns:
            ComposeResult: The result of composing the help screen.
        """
        yield Markdown(Path(__file__).with_suffix(".md").read_text())


class WinnerMessage(Label):
    """Widget to tell the user they have won."""

    MIN_MOVES: Final = 14
    """int: The minimum number of moves you can solve the puzzle in."""

    @staticmethod
    def _plural(value: int) -> str:
        return "" if value == 1 else "s"

    def show(self, moves: int) -> None:
        """Show the winner message.

        Args:
            moves (int): The number of moves required to win.
        """
        self.update(
            "W I N N E R !\n\n\n"
            f"You solved the puzzle in {moves} move{self._plural(moves)}."
            + (
                (
                    f" It is possible to solve the puzzle in {self.MIN_MOVES}, "
                    f"you were {moves - self.MIN_MOVES} move{self._plural(moves - self.MIN_MOVES)} over."
                )
                if moves > self.MIN_MOVES
                else " Well done! That's the minimum number of moves to solve the puzzle!"
            )
        )
        self.add_class("visible")

    def hide(self) -> None:
        """Hide the winner message."""
        self.remove_class("visible")


class GameHeader(Widget):
    """Header for the game.

    Comprises of the title (``#app-title``), the number of moves ``#moves``
    and the count of how many cells are turned on (``#progress``).
    """

    moves = reactive(0)
    """int: Keep track of how many moves the player has made."""

    filled = reactive(0)
    """int: Keep track of how many cells are filled."""

    def compose(self) -> ComposeResult:
        """Compose the game header.

        Returns:
            ComposeResult: The result of composing the game header.
        """
        with Horizontal():
            yield Label(self.app.title, id="app-title")
            yield Label(id="moves")
            yield Label(id="progress")

    def watch_moves(self, moves: int):
        """Watch the moves reactive and update when it changes.

        Args:
            moves (int): The number of moves made.
        """
        self.query_one("#moves", Label).update(f"Moves: {moves}")

    def watch_filled(self, filled: int):
        """Watch the on-count reactive and update when it changes.

        Args:
            filled (int): The number of cells that are currently on.
        """
        self.query_one("#progress", Label).update(f"Filled: {filled}")


class GameCell(Button):
    """Individual playable cell in the game."""

    @staticmethod
    def at(row: int, col: int) -> str:
        """Get the ID of the cell at the given location.

        Args:
            row (int): The row of the cell.
            col (int): The column of the cell.

        Returns:
            str: A string ID for the cell.
        """
        return f"cell-{row}-{col}"

    def __init__(self, row: int, col: int) -> None:
        """Initialise the game cell.

        Args:
            row (int): The row of the cell.
            col (int): The column of the cell.
        """
        super().__init__("", id=self.at(row, col))
        self.row = row
        self.col = col


class GameGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        """Compose the game grid.

        Returns:
            ComposeResult: The result of composing the game grid.
        """
        for row in range(Game.SIZE):
            for col in range(Game.SIZE):
                yield GameCell(row, col)


class Game(Screen):
    """Main 5x5 game grid screen."""

    SIZE: Final = 5
    """The size of the game grid. Clue's in the name really."""

    BINDINGS = [
        Binding("n", "new_game", "New Game"),
        Binding("question_mark", "app.push_screen('help')", "Help", key_display="?"),
        Binding("q", "app.quit", "Quit"),
        Binding("up,w,k", "navigate(-1,0)", "Move Up", False),
        Binding("down,s,j", "navigate(1,0)", "Move Down", False),
        Binding("left,a,h", "navigate(0,-1)", "Move Left", False),
        Binding("right,d,l", "navigate(0,1)", "Move Right", False),
        Binding("space", "move", "Toggle", False),
    ]
    """The bindings for the main game grid."""

    @property
    def filled_cells(self) -> DOMQuery[GameCell]:
        """DOMQuery[GameCell]: The collection of cells that are currently turned on."""
        return cast(DOMQuery[GameCell], self.query("GameCell.filled"))

    @property
    def filled_count(self) -> int:
        """int: The number of cells that are currently filled."""
        return len(self.filled_cells)

    @property
    def all_filled(self) -> bool:
        """bool: Are all the cells filled?"""
        return self.filled_count == self.SIZE * self.SIZE

    def game_playable(self, playable: bool) -> None:
        """Mark the game as playable, or not.

        Args:
            playable (bool): Should the game currently be playable?
        """
        self.query_one(GameGrid).disabled = not playable

    def cell(self, row: int, col: int) -> GameCell:
        """Get the cell at a given location.

        Args:
            row (int): The row of the cell to get.
            col (int): The column of the cell to get.

        Returns:
            GameCell: The cell at that location.
        """
        return self.query_one(f"#{GameCell.at(row,col)}", GameCell)

    def compose(self) -> ComposeResult:
        """Compose the game screen.

        Returns:
            ComposeResult: The result of composing the game screen.
        """
        yield GameHeader()
        yield GameGrid()
        yield Footer()
        yield WinnerMessage()

    def toggle_cell(self, row: int, col: int) -> None:
        """Toggle an individual cell, but only if it's in bounds.

        If the row and column would place the cell out of bounds for the
        game grid, this function call is a no-op. That is, it's safe to call
        it with an invalid cell coordinate.

        Args:
            row (int): The row of the cell to toggle.
            col (int): The column of the cell to toggle.
        """
        if 0 <= row <= (self.SIZE - 1) and 0 <= col <= (self.SIZE - 1):
            self.cell(row, col).toggle_class("filled")

    _PATTERN: Final = (-1, 1, 0, 0, 0)

    def toggle_cells(self, cell: GameCell) -> None:
        """Toggle a 5x5 pattern around the given cell.

        Args:
            cell (GameCell): The cell to toggle the cells around.
        """
        for row, col in zip(self._PATTERN, reversed(self._PATTERN)):
            self.toggle_cell(cell.row + row, cell.col + col)
        self.query_one(GameHeader).filled = self.filled_count

    def make_move_on(self, cell: GameCell) -> None:
        """Make a move on the given cell.

        All relevant cells around the given cell are toggled as per the
        game's rules.

        Args:
            cell (GameCell): The cell to make a move on
        """
        self.toggle_cells(cell)
        self.query_one(GameHeader).moves += 1
        if self.all_filled:
            self.query_one(WinnerMessage).show(self.query_one(GameHeader).moves)
            self.game_playable(False)

    def on_button_pressed(self, event: GameCell.Pressed) -> None:
        """React to a press of a button on the game grid.

        Args:
            event (GameCell.Pressed): The event to react to.
        """
        self.make_move_on(cast(GameCell, event.button))

    def action_new_game(self) -> None:
        """Start a new game."""
        self.query_one(GameHeader).moves = 0
        self.filled_cells.remove_class("filled")
        self.query_one(WinnerMessage).hide()
        middle = self.cell(self.SIZE // 2, self.SIZE // 2)
        self.toggle_cells(middle)
        self.set_focus(middle)
        self.game_playable(True)

    def action_navigate(self, row: int, col: int) -> None:
        """Navigate to a new cell by the given offsets.

        Args:
            row (int): The row of the cell to navigate to.
            col (int): The column of the cell to navigate to.
        """
        if isinstance(self.focused, GameCell):
            self.set_focus(
                self.cell(
                    (self.focused.row + row) % self.SIZE,
                    (self.focused.col + col) % self.SIZE,
                )
            )

    def action_move(self) -> None:
        """Make a move on the current cell."""
        if isinstance(self.focused, GameCell):
            self.focused.press()

    def on_mount(self) -> None:
        """Get the game started when we first mount."""
        self.action_new_game()


class FiveByFive(App[None]):
    """Main 5x5 application class."""

    CSS_PATH = "five_by_five.tcss"
    """The name of the stylesheet for the app."""

    SCREENS = {"help": Help}
    """The pre-loaded screens for the application."""

    BINDINGS = [("ctrl+d", "toggle_dark", "Toggle Dark Mode")]
    """App-level bindings."""

    TITLE = "5x5 -- A little annoying puzzle"
    """The title of the application."""

    def on_mount(self) -> None:
        """Set up the application on startup."""
        self.push_screen(Game())


if __name__ == "__main__":
    FiveByFive().run()
