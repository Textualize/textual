from __future__ import annotations

from typing import ClassVar

import rich.repr
from rich.console import RenderableType
from rich.measure import Measurement
from rich.rule import Rule
from rich.style import Style
from typing_extensions import TypeAlias

from .. import events
from ..cache import LRUCache
from ..geometry import Size
from ..reactive import reactive
from ..scroll_view import ScrollView
from ..strip import Strip


class DuplicateID(Exception):
    """Raised if a duplicate ID is used when adding options to an option list."""


class OptionDoesNotExist(Exception):
    """Raised when a request has been made for an option that doesn't exist."""


class Separator:
    """Class used to add a separator to an [OptionList][textual.widgets.OptionList]."""

    def __rich__(self):
        return Rule()


@rich.repr.auto
class Option:
    """Class that holds the details of an individual option."""

    def __init__(
        self, prompt: RenderableType, id: str | None = None, disabled: bool = False
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt for the option.
            id: The optional ID for the option.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        self.__prompt = prompt
        self.__id = id
        self.disabled = disabled

    @property
    def prompt(self) -> RenderableType:
        """The prompt for the option."""
        return self.__prompt

    def set_prompt(self, prompt: RenderableType) -> None:
        """Set the prompt for the option.

        Args:
            prompt: The new prompt for the option.
        """
        self.__prompt = prompt

    @property
    def id(self) -> str | None:
        """The optional ID for the option."""
        return self.__id

    def __rich_repr__(self) -> rich.repr.Result:
        yield "prompt", self.prompt
        yield "id", self.id, None
        yield "disabled", self.disabled, False

    def __rich__(self) -> RenderableType:
        return self.__prompt


OptionListContent: TypeAlias = "Option | Separator"
"""The type of an item of content in the option list.

This type represents all of the types that will be found in the list of
content of the option list after it has been processed for addition.
"""

NewOptionListContent: TypeAlias = "OptionListContent | None | RenderableType"
"""The type of a new item of option list content to be added to an option list.

This type represents all of the types that will be accepted when adding new
content to the option list. This is a superset of [`OptionListContent`][textual.types.OptionListContent].
"""


class OptionList(ScrollView, can_focus=True):
    DEFAULT_CSS = """
    OptionList {
        height: auto;
        max-height: 100%;
        background: $boost;
        color: $text;
        overflow-x: hidden;
        border: tall transparent;
        padding: 0 1;
    }

    OptionList:focus {
        border: tall $accent;

    }

    OptionList > .option-list--separator {
        color: $foreground 15%;
    }

    OptionList > .option-list--option-highlighted {
        color: $text;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-highlighted {
        background: $accent;
    }

    OptionList > .option-list--option-disabled {
        color: $text-disabled;
    }

    OptionList > .option-list--option-hover {
        background: $boost;
    }

    OptionList > .option-list--option-hover-highlighted {
        background: $accent 60%;
        color: $text;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-hover-highlighted {
        background: $accent;
        color: $text;
        text-style: bold;
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "option-list--option",
        "option-list--option-disabled",
        "option-list--option-highlighted",
        "option-list--option-hover",
        "option-list--option-hover-highlighted",
        "option-list--separator",
    }

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

        self._wrap = wrap
        """Should we auto-wrap options?

        If `False` options wider than the list will be truncated.
        """

        self._contents: list[OptionListContent] = [
            self._make_content(item) for item in content
        ]
        """A list of the content of the option list.

        This is *every* item that makes up the content of the option list;
        this includes both the options *and* the separators (and any other
        decoration we could end up adding -- although I don't anticipate
        anything else at the moment; but padding around separators could be
        a thing, perhaps).
        """

        self._options: list[Option] = [
            content for content in self._contents if isinstance(content, Option)
        ]
        """A list of the options within the option list.

        This is a list of references to just the options alone, ignoring the
        separators and potentially any other line-oriented option list
        content that isn't an option.
        """

        self._option_ids: dict[str, int] = {
            option.id: index for index, option in enumerate(self._options) if option.id
        }
        """A dictionary of option IDs and the option indexes they relate to."""

        self._content_render_cache: LRUCache[tuple[int, Style, int], list[Strip]] = (
            LRUCache(256)
        )

        self._lines: list[tuple[int, int]] | None = None

        self._mouse_hovering_over: int | None = None
        """Used to track what the mouse is hovering over."""

        if tooltip is not None:
            self.tooltip = tooltip

    def _populate(self) -> None:
        if self._lines is not None:
            return
        self._lines = []
        style = Style()
        width = self.size.width
        for index, content in enumerate(self._contents):
            if isinstance(content, Option):
                height = len(self._render_option_content(index, content, style, width))
                self._lines.extend((index, y) for y in range(height))
            else:
                self._lines.append((-1, 0))

        self.virtual_size = Size(width, len(self._lines))

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Get maximum width of options."""
        console = self.app.console
        options = console.options
        return max(
            Measurement.get(console, options, option.prompt).maximum
            for option in self._options
        )

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self._mouse_hovering_over = event.style.meta.get("option")

    def _make_content(self, content: NewOptionListContent) -> OptionListContent:
        """Convert a single item of content for the list into a content type.

        Args:
            content: The content to turn into a full option list type.

        Returns:
            The content, usable in the option list.
        """
        if isinstance(content, (Option, Separator)):
            return content
        if content is None:
            return Separator()
        return Option(content)

    def _render_option_content(
        self, index: int, renderable: RenderableType, style: Style, width: int
    ) -> list[Strip]:
        cache_key = (index, style, width)
        if (strips := self._content_render_cache.get(cache_key, None)) is not None:
            return strips
        console = self.app.console
        options = console.options
        lines = self.app.console.render_lines(renderable, options, style=style)
        strips = [Strip(line, width) for line in lines]
        self._content_render_cache[cache_key] = strips
        return strips

    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        line_number = scroll_y + y

        option_index, y_offset = self._lines[line_number]

        mouse_over = self._mouse_hovering_over

        component_classes = []

        # if option_index == -1:
        #     component_classes.append("option-list--separator")
        # else:
        #     option = self._options[option_index]
        #     if option.disabled:
        #         component_classes.append("option-list--option-disabled")
        #     else:
        #         if option_index == self._mouse_hovering_over:
        #             component_classes.append("option-list--option-hover-highlighted")

        # if mouse_over is not None:
        #     component_classes.append("option-list--option-hover")

        renderable = Rule() if option_index == -1 else self._lines[option_index]

        strips = self._render_option_content(option_index, renderable, self.size.width)
        strip = strips[y_offset]
        return strip
