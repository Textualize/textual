from __future__ import annotations

from asyncio import sleep
from dataclasses import dataclass
from itertools import product
from random import choice
from time import monotonic

from rich.console import ConsoleRenderable
from rich.syntax import Syntax

from textual import containers, events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.demo.page import PageScreen
from textual.geometry import Offset, Size
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.timer import Timer
from textual.widgets import Button, Digits, Footer, Select, Static


@dataclass
class NewGame:
    language: str
    code: str
    size: tuple[int, int]


PYTHON_CODE = '''\
class SpatialMap(Generic[ValueType]):
    """A spatial map allows for data to be associated with rectangular regions
    in Euclidean space, and efficiently queried.

    When the SpatialMap is populated, a reference to each value is placed into one or
    more buckets associated with a regular grid that covers 2D space.

    The SpatialMap is able to quickly retrieve the values under a given "window" region
    by combining the values in the grid squares under the visible area.
    """

    def __init__(self, grid_width: int = 100, grid_height: int = 20) -> None:
        """Create a spatial map with the given grid size.

        Args:
            grid_width: Width of a grid square.
            grid_height: Height of a grid square.
        """
        self._grid_size = (grid_width, grid_height)
        self.total_region = Region()
        self._map: defaultdict[GridCoordinate, list[ValueType]] = defaultdict(list)
        self._fixed: list[ValueType] = []

    def _region_to_grid_coordinates(self, region: Region) -> Iterable[GridCoordinate]:
        """Get the grid squares under a region.

        Args:
            region: A region.

        Returns:
            Iterable of grid coordinates (tuple of 2 values).
        """
        # (x1, y1) is the coordinate of the top left cell
        # (x2, y2) is the coordinate of the bottom right cell
        x1, y1, width, height = region
        x2 = x1 + width - 1
        y2 = y1 + height - 1
        grid_width, grid_height = self._grid_size

        return product(
            range(x1 // grid_width, x2 // grid_width + 1),
            range(y1 // grid_height, y2 // grid_height + 1),
        )
'''

XML_CODE = """\
<?xml version="1.0" encoding="UTF-8"?>
<movies>
    <movie>
        <title>Back to the Future</title> <year>1985</year> <director>Robert Zemeckis</director>
        <genre>Science Fiction</genre> <rating>PG</rating>
        <cast>
            <actor> <name>Michael J. Fox</name> <role>Marty McFly</role> </actor>
            <actor> <name>Christopher Lloyd</name> <role>Dr. Emmett Brown</role> </actor>
        </cast>
    </movie>
    <movie>
        <title>The Breakfast Club</title> <year>1985</year> <director>John Hughes</director>
        <genre>Drama</genre> <rating>R</rating>
        <cast>
            <actor> <name>Emilio Estevez</name> <role>Andrew Clark</role> </actor>
            <actor> <name>Molly Ringwald</name> <role>Claire Standish</role> </actor>
        </cast>
    </movie>
    <movie>
        <title>Ghostbusters</title> <year>1984</year> <director>Ivan Reitman</director>
        <genre>Comedy</genre> <rating>PG</rating>
        <cast>
            <actor> <name>Bill Murray</name> <role>Dr. Peter Venkman</role> </actor>
            <actor> <name>Dan Aykroyd</name> <role>Dr. Raymond Stantz</role> </actor>
        </cast>
    </movie>
    <movie>
        <title>Die Hard</title> <year>1988</year> <director>John McTiernan</director>
        <genre>Action</genre> <rating>R</rating>
        <cast>
            <actor> <name>Bruce Willis</name> <role>John McClane</role> </actor>
            <actor> <name>Alan Rickman</name> <role>Hans Gruber</role> </actor>
        </cast>
    </movie>
    <movie>
        <title>E.T. the Extra-Terrestrial</title> <year>1982</year> <director>Steven Spielberg</director>
        <genre>Science Fiction</genre> <rating>PG</rating>
        <cast>
            <actor> <name>Henry Thomas</name> <role>Elliott</role> </actor>
            <actor> <name>Drew Barrymore</name> <role>Gertie</role> </actor>
        </cast>
    </movie>
</movies>"""

