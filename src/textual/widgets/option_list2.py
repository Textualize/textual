from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rich.console import RenderableType

from textual.binding import Binding, BindingType
from textual.reactive import reactive
from textual.scroll_view import ScrollView

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


NewOptionListContent: TypeAlias = "OptionListContent | None | RenderableType"
"""The type of a new item of option list content to be added to an option list.

This type represents all of the types that will be accepted when adding new
content to the option list. This is a superset of [`OptionListContent`][textual.types.OptionListContent].
"""


class OptionList(ScrollView, can_focus=True):
    """A vertical option list with bounce-bar highlighting."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("pagedown", "page_down", "Page down", show=False),
        Binding("pageup", "page_up", "Page up", show=False),
        Binding("up", "cursor_up", "Up", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | down | Move the highlight down. |
    | end | Move the highlight to the last option. |
    | enter | Select the current option. |
    | home | Move the highlight to the first option. |
    | pagedown | Move the highlight down a page of options. |
    | pageup | Move the highlight up a page of options. |
    | up | Move the highlight up. |
    """

    DEFAULT_CSS = """
    OptionList {
        height: auto;
        max-height: 100%;
        color: $foreground;
        overflow-x: hidden;
        border: tall $border-blurred;
        padding: 0 1;
        background: $surface;
        & > .option-list--option-highlighted {
            color: $block-cursor-blurred-foreground;
            background: $block-cursor-blurred-background;
            text-style: $block-cursor-blurred-text-style;
        }
        &:focus {
            border: tall $border;
            background-tint: $foreground 5%;
            & > .option-list--option-highlighted {
                color: $block-cursor-foreground;
                background: $block-cursor-background;
                text-style: $block-cursor-text-style;
            }
        }
        & > .option-list--separator {
            color: $foreground 15%;
        }
        & > .option-list--option-highlighted {
            color: $foreground;
            background: $block-cursor-blurred-background;
        }
        & > .option-list--option-disabled {
            color: $text-disabled;
        }
        & > .option-list--option-hover {
            background: $block-hover-background;
        }
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "option-list--option",
        "option-list--option-disabled",
        "option-list--option-highlighted",
        "option-list--option-hover",
        "option-list--separator",
    }
    """
    | Class | Description |
    | :- | :- |
    | `option-list--option-disabled` | Target disabled options. |
    | `option-list--option-highlighted` | Target the highlighted option. |
    | `option-list--option-hover` | Target an option that has the mouse over it. |
    | `option-list--separator` | Target the separators. |
    """

    highlighted: reactive[int | None] = reactive["int | None"](None)
    """The index of the currently-highlighted option, or `None` if no option is highlighted."""

    def __init__(
        self,
        *content: NewOptionListContent,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        wrap: bool = True,
        tooltip: RenderableType | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
