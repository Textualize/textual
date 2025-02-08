from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Sequence

import rich.repr
from rich.segment import Segment
from rich.style import Style as RichStyle

from textual import _widget_navigation, events
from textual.binding import Binding, BindingType
from textual.cache import LRUCache
from textual.geometry import Region, Size
from textual.message import Message
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.style import Style
from textual.visual import Visual, VisualType, visualize


@rich.repr.auto
class Option:
    def __init__(
        self, prompt: VisualType, id: str | None = None, disabled: bool = False
    ) -> None:
        self._prompt = prompt
        self._visual: Visual | None = None
        self._id = id
        self._disabled = disabled
        self._divider = False

    @property
    def prompt(self) -> VisualType:
        return self._prompt

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def disabled(self) -> bool:
        return self._disabled

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._prompt
        yield "id", self._id, None
        yield "disabled", self.disabled, False
        yield "_divider", self._divider, False


@dataclass
class _LineCache:
    """Cached line information."""

    lines: list[tuple[int, int]] = field(default_factory=list)
    heights: dict[int, int] = field(default_factory=dict)
    index_to_line: dict[int, int] = field(default_factory=dict)

    def clear(self) -> None:
        self.lines.clear()
        self.heights.clear()
        self.index_to_line.clear()


class OptionList(ScrollView, can_focus=True):
    ALLOW_SELECT = False
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
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
    | `option-list--option` | Target options that are not disabled, highlighted or have the mouse over them. |
    | `option-list--option-disabled` | Target disabled options. |
    | `option-list--option-highlighted` | Target the highlighted option. |
    | `option-list--option-hover` | Target an option that has the mouse over it. |
    | `option-list--separator` | Target the separators. |
    """

    highlighted: reactive[int | None] = reactive(None)
    """The index of the currently-highlighted option, or `None` if no option is highlighted."""

    hover_option_index: reactive[int | None] = reactive(None)
    """The index of the option under the mouse or `None`."""

    class OptionMessage(Message):
        """Base class for all option messages."""

        def __init__(self, option_list: OptionList, option: Option, index: int) -> None:
            """Initialise the option message.

            Args:
                option_list: The option list that owns the option.
                index: The index of the option that the message relates to.
            """
            super().__init__()
            self.option_list: OptionList = option_list
            """The option list that sent the message."""
            self.option: Option = option
            """The highlighted option."""
            self.option_id: str | None = option.id
            """The ID of the option that the message relates to."""
            self.option_index: int = index
            """The index of the option that the message relates to."""

        @property
        def control(self) -> OptionList:
            """The option list that sent the message.

            This is an alias for [`OptionMessage.option_list`][textual.widgets.OptionList.OptionMessage.option_list]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.option_list

        def __rich_repr__(self) -> rich.repr.Result:
            try:
                yield "option_list", self.option_list
                yield "option", self.option
                yield "option_id", self.option_id
                yield "option_index", self.option_index
            except AttributeError:
                return

    class OptionHighlighted(OptionMessage):
        """Message sent when an option is highlighted.

        Can be handled using `on_option_list_option_highlighted` in a subclass of
        `OptionList` or in a parent node in the DOM.
        """

    class OptionSelected(OptionMessage):
        """Message sent when an option is selected.

        Can be handled using `on_option_list_option_selected` in a subclass of
        `OptionList` or in a parent node in the DOM.
        """

    def __init__(
        self,
        *content: Option | VisualType | None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        wrap: bool = True,
        markup: bool = True,
        tooltip: VisualType | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._wrap = wrap
        self._markup = markup
        self._options: list[Option] = []
        options = self._options
        add_option = self._options.append
        for prompt in content:
            if isinstance(prompt, Option):
                add_option(prompt)
            elif prompt is None:
                if options:
                    options[-1]._divider = True
            else:
                add_option(Option(prompt))

        self._visuals: dict[int, Visual] = {}
        self._option_render_cache: LRUCache[tuple[Style, int], list[Strip]] = LRUCache(
            maxsize=1024
        )
        # self._lines: list[tuple[int, int]] = []
        # """One entry per line, (OPTION_INDEX, LINE_OFFSET)"""
        # self._heights: dict[int, int] = {}
        # """Maps option index on to it's height."""
        # self._index_to_line: dict[int, int] = {}
        # """Maps option index on to y offset."""

        self._line_cache = _LineCache()

        if tooltip is not None:
            self.tooltip = tooltip

    @property
    def options(self) -> Sequence[Option]:
        """Sequence of options in the OptionList.

        !!! note "This is read-only"

        """
        return self._options

    @property
    def _lines(self) -> Sequence[tuple[int, int]]:
        """A sequence of pairs of ints for each line, used internally.

        The first int is the index of the option, and second is the line offset.

        !!! note "This is read-only"

        Returns:
            A sequence of tuples.
        """
        self._update_lines()
        return self._line_cache.lines

    @property
    def _heights(self) -> dict[int, int]:
        self._update_lines()
        return self._line_cache.heights

    @property
    def _index_to_line(self) -> dict[int, int]:
        self._update_lines()
        return self._line_cache.index_to_line

    def _clear_caches(self) -> None:
        self._option_render_cache.clear()
        self._line_cache.clear()

    def _on_resize(self):
        self._clear_caches()
        self.refresh()

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        """React to the mouse moving.

        Args:
            event: The mouse movement event.
        """
        self.hover_option_index = event.style.meta.get("option")

    def _get_option_visual(self, index: int) -> Visual:
        visual = self._visuals.get(index, None)
        if visual is None:
            option = self.options[index]
            visual = visualize(self, option.prompt, markup=self._markup)
            self._visuals[index] = visual
        return visual

    def _get_option_render(self, style: Style, index: int) -> list[Strip]:
        cache_key = (style, index)
        if (strips := self._option_render_cache.get(cache_key)) is None:
            visual = self._get_option_visual(index)
            width = self.content_region.width
            strips = visual.to_strips(self, visual, width, None, style)
            strips = [
                strip.adjust_cell_length(width, style.rich_style).apply_style(
                    RichStyle.from_meta({"option": index})
                )
                for strip in strips
            ]
            option = self.options[index]
            if option._divider:
                style = self.get_visual_style("option-list--separator")
                rule_segments = [Segment("─" * width, style.rich_style)]
                strips.append(Strip(rule_segments, width))

            self._option_render_cache[cache_key] = strips
        return strips

    def _update_lines(self) -> None:
        line_cache = self._line_cache
        lines = line_cache.lines
        last_index = lines[-1][0] if lines else 0

        if last_index < len(self.options) - 1:
            style = self.get_visual_style("option-list--option")

            for index in range(last_index, len(self.options)):
                line_cache.index_to_line[index] = len(line_cache.lines)
                line_count = len(self._get_option_render(style, index))
                line_cache.heights[index] = line_count
                line_cache.lines.extend(
                    [(index, line_no) for line_no in range(0, line_count)]
                )

        self.virtual_size = Size(self.content_region.width, len(lines))

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Get maximum width of options."""
        container_width = container.width
        get_option_visual = self._get_option_visual
        padding = self.get_component_styles("option-list--option").padding
        width = (
            max(
                get_option_visual(index).get_optimal_width({}, container_width)
                for index in range(len(self.options))
            )
            + padding.width
        )
        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        null_style = Style.null()
        height = sum(
            len(
                visualize(self, option.prompt, markup=False).render_strips(
                    {}, container.width, None, null_style
                )
            )
            + option._divider
            for option in self.options
        )
        if self.options and self.options[-1]._divider:
            # Last divider should add a line
            height -= 1
        return height

    def _get_line(self, style: Style, y: int) -> Strip:
        index, line_offset = self._lines[y]
        strips = self._get_option_render(style, index)
        return strips[line_offset]

    def render_line(self, y: int) -> Strip:

        _scroll_x, scroll_y = self.scroll_offset
        line_number = scroll_y + y
        try:
            option_index, line_offset = self._lines[line_number]
        except IndexError:
            return Strip.blank(self.content_region.width)
        option = self.options[option_index]

        mouse_over = self.hover_option_index == option_index
        if option.disabled:
            component_class = "option-list--option-disabled"
        elif self.highlighted == option_index:
            component_class = "option-list--option-highlighted"
        elif mouse_over:
            component_class = "option-list--option-hover"
        else:
            component_class = "option-list--option"

        style = self.get_visual_style(component_class)
        strips = self._get_option_render(style, option_index)
        strip = strips[line_offset]

        return strip

    def validate_highlighted(self, highlighted: int | None) -> int | None:
        """Validate the `highlighted` property value on access."""
        if highlighted is None or not self.options:
            return None
        elif highlighted < 0:
            return 0
        elif highlighted >= len(self.options):
            return len(self.options) - 1
        return highlighted

    def watch_highlighted(self, highlighted: int | None) -> None:
        """React to the highlighted option having changed."""
        if highlighted is None:
            return

        if not self._options[highlighted].disabled:
            self.scroll_to_highlight()

        option: Option
        if highlighted is None:
            option = None
        else:
            option = self.options[highlighted]
        self.post_message(self.OptionHighlighted(self, option, highlighted))

    def scroll_to_highlight(self, top: bool = False) -> None:
        highlighted = self.highlighted
        if highlighted is None or not self.is_mounted:
            return

        y = self._index_to_line[highlighted]
        option = self.options[highlighted]
        height = self._heights[highlighted] - option._divider

        self.scroll_to_region(
            Region(0, y, self.scrollable_content_region.width, height),
            force=True,
            animate=False,
            top=top,
            immediate=True,
        )

    def action_cursor_up(self) -> None:
        """Move the highlight up to the previous enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self.options,
            anchor=self.highlighted,
            direction=-1,
        )

    def action_cursor_down(self) -> None:
        """Move the highlight down to the next enabled option."""
        self.highlighted = _widget_navigation.find_next_enabled(
            self.options,
            anchor=self.highlighted,
            direction=1,
        )

    def action_first(self) -> None:
        """Move the highlight to the first enabled option."""
        self.highlighted = _widget_navigation.find_first_enabled(self.options)

    def action_last(self) -> None:
        """Move the highlight to the last enabled option."""
        self.highlighted = _widget_navigation.find_last_enabled(self.options)

    def _move_page(self, direction: _widget_navigation.Direction) -> None:

        height = self.content_region.height

        option_index = self.highlighted or 0

        y = self._index_to_line[option_index] + direction * height
        option_index = self._lines[y][0]

        target_option = _widget_navigation.find_next_enabled_no_wrap(
            candidates=self._options,
            anchor=option_index,
            direction=direction,
            with_anchor=True,
        )
        if target_option is not None:
            self.highlighted = target_option


if __name__ == "__main__":
    from textual.app import App, ComposeResult

    TEXT = """I must not fear.
Fear is the [u]mind-killer[/u].
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""

    class OLApp(App):

        def compose(self) -> ComposeResult:
            yield OptionList(
                *(["Hello", "World!", None, TEXT, None, "Foo", "Bar", "Baz", None] * 10)
            )

    app = OLApp()
    app.run()