BF_CODE = """\
[life.b -- John Horton Conway's Game of Life
(c) 2021 Daniel B. Cristofani
http://brainfuck.org/]

>>>->+>+++++>(++++++++++)[[>>>+<<<-]>+++++>+>>+[<<+>>>>>+<<<-]<-]>>>>[
  [>>>+>+<<<<-]+++>>+[<+>>>+>+<<<-]>>[>[[>>>+<<<-]<]<<++>+>>>>>>-]<-
]+++>+>[[-]<+<[>+++++++++++++++++<-]<+]>>[
  [+++++++++.-------->>>]+[-<<<]>>>[>>,----------[>]<]<<[
    <<<[
      >--[<->>+>-<<-]<[[>>>]+>-[+>>+>-]+[<<<]<-]>++>[<+>-]
      >[[>>>]+[<<<]>>>-]+[->>>]<-[++>]>[------<]>+++[<<<]>
    ]<
  ]>[
    -[+>>+>-]+>>+>>>+>[<<<]>->+>[
      >[->+>+++>>++[>>>]+++<<<++<<<++[>>>]>>>]<<<[>[>>>]+>>>]
      <<<<<<<[<<++<+[-<<<+]->++>>>++>>>++<<<<]<<<+[-<<<+]+>->>->>
    ]<<+<<+<<<+<<-[+<+<<-]+<+[
      ->+>[-<-<<[<<<]>[>>[>>>]<<+<[<<<]>-]]
      <[<[<[<<<]>+>>[>>>]<<-]<[<<<]]>>>->>>[>>>]+>
    ]>+[-<<[-]<]-[
      [>>>]<[<<[<<<]>>>>>+>[>>>]<-]>>>[>[>>>]<<<<+>[<<<]>>-]>
    ]<<<<<<[---<-----[-[-[<->>+++<+++++++[-]]]]<+<+]>
  ]>>
]

[This program simulates the Game of Life cellular automaton.

It duplicates the interface of the classic program at
http://www.linusakesson.net/programming/brainfuck/index.php,
but this program was written from scratch.

Type e.g. "be" to toggle the fifth cell in the second row, "q" to quit,
or a bare linefeed to advance one generation.

Grid wraps toroidally. Board size in parentheses in first line (2-166 work).

This program is licensed under a Creative Commons Attribution-ShareAlike 4.0
International License (http://creativecommons.org/licenses/by-sa/4.0/).]
"""


LEVELS = {"Python": PYTHON_CODE, "XML": XML_CODE, "BF": BF_CODE}


class Tile(containers.Vertical):
    DEFAULT_CSS = """
    Tile {
        width: 16;
        height: 8;
        position: absolute;
       
        transition: opacity 0.1s;
        Static {
            width: auto;
            height: auto;

            &:hover {
              
                tint: $primary 30%;
            }

        }
       
        &#blank {
            visibility: hidden;
        }
    }
   
    """

    position: reactive[Offset] = reactive(Offset)

    def __init__(
        self,
        renderable: ConsoleRenderable,
        tile: int | None,
        size: Size,
        position: Offset,
    ) -> None:
        self.renderable = renderable
        self.tile = tile
        self.tile_size = size
        self.start_position = position

        super().__init__(id="blank" if tile is None else f"tile{self.tile}")
        self.set_reactive(Tile.position, position)

    def compose(self) -> ComposeResult:
        static = Static(
            self.renderable,
            classes="tile",
            name="blank" if self.tile is None else str(self.tile),
        )
        static.styles.width = self.parent.styles.width
        static.styles.height = self.parent.styles.height
        yield static

    def on_mount(self) -> None:
        if self.tile is not None:
            width, height = self.tile_size
            self.styles.width = width
            self.styles.height = height
            column, row = self.position
            self.set_scroll(column * width, row * height)

        self.offset = self.position * self.tile_size

    def watch_position(self, position: Offset) -> None:
        self.animate("offset", position * self.tile_size, duration=0.2)


