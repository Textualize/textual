$animation-type: linear;
$animation-speed: 175ms;

Game {
    align: center middle;
    layers: gameplay messages;
}

GameGrid {
    layout: grid;
    grid-size: 5 5;
    layer: gameplay;
}

GameHeader {
    background: $primary-background;
    color: $text;
    height: 1;
    dock: top;
    layer: gameplay;
}

GameHeader #app-title {
    width: 60%;
}

GameHeader #moves {
    width: 20%;
}

GameHeader #progress {
    width: 20%;
}

Footer {
    height: 1;
    dock: bottom;
    layer: gameplay;
}

GameCell {
    width: 100%;
    height: 100%;
    background: $surface;
    border: round $surface-darken-1;
    transition: background $animation-speed $animation-type, color $animation-speed $animation-type;
}

GameCell:hover {
    background: $panel-lighten-1;
    border: round $panel;
}

GameCell.filled {
    background: $secondary;
    border: round $secondary-darken-1;
}

GameCell.filled:hover {
    background: $secondary-lighten-1;
    border: round $secondary;
}

WinnerMessage {
    width: 50%;
    height: 25%;
    layer: messages;
    visibility: hidden;
    content-align: center middle;
    text-align: center;
    background: $success;
    color: $text;
    border: round;
    padding: 2;
}

.visible {
    visibility: visible;
}

Help {
    border: round $primary-lighten-3;
}

/* five_by_five.tcss ends here */
