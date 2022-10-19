"""Simple version of 5x5, developed for/with Textual."""

from pathlib import Path
from typing import Final, cast

from textual.containers import Horizontal
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Button, Static
from textual.css.query import DOMQuery
from textual.reactive import reactive
from textual.binding import Binding

from rich.markdown import Markdown


class Help(Screen):
    """The help screen for the application."""

    #: Bindings for the help screen.
    BINDINGS = [("escape,space,q,h,question_mark", "app.pop_screen", "Close")]

    def compose(self) -> ComposeResult:
        """Compose the game's help."""
        yield Static(Markdown(Path(__file__).with_suffix(".md").read_text()))


class WinnerMessage(Static):
    """Widget to tell the user they have won."""

    #: The minimum number of moves you can solve the puzzle in.
    MIN_MOVES: Final = 14

    @staticmethod
    def _plural(value: int) -> str:
        return "" if value == 1 else "s"

    def show(self, moves: int) -> None:
        """Show the winner message."""
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

    #: Keep track of how many moves the player has made.
    moves = reactive(0)

    #: Keep track of how many cells are turned on.
    on = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the game header."""
        yield Horizontal(
            Static(self.app.title, id="app-title"),
            Static(id="moves"),
            Static(id="progress"),
        )

    def watch_moves(self, moves: int):
        """Watch the moves reactive and update when it changes."""
        self.query_one("#moves", Static).update(f"Moves: {moves}")

    def watch_on(self, on: int):
        """Watch the on-count reactive and update when it changes."""
        self.query_one("#progress", Static).update(f"On: {on}")


class GameCell(Button):
    """Individual playable cell in the game."""

    @staticmethod
    def at(row: int, col: int) -> str:
        return f"cell-{row}-{col}"

    def __init__(self, row: int, col: int) -> None:
        """Initialise the game cell."""
        super().__init__("", id=self.at(row, col))
        self.row = row
        self.col = col


class GameGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        """Compose the game grid."""
        for row in range(Game.SIZE):
            for col in range(Game.SIZE):
                yield GameCell(row, col)


class Game(Screen):
    """Main 5x5 game grid screen."""

    #: The size of the game grid. Clue's in the name really.
    SIZE = 5

    #: The bindings for the main game grid.
    BINDINGS = [
        Binding("n", "new_game", "New Game"),
        Binding("h,question_mark", "app.push_screen('help')", "Help"),
        Binding("q", "quit", "Quit"),
        Binding("up,w", "navigate(-1,0)", "Move Up", False),
        Binding("down,s", "navigate(1,0)", "Move Down", False),
        Binding("left,a", "navigate(0,-1)", "Move Left", False),
        Binding("right,d", "navigate(0,1)", "Move Right", False),
        Binding("space", "move", "Toggle", False),
    ]

    @property
    def on_cells(self) -> DOMQuery[GameCell]:
        """The collection of cells that are currently turned on.

        :type: DOMQuery[GameCell]
        """
        return cast(DOMQuery[GameCell], self.query("GameCell.on"))

    @property
    def on_count(self) -> int:
        """The number of cells that are turned on.

        :type: int
        """
        return len(self.on_cells)

    @property
    def all_on(self) -> bool:
        """Are all the cells turned on?

        :type: bool
        """
        return self.on_count == self.SIZE * self.SIZE

    def game_playable(self, playable: bool) -> None:
        """Mark the game as playable, or not.

        :param bool playable: Should the game currently be playable?
        """
        for cell in self.query(GameCell):
            cell.disabled = not playable

    def cell(self, row: int, col: int) -> GameCell:
        """Get the cell at a given location.

        :param int row: The row of the cell to get.
        :param int col: The column of the cell to get.
        :returns: The cell at that location.
        :rtype: GameCell
        """
        return self.query_one(f"#{GameCell.at(row,col)}", GameCell)

    def compose(self) -> ComposeResult:
        """Compose the application screen."""
        yield GameHeader()
        yield GameGrid()
        yield Footer()
        yield WinnerMessage()

    def toggle_cell(self, row: int, col: int) -> None:
        """Toggle an individual cell, but only if it's on bounds.

        :param int row: The row of the cell to toggle.
        :param int col: The column of the cell to toggle.

        If the row and column would place the cell out of bounds for the
        game grid, this function call is a no-op. That is, it's safe to call
        it with an invalid cell coordinate.
        """
        if 0 <= row <= (self.SIZE - 1) and 0 <= col <= (self.SIZE - 1):
            self.cell(row, col).toggle_class("on")

    _PATTERN: Final = (-1, 1, 0, 0, 0)

    def toggle_cells(self, cell: GameCell) -> None:
        """Toggle a 5x5 pattern around the given cell.

        :param GameCell cell: The cell to toggle the cells around.
        """
        for row, col in zip(self._PATTERN, reversed(self._PATTERN)):
            self.toggle_cell(cell.row + row, cell.col + col)
        self.query_one(GameHeader).on = self.on_count

    def make_move_on(self, cell: GameCell) -> None:
        """Make a move on the given cell.

        All relevant cells around the given cell are toggled as per the
        game's rules.
        """
        self.toggle_cells(cell)
        self.query_one(GameHeader).moves += 1
        if self.all_on:
            self.query_one(WinnerMessage).show(self.query_one(GameHeader).moves)
            self.game_playable(False)

    def on_button_pressed(self, event: GameCell.Pressed) -> None:
        """React to a press of a button on the game grid."""
        self.make_move_on(cast(GameCell, event.button))

    def action_new_game(self) -> None:
        """Start a new game."""
        self.query_one(GameHeader).moves = 0
        self.on_cells.remove_class("on")
        self.query_one(WinnerMessage).hide()
        middle = self.cell(self.SIZE // 2, self.SIZE // 2)
        self.toggle_cells(middle)
        self.set_focus(middle)
        self.game_playable(True)

    def action_navigate(self, row: int, col: int) -> None:
        """Navigate to a new cell by the given offsets."""
        if self.focused and isinstance(self.focused, GameCell):
            self.set_focus(
                self.cell(
                    (self.focused.row + row) % self.SIZE,
                    (self.focused.col + col) % self.SIZE,
                )
            )

    def action_move(self) -> None:
        """Make a move on the current cell."""
        if self.focused and isinstance(self.focused, GameCell):
            self.focused.press()

    def on_mount(self) -> None:
        """Get the game started when we first mount."""
        self.action_new_game()


class FiveByFive(App[None]):
    """Main 5x5 application class."""

    #: The name of the stylesheet for the app.
    CSS_PATH = Path(__file__).with_suffix(".css")

    #: The pre-loaded screens for the application.
    SCREENS = {"help": Help()}

    #: App-level bindings.
    BINDINGS = [("D", "app.toggle_dark", "Toggle Dark Mode")]

    def __init__(self) -> None:
        """Constructor."""
        super().__init__(title="5x5 -- A little annoying puzzle")

    def on_mount(self) -> None:
        """Set up the application on startup."""
        self.push_screen(Game())


if __name__ == "__main__":
    FiveByFive().run()