class GameDialog(containers.VerticalGroup):
    DEFAULT_CSS = """
        GameDialog {
            border: thick $primary-muted;
            padding: 0 2;
            width: 50;
            #values {
                width: 1fr;
                Select { margin: 1 0;}
            }
            Button {
                margin: 0 1 1 1;
                width: 1fr;
            }
        }        
    """

    def compose(self) -> ComposeResult:
        with containers.VerticalGroup(id="values"):
            yield Select.from_values(
                LEVELS.keys(),
                prompt="Language",
                value="Python",
                id="language",
                allow_blank=False,
            )
            yield Select(
                [
                    ("Easy (3x3)", (3, 3)),
                    ("Medium (4x4)", (4, 4)),
                    ("Hard (5x5)", (5, 5)),
                ],
                prompt="Level",
                value=(4, 4),
                id="level",
                allow_blank=False,
            )

        yield Button("Start", variant="primary")

    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        language = self.query_one("#language", Select).value

        level = self.query_one("#level", Select).value
        self.screen.dismiss(NewGame(language, LEVELS[language], level))


class GameDialogScreen(ModalScreen):
    CSS = """
    GameDialogScreen {
      
        align: center middle;        
      
    }

    """

    BINDINGS = [("escape", "dismiss")]

    def compose(self) -> ComposeResult:
        yield GameDialog()


class Game(containers.Vertical, can_focus=True):
    ALLOW_MAXIMIZE = False
    DEFAULT_CSS = """
    Game {
        
        align: center middle;
        hatch: right $panel;
        border: heavy transparent;
        &:focus {
            border: heavy $success;
        }
        #grid {
            border: heavy $primary;           
            hatch: right $panel;
            box-sizing: content-box;
        }
        Digits {
            width: auto;
            color: $foreground;
        }
    }

    """

    BINDINGS = [
        Binding("up", "move('up')", "☝️", priority=True),
        Binding("down", "move('down')", "👇", priority=True),
        Binding("left", "move('left')", "👈", priority=True),
        Binding("right", "move('right')", "👉", priority=True),
    ]

    state = reactive("waiting")
    play_start_time = reactive(monotonic)
    play_time = reactive(0.0, init=False)
    code = reactive("")
    dimensions = reactive(Size(3, 3))
    code = reactive("")
    language = reactive("")

    def __init__(
        self,
        code: str,
        language: str,
        dimensions: tuple[int, int],
        tile_size: tuple[int, int],
    ) -> None:
        self.set_reactive(Game.code, code)
        self.set_reactive(Game.language, language)
        self.set_reactive(Game.dimensions, Size(*dimensions))
        self.tile_size = Size(*tile_size)

        tile_width, tile_height = dimensions
        tile_no = -1
        self.locations: list[list[int | None]] = [
            [(tile_no := tile_no + 1) for _ in range(tile_width)]
            for _ in range(tile_height)
        ]
        self.locations[tile_height - 1][tile_width - 1] = None

        super().__init__()

        self.play_timer: Timer | None = None

    def check_win(self) -> bool:
        return all(tile.start_position == tile.position for tile in self.query(Tile))

    def watch_dimensions(self, dimensions: Size) -> None:
        tile_width, tile_height = dimensions
        tile_no = 0
        self.locations: list[list[int | None]] = [
            [(tile_no := tile_no + 1) for _ in range(tile_width)]
            for _ in range(tile_height)
        ]
        self.locations[tile_height - 1][tile_width - 1] = None

    def compose(self) -> ComposeResult:
        syntax = Syntax(self.code, self.language.lower(), indent_guides=True)
        tile_width, tile_height = self.dimensions
        self.state = "waiting"
        yield Digits("")
        with containers.HorizontalGroup(id="grid") as grid:
            grid.styles.width = tile_width * self.tile_size[0]
            grid.styles.height = tile_height * self.tile_size[1]
            for row, column in product(range(tile_width), range(tile_height)):
                tile_no = self.locations[column][row]
                yield Tile(
                    syntax,
                    tile_no,
                    self.tile_size,
                    Offset(row, column),
                )
        if self.language:
            self.call_later(self.shuffle)

    def update_clock(self) -> None:
        if self.state == "playing":
            elapsed = monotonic() - self.play_start_time
            self.play_time = elapsed

    def watch_play_time(self, play_time: float) -> None:
        minutes, seconds = divmod(play_time, 60)
        hours, minutes = divmod(minutes, 60)
        self.query_one(Digits).update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:04.1f}")

    def watch_state(self, old_state: str, new_state: str) -> None:
        if self.play_timer is not None:
            self.play_timer.stop()

        if new_state == "playing":
            self.play_start_time = monotonic()
            self.play_timer = self.set_interval(1 / 10, self.update_clock)

    def get_tile_location(self, tile: int | None) -> Offset:
        return self.get_tile(tile).position

    def get_tile(self, tile: int | None) -> Tile:
        return self.query_one("#blank" if tile is None else f"#tile{tile}", Tile)

    def get_tile_at(self, position: Offset) -> Tile:
        if position.x < 0 or position.y < 0:
            raise IndexError("No tile")
        tile_no = self.locations[position.y][position.x]
        return self.get_tile(tile_no)

    def move_tile(self, tile_no: int | None, position: Offset) -> None:
        tile = self.get_tile(tile_no)
        blank = self.get_tile(None)
        self.locations[tile.position.y][tile.position.x] = None
        blank.position = tile.position
        self.locations[position.y][position.x] = tile_no
        tile.position = position

        if self.check_win():
            self.state = "won"
            self.notify("You won!")

    def can_move(self, tile: int) -> bool:
        blank_position = self.get_tile(None).position
        tile_position = self.get_tile(tile).position
        return blank_position in (
            tile_position + (1, 0),
            tile_position - (1, 0),
            tile_position + (0, 1),
            tile_position - (0, 1),
        )

    def action_move(self, direction: str) -> None:
        if self.state != "playing":
            self.app.bell()
            return
        blank = self.get_tile(None).position
        if direction == "up":
            position = blank + (0, -1)
        elif direction == "down":
            position = blank + (0, +1)
        elif direction == "left":
            position = blank + (-1, 0)
        elif direction == "right":
            position = blank + (+1, 0)
        try:
            tile = self.get_tile_at(position)
        except IndexError:
            return

        self.move_tile(tile.tile, blank)

    @work(exclusive=True)
    async def shuffle(self, shuffles: int = 150) -> None:
        if self.play_timer is not None:
            self.play_timer.stop()
        self.query_one("#grid").border_title = "[reverse bold] SHUFFLING - Please Wait "
        self.state = "shuffling"
        previous_move: Offset = Offset(-1, -1)
        tile_width, tile_height = self.dimensions
        for _ in range(shuffles):
            blank = self.get_tile(None).position
            moves: list[Offset] = []
            if blank.x > 0:
                moves.append(blank + (-1, 0))
            if blank.x < tile_width - 1:
                moves.append(blank + (+1, 0))
            if blank.y > 0:
                moves.append(blank + (0, -1))
            if blank.y < tile_height - 1:
                moves.append(blank + (0, +1))
            move_position = choice([move for move in moves if move != previous_move])

            move_tile = self.get_tile_at(move_position)
            self.move_tile(move_tile.tile, blank)
            await sleep(0.05)
            previous_move = blank
        self.query_one("#grid").border_title = ""
        self.state = "playing"

    @on(events.Click, ".tile")
    def on_tile_clicked(self, event: events.Click) -> None:
        tile = int(event.widget.name or 0)
        if self.state != "playing" or not self.can_move(tile):
            self.app.bell()
            return
        blank = self.get_tile_location(None)
        self.move_tile(tile, blank)


class GameScreen(PageScreen):
    AUTO_FOCUS = "Game"
    BINDINGS = [
        ("s", "shuffle", "Shuffle"),
        ("n", "new_game", "New Game"),
    ]

    def compose(self) -> ComposeResult:
        yield Game("\n" * 100, "", dimensions=(4, 4), tile_size=(16, 8))
        yield Footer()

    def action_shuffle(self) -> None:
        self.query_one(Game).shuffle()

    def action_new_game(self) -> None:
        self.app.push_screen(GameDialogScreen(), callback=self.new_game)

    async def new_game(self, new_game: NewGame | None) -> None:
        if new_game is None:
            return
        game = self.query_one(Game)
        game.state = "waiting"
        game.code = new_game.code
        game.language = new_game.language
        game.dimensions = Size(*new_game.size)
        await game.recompose()

    def on_mount(self) -> None:
        self.action_new_game()


if __name__ == "__main__":
    from textual.app import App

    class GameApp(App):
        def get_default_screen(self) -> Screen:
            return GameScreen()

    app = GameApp()
    app.run()
